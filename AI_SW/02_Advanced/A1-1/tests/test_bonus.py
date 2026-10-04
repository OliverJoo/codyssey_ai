import unittest

import numpy as np
import pandas as pd

from src.bonus_pipeline import BonusDataAnalyzer
from src.pipeline import DataAnalyzer


class BonusTest(unittest.TestCase):
    def setUp(self):
        self.analyzer = BonusDataAnalyzer(None, None)

    def test_inherits_basic_pipeline(self):
        self.assertIsInstance(self.analyzer, DataAnalyzer)

    def test_numpy_edge_strength_without_unsigned_wraparound(self):
        self.analyzer.images = np.array([[[255, 0], [255, 0]],
                                        [[4, 4], [4, 4]]], dtype=np.uint8)
        self.analyzer.df = pd.DataFrame({'image_index': [0, 1, 0]})
        result = self.analyzer.add_edge_features()
        np.testing.assert_allclose(result.image_edge, [127.5, 0, 127.5])

    def test_signup_cohort_repeat_purchase_and_future_mask(self):
        self.analyzer.df = pd.DataFrame({
            'customer_id': ['a', 'a', 'b', 'c', 'c', 'd'],
            'signup_date': pd.to_datetime(['2026-01-01'] * 3 + ['2026-02-01'] * 3),
            'order_date': pd.to_datetime(['2026-01-02', '2026-02-03', '2026-02-02',
                                          '2026-02-02', '2026-02-04', '2026-03-01']),
        })
        retention = self.analyzer.cohort_retention()
        self.assertEqual(retention.loc['2026-01', 0], 0)
        self.assertEqual(retention.loc['2026-01', 1], 0.5)
        self.assertEqual(retention.loc['2026-02', 0], 0.5)
        self.assertEqual(retention.loc['2026-02', 1], 0)
        self.assertTrue(pd.isna(retention.loc['2026-02', 2]))

    def test_plotly_contains_all_customers_and_axis_titles(self):
        rfm = pd.DataFrame({'recency': [0, 10, 30, 100], 'frequency': [10, 4, 1, 1],
                            'monetary': [900, 100, 20, 10],
                            'segment': ['VIP', 'Loyal', 'New', 'Churned']},
                           index=pd.Index(['a', 'b', 'c', 'd'], name='customer_id'))
        figure = self.analyzer.plot_rfm(rfm)
        self.assertEqual(sum(len(trace.x) for trace in figure.data), 4)
        self.assertTrue(figure.layout.title.text)
        self.assertTrue(figure.layout.xaxis.title.text)
        self.assertTrue(figure.layout.yaxis.title.text)


if __name__ == '__main__':
    unittest.main()
