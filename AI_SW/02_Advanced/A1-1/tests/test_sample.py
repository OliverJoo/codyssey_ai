import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.make_sample_data import make_sample_data
from src.pipeline import DataAnalyzer


class SampleTest(unittest.TestCase):
    def test_public_retail_preserves_original_amount_and_unique_orders(self):
        root = Path(__file__).resolve().parents[1]
        source = pd.read_csv(root / 'data/retail_source.csv')
        analyzer = DataAnalyzer(root / 'data/orders.csv', root / 'data/images.npy')
        raw = analyzer.load_data().copy()
        self.assertGreaterEqual(len(raw), 1000)
        self.assertGreaterEqual(len(raw.columns), 8)
        self.assertTrue(raw.order_id.duplicated().any())
        np.testing.assert_allclose(raw.amount, source.UnitPrice * source.Quantity)
        analyzer.handle_missing_values(group_col='product_id')
        analyzer.engineer_features()
        analyzer.handle_outliers('price')
        rfm = analyzer.segment_customers(analyzer.calculate_rfm())
        self.assertEqual(rfm.frequency.sum(), raw.order_id.nunique())
        self.assertAlmostEqual(rfm.monetary.sum(), raw.amount.sum())
        self.assertEqual(rfm.segment.nunique(), 4)
        self.assertFalse(analyzer.df.price.isna().any())

    def test_reproducible_multimodal_sample_and_complete_analysis(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root = Path(folder)
            make_sample_data(root)
            first = pd.read_csv(root / 'orders.csv')
            images = np.load(root / 'images.npy')
            make_sample_data(root)
            pd.testing.assert_frame_equal(first, pd.read_csv(root / 'orders.csv'))
            np.testing.assert_array_equal(images, np.load(root / 'images.npy'))
            self.assertGreaterEqual(len(first), 1000)
            self.assertGreaterEqual(len(first.columns), 8)
            self.assertTrue(first.order_id.is_unique)
            self.assertTrue((pd.to_datetime(first.signup_date) <= pd.to_datetime(first.order_date)).all())
            self.assertEqual(first.groupby('customer_id').signup_date.nunique().max(), 1)
            analyzer = DataAnalyzer(root / 'orders.csv', root / 'images.npy')
            analyzer.load_data()
            self.assertGreater(analyzer.missing_summary()['price'], 0)
            analyzer.handle_missing_values()
            self.assertFalse(analyzer.df.price.isna().any())
            analyzer.engineer_features()
            self.assertGreater(len(analyzer.detect_outliers('price')), 0)
            analyzer.handle_outliers('price')
            rfm = analyzer.segment_customers(analyzer.calculate_rfm())
            self.assertEqual(set(rfm.segment), {'VIP', 'Loyal', 'New', 'Churned'})
            self.assertAlmostEqual(rfm.monetary.sum(), first.amount.sum())
            self.assertEqual(rfm.frequency.sum(), len(first))


if __name__ == '__main__':
    unittest.main()
