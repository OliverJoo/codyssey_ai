import unittest
import tempfile
import shutil
import zipfile
from pathlib import Path
from budget_app.bonus import (
    AtomicTransactionRepository,
    TableFormatter,
    BonusBudgetService,
    RecurringTransaction,
)
from budget_app.models import Transaction, ValidationError


class TestBonus(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data"
        self.backup_dir = Path(self.test_dir) / "backups"
        self.service = BonusBudgetService(data_dir=self.data_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_atomic_transaction_repository(self):
        repo = AtomicTransactionRepository(data_dir=self.data_dir)
        tx1 = Transaction(
            id="TX-000001",
            type="expense",
            date="2024-01-10",
            amount=10000,
            category="food",
            memo="점심",
        )
        repo.save(tx1)

        # Atomic update
        tx1.amount = 15000
        self.assertTrue(repo.update(tx1))
        self.assertEqual(repo.get_by_id("TX-000001").amount, 15000)

        # Atomic delete
        self.assertTrue(repo.delete("TX-000001"))
        self.assertIsNone(repo.get_by_id("TX-000001"))

    def test_table_formatter_alignment(self):
        formatter = TableFormatter()
        headers = ["ID", "날짜", "타입", "카테고리", "금액", "메모"]
        rows = [
            ["TX-000001", "2024-01-15", "expense", "food", 15000, "맛있는 점심"],
            ["TX-000002", "2024-01-20", "income", "salary", 3000000, "월급"],
        ]
        table = formatter.format_table(headers, rows)
        self.assertIn("TX-000001", table)
        self.assertIn("맛있는 점심", table)
        self.assertIn("3000000", table)

    def test_backup_functionality(self):
        # Create some data
        self.service.add_transaction(
            date="2024-01-10", type_="expense", category="food", amount=15000
        )
        self.service.set_budget(month="2024-01", amount=500000)

        backup_file = self.service.create_backup(backup_dir=self.backup_dir)
        self.assertTrue(backup_file.exists())
        self.assertTrue(backup_file.name.startswith("backup_"))
        self.assertTrue(backup_file.name.endswith(".zip"))

        # Verify zip contents
        with zipfile.ZipFile(backup_file, "r") as zf:
            namelist = zf.namelist()
            self.assertTrue(any("transactions.jsonl" in n for n in namelist))
            self.assertTrue(any("budgets.jsonl" in n for n in namelist))
            self.assertTrue(any("categories.jsonl" in n for n in namelist))

    def test_recurring_transactions(self):
        # Add recurring rule
        rule = self.service.add_recurring(
            day=25,
            type_="expense",
            category="living",
            amount=500000,
            memo="월세",
            tags=["regular", "rent"],
        )
        self.assertEqual(rule.day, 25)
        self.assertEqual(rule.amount, 500000)

        # List recurring
        rules = self.service.list_recurring()
        self.assertEqual(len(rules), 1)

        # Generate recurring transactions for 2024-01
        generated = self.service.generate_recurring(month="2024-01")
        self.assertEqual(len(generated), 1)
        self.assertEqual(generated[0].date, "2024-01-25")
        self.assertEqual(generated[0].amount, 500000)
        self.assertEqual(generated[0].category, "living")

        # Generating again for the same month should not duplicate
        generated_again = self.service.generate_recurring(month="2024-01")
        self.assertEqual(len(generated_again), 0)


if __name__ == "__main__":
    unittest.main()
