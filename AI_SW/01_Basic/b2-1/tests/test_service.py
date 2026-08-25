import unittest
import tempfile
import shutil
from pathlib import Path
from budget_app.models import ValidationError
from budget_app.storage import TransactionRepository, CategoryStore, BudgetStore
from budget_app.service import BudgetService


class TestBudgetService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data"
        self.service = BudgetService(data_dir=self.data_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_transaction_success(self):
        tx = self.service.add_transaction(
            date="2024-01-15",
            type_="expense",
            category="food",
            amount=15000,
            memo="점심",
            tags=["meal"],
        )
        self.assertEqual(tx.id, "TX-000001")
        self.assertEqual(tx.amount, 15000)
        self.assertEqual(tx.category, "food")

    def test_add_transaction_invalid_category(self):
        with self.assertRaises(ValidationError) as ctx:
            self.service.add_transaction(
                date="2024-01-15",
                type_="expense",
                category="unknown_cat",
                amount=15000,
            )
        self.assertIn("등록되지 않은 카테고리", str(ctx.exception))

    def test_list_and_search_transactions(self):
        self.service.add_transaction(
            date="2024-01-10",
            type_="expense",
            category="food",
            amount=10000,
            memo="아침",
            tags=["morning"],
        )
        self.service.add_transaction(
            date="2024-01-15",
            type_="income",
            category="salary",
            amount=3000000,
            memo="월급",
            tags=["work"],
        )
        self.service.add_transaction(
            date="2024-01-20",
            type_="expense",
            category="transport",
            amount=20000,
            memo="지하철",
            tags=["subway"],
        )

        # List (최신순: 2024-01-20 -> 2024-01-15 -> 2024-01-10)
        txs = self.service.list_transactions(limit=2)
        self.assertEqual(len(txs), 2)
        self.assertEqual(txs[0].date, "2024-01-20")

        # Search by date range
        res = self.service.search_transactions(from_date="2024-01-11", to_date="2024-01-18")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].id, "TX-000002")

        # Search by category and type
        res = self.service.search_transactions(category="food", type_="expense")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].memo, "아침")

        # Search by query
        res = self.service.search_transactions(query="월급")
        self.assertEqual(len(res), 1)

        # Search by tag
        res = self.service.search_transactions(tag="subway")
        self.assertEqual(len(res), 1)

    def test_monthly_summary_and_budget(self):
        # Empty summary
        empty_summary = self.service.get_monthly_summary(month="2024-02")
        self.assertFalse(empty_summary["has_data"])

        # Add income and expenses
        self.service.add_transaction(
            date="2024-01-05", type_="income", category="salary", amount=3000000
        )
        self.service.add_transaction(
            date="2024-01-10", type_="expense", category="living", amount=150000, memo="월세"
        )
        self.service.add_transaction(
            date="2024-01-12", type_="expense", category="food", amount=45000
        )
        self.service.add_transaction(
            date="2024-01-15", type_="expense", category="transport", amount=20000
        )

        # Set budget
        self.service.set_budget(month="2024-01", amount=500000)

        summary = self.service.get_monthly_summary(month="2024-01", top_n=3)
        self.assertTrue(summary["has_data"])
        self.assertEqual(summary["total_income"], 3000000)
        self.assertEqual(summary["total_expense"], 215000)
        self.assertEqual(summary["balance"], 2785000)
        self.assertEqual(summary["budget_amount"], 500000)
        self.assertEqual(summary["usage_rate"], 43.0)
        self.assertFalse(summary["is_over_budget"])

        top_cats = summary["top_expenses"]
        self.assertEqual(len(top_cats), 3)
        self.assertEqual(top_cats[0], ("living", 150000))
        self.assertEqual(top_cats[1], ("food", 45000))
        self.assertEqual(top_cats[2], ("transport", 20000))

    def test_category_management(self):
        self.assertTrue(self.service.category_add("hobby"))
        self.assertIn("hobby", self.service.category_list())

        self.service.add_transaction(
            date="2024-01-10", type_="expense", category="hobby", amount=50000
        )

        # Removal without replacement when in use should fail
        with self.assertRaises(ValidationError):
            self.service.category_remove("hobby")

        # Removal with replacement
        self.service.category_remove("hobby", replacement="living")
        self.assertNotIn("hobby", self.service.category_list())
        tx = self.service.list_transactions()[0]
        self.assertEqual(tx.category, "living")

    def test_update_and_delete(self):
        tx = self.service.add_transaction(
            date="2024-01-10", type_="expense", category="food", amount=10000
        )
        updated = self.service.update_transaction(
            tx_id=tx.id, amount=12000, memo="맛있는 점심"
        )
        self.assertEqual(updated.amount, 12000)
        self.assertEqual(updated.memo, "맛있는 점심")

        # Non-existing update
        with self.assertRaises(ValidationError):
            self.service.update_transaction(tx_id="TX-999999", amount=5000)

        # Delete
        self.assertTrue(self.service.delete_transaction(tx.id))
        with self.assertRaises(ValidationError):
            self.service.delete_transaction(tx.id)

    def test_export_and_import_csv(self):
        self.service.add_transaction(
            date="2024-01-10",
            type_="expense",
            category="food",
            amount=10000,
            memo="점심",
            tags=["lunch"],
        )
        self.service.add_transaction(
            date="2024-01-15",
            type_="income",
            category="salary",
            amount=3000000,
            memo="월급",
            tags=["work", "bonus"],
        )

        export_path = Path(self.test_dir) / "export.csv"
        count = self.service.export_to_csv(export_path, month="2024-01")
        self.assertEqual(count, 2)
        self.assertTrue(export_path.exists())

        # Test import into a new service instance
        new_data_dir = Path(self.test_dir) / "data_new"
        new_service = BudgetService(data_dir=new_data_dir)
        imported, skipped = new_service.import_from_csv(export_path)
        self.assertEqual(imported, 2)
        self.assertEqual(skipped, 0)
        self.assertEqual(len(new_service.list_transactions()), 2)


if __name__ == "__main__":
    unittest.main()
