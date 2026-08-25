import unittest
from budget_app.models import (
    Transaction,
    Category,
    Budget,
    ValidationError,
    validate_date,
    validate_month,
    validate_amount,
    validate_type,
)


class TestModels(unittest.TestCase):
    def test_valid_transaction_creation(self):
        tx = Transaction(
            id="TX-000001",
            type="expense",
            date="2024-01-15",
            amount=15000,
            category="food",
            memo="점심",
            tags=["meal", "lunch"],
        )
        self.assertEqual(tx.id, "TX-000001")
        self.assertEqual(tx.amount, 15000)
        self.assertEqual(tx.tags, ["meal", "lunch"])

    def test_transaction_dict_serialization(self):
        tx = Transaction(
            id="TX-000002",
            type="income",
            date="2024-01-10",
            amount=3000000,
            category="salary",
            memo="월급",
            tags=["regular"],
        )
        d = tx.to_dict()
        self.assertEqual(d["id"], "TX-000002")
        self.assertEqual(d["type"], "income")
        self.assertEqual(d["amount"], 3000000)

        restored = Transaction.from_dict(d)
        self.assertEqual(restored.id, tx.id)
        self.assertEqual(restored.amount, tx.amount)
        self.assertEqual(restored.tags, tx.tags)

    def test_validation_date_format(self):
        self.assertEqual(validate_date("2024-01-15"), "2024-01-15")
        with self.assertRaises(ValidationError) as ctx:
            validate_date("2024-13-40")
        self.assertIn("날짜 형식", str(ctx.exception))
        self.assertTrue(bool(ctx.exception.hint))

        with self.assertRaises(ValidationError):
            validate_date("invalid-date")

    def test_validation_month_format(self):
        self.assertEqual(validate_month("2024-01"), "2024-01")
        with self.assertRaises(ValidationError):
            validate_month("2024-13")
        with self.assertRaises(ValidationError):
            validate_month("202401")

    def test_validation_amount(self):
        self.assertEqual(validate_amount(10000), 10000)
        self.assertEqual(validate_amount("15000"), 15000)
        with self.assertRaises(ValidationError):
            validate_amount(0)
        with self.assertRaises(ValidationError):
            validate_amount(-500)
        with self.assertRaises(ValidationError):
            validate_amount("abc")

    def test_validation_type(self):
        self.assertEqual(validate_type("income"), "income")
        self.assertEqual(validate_type("expense"), "expense")
        self.assertEqual(validate_type("INCOME"), "income")
        with self.assertRaises(ValidationError):
            validate_type("transfer")

    def test_category_and_budget_validation(self):
        cat = Category(name="food")
        cat.validate()
        with self.assertRaises(ValidationError):
            Category(name="").validate()

        b = Budget(month="2024-01", amount=500000)
        b.validate()
        with self.assertRaises(ValidationError):
            Budget(month="2024-99", amount=500000).validate()
        with self.assertRaises(ValidationError):
            Budget(month="2024-01", amount=-100).validate()


if __name__ == "__main__":
    unittest.main()
