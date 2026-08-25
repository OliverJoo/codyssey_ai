import unittest
import tempfile
import shutil
from pathlib import Path
from budget_app.models import Transaction, Budget
from budget_app.storage import TransactionRepository, CategoryStore, BudgetStore


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_category_store_initialization(self):
        store = CategoryStore(data_dir=self.data_dir)
        categories = store.get_all()
        self.assertIn("food", categories)
        self.assertIn("transport", categories)
        self.assertTrue(store.exists("food"))

        # Add category
        self.assertTrue(store.add("travel"))
        self.assertIn("travel", store.get_all())
        self.assertFalse(store.add("travel"))  # Duplicate

        # Remove category
        self.assertTrue(store.remove("travel"))
        self.assertNotIn("travel", store.get_all())
        self.assertFalse(store.remove("nonexistent"))

    def test_budget_store(self):
        store = BudgetStore(data_dir=self.data_dir)
        self.assertIsNone(store.get_budget("2024-01"))

        store.set_budget(Budget(month="2024-01", amount=500000))
        b = store.get_budget("2024-01")
        self.assertIsNotNone(b)
        self.assertEqual(b.amount, 500000)

        # Update budget
        store.set_budget(Budget(month="2024-01", amount=600000))
        self.assertEqual(store.get_budget("2024-01").amount, 600000)

    def test_transaction_repository_crud_and_generator(self):
        repo = TransactionRepository(data_dir=self.data_dir)

        # Generate id
        next_id = repo.generate_next_id()
        self.assertEqual(next_id, "TX-000001")

        tx1 = Transaction(
            id=next_id,
            type="expense",
            date="2024-01-10",
            amount=10000,
            category="food",
            memo="점심",
            tags=["lunch"],
        )
        repo.save(tx1)

        # Stream verification
        items = list(repo.stream_all())
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, "TX-000001")

        # Next id
        next_id2 = repo.generate_next_id()
        self.assertEqual(next_id2, "TX-000002")

        tx2 = Transaction(
            id=next_id2,
            type="income",
            date="2024-01-12",
            amount=3000000,
            category="salary",
        )
        repo.save(tx2)

        self.assertEqual(len(list(repo.stream_all())), 2)
        self.assertEqual(repo.get_by_id("TX-000002").amount, 3000000)
        self.assertIsNone(repo.get_by_id("TX-999999"))

        # Update
        tx1_updated = Transaction(
            id="TX-000001",
            type="expense",
            date="2024-01-10",
            amount=12000,
            category="food",
            memo="점심(특식)",
            tags=["lunch", "special"],
        )
        self.assertTrue(repo.update(tx1_updated))
        self.assertEqual(repo.get_by_id("TX-000001").amount, 12000)
        self.assertEqual(repo.get_by_id("TX-000001").memo, "점심(특식)")

        # Delete
        self.assertTrue(repo.delete("TX-000001"))
        self.assertIsNone(repo.get_by_id("TX-000001"))
        self.assertFalse(repo.delete("TX-000001"))
        self.assertEqual(len(list(repo.stream_all())), 1)


if __name__ == "__main__":
    unittest.main()
