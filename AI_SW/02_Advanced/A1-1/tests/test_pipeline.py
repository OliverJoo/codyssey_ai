"""손으로 계산한 작은 자료로 분석 결과를 검증한다."""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.pipeline import DataAnalyzer


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.frame = pd.DataFrame({
            'customer_id': ['a', 'a', 'b', 'c', 'd'],
            'order_date': ['2026-01-01', '2026-01-10', '2026-01-09',
                           '2025-01-01', '2026-01-08'],
            'signup_date': ['2025-01-01'] * 5,
            'amount': [10, 20, 15, 5, 25],
            'price': [10.0, np.nan, 30, np.nan, 50],
            'category': ['A', 'A', 'B', 'C', 'B'],
            'product_name': ['red bag', 'blue bag', 'cup', 'tea cup', 'hat'],
            'image_index': [1, 0, 1, 0, 1],
        })
        self.frame.to_csv(self.root / 'orders.csv', index=False)
        np.save(self.root / 'images.npy', np.array([[[0, 2], [4, 6]],
                                                  [[10, 10], [10, 10]]]))
        self.analyzer = DataAnalyzer(self.root / 'orders.csv', self.root / 'images.npy')
        self.analyzer.load_data()

    def test_load_dates_and_image_mapping(self):
        self.assertEqual(self.analyzer.df.shape, (5, 8))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.analyzer.df.order_date))
        self.assertEqual(self.analyzer.images.shape, (2, 2, 2))

    def test_group_mean_and_empty_group_global_fallback(self):
        before = self.analyzer.missing_summary()
        self.assertEqual(before['price'], 2)
        self.analyzer.handle_missing_values('price', 'category', 'mean')
        self.assertEqual(self.analyzer.df.loc[1, 'price'], 10)
        self.assertEqual(self.analyzer.df.loc[3, 'price'], 30)
        self.assertEqual(self.analyzer.missing_summary()['price'], 0)

    def test_group_median_and_invalid_strategy(self):
        self.analyzer.handle_missing_values('price', 'category', 'median')
        self.assertEqual(self.analyzer.df.loc[3, 'price'], 30)
        with self.assertRaises(ValueError):
            self.analyzer.handle_missing_values('price', 'category', 'magic')

    def test_image_mean_population_std_and_word_count(self):
        self.analyzer.engineer_features()
        np.testing.assert_allclose(self.analyzer.df.image_mean, [10, 3, 10, 3, 10])
        self.assertAlmostEqual(self.analyzer.df.loc[1, 'image_std'], np.sqrt(5))
        self.assertEqual(self.analyzer.df.product_word_count.tolist(), [2, 2, 1, 2, 1])

    def test_iqr_boundary_and_clipping_preserve_revenue(self):
        self.analyzer.df['price'] = [0, 1, 2, 3, 100]
        self.assertEqual(self.analyzer.detect_outliers('price').index.tolist(), [4])
        self.assertEqual(self.analyzer.iqr_bounds('price'), (-2, 6))
        self.assertEqual(len(self.analyzer.detect_outliers('price', threshold=100)), 0)
        before = self.analyzer.df.amount.copy()
        self.analyzer.handle_outliers('price')
        self.assertEqual(self.analyzer.df.price.tolist(), [0, 1, 2, 3, 6])
        pd.testing.assert_series_equal(before, self.analyzer.df.amount)

    def test_iqr_equal_boundary_is_not_outlier_and_zero_iqr(self):
        self.analyzer.df['price'] = [0, 1, 2, 3, 6]
        self.assertTrue(self.analyzer.detect_outliers('price').empty)
        self.analyzer.df['price'] = [2, 2, 2, 2, 9]
        self.assertEqual(self.analyzer.detect_outliers('price').index.tolist(), [4])

    def test_rfm_reference_date_totals_and_scores(self):
        rfm = self.analyzer.calculate_rfm()
        self.assertEqual(rfm.loc['a', 'recency'], 0)
        self.assertEqual(rfm.loc['a', 'frequency'], 2)
        self.assertEqual(rfm.loc['a', 'monetary'], 30)
        self.assertEqual(rfm.loc['b', 'recency'], 1)
        self.assertTrue(rfm[['r_score', 'f_score', 'm_score']].isin([1, 2, 3, 4]).all().all())
        self.assertEqual(rfm.loc['a', 'r_score'], 4)
        self.assertEqual(rfm.loc['c', 'r_score'], 1)
        later = self.analyzer.calculate_rfm(reference_date='2026-01-11')
        self.assertEqual(later.loc['a', 'recency'], 1)

    def test_rfm_ties_have_same_scores(self):
        self.analyzer.df['amount'] = 10
        rfm = self.analyzer.calculate_rfm()
        self.assertEqual(rfm.loc['b', 'f_score'], rfm.loc['c', 'f_score'])
        self.assertEqual(rfm.loc['b', 'm_score'], rfm.loc['c', 'm_score'])

    def test_rfm_counts_orders_not_product_lines(self):
        self.analyzer.df['order_id'] = ['O1', 'O1', 'O2', 'O3', 'O4']
        self.analyzer.df.loc[1, 'order_date'] = self.analyzer.df.loc[0, 'order_date']
        rfm = self.analyzer.calculate_rfm()
        self.assertEqual(rfm.loc['a', 'frequency'], 1)
        self.assertEqual(rfm.loc['a', 'monetary'], 30)

    def test_reference_before_latest_order_is_rejected(self):
        with self.assertRaises(ValueError):
            self.analyzer.calculate_rfm(reference_date='2026-01-01')

    def test_segmentation_priority_and_four_groups(self):
        rfm = pd.DataFrame({'recency': [1, 10, 3, 180, 15],
                            'frequency': [10, 4, 1, 1, 1],
                            'monetary': [900, 90, 10, 5, 20],
                            'f_score': [4, 3, 1, 1, 1],
                            'm_score': [4, 2, 1, 1, 1]})
        result = self.analyzer.segment_customers(rfm, recent_days=30, churn_days=90)
        self.assertEqual(result.segment.tolist(), ['VIP', 'Loyal', 'New', 'Churned', 'New'])
        changed = self.analyzer.segment_customers(rfm, recent_days=2, churn_days=90)
        self.assertEqual(changed.loc[2, 'segment'], 'Loyal')

    def test_summary_uses_sample_standard_deviation(self):
        result = self.analyzer.summary_statistics(['amount'])
        self.assertEqual(result.loc['amount', 'mean'], 15)
        self.assertEqual(result.loc['amount', 'median'], 15)
        self.assertAlmostEqual(result.loc['amount', 'std'], np.sqrt(62.5))
        self.assertEqual(result.loc['amount', 'q1'], 10)
        self.assertEqual(result.loc['amount', 'q3'], 20)


if __name__ == '__main__':
    unittest.main()
