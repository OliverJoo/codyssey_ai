import unittest
from unittest.mock import patch
import io
import tempfile
import shutil
from pathlib import Path
from budget_app.cli import main_cli


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = str(Path(self.test_dir) / "data")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_cli(self, args: list[str]) -> tuple[int, str]:
        captured = io.StringIO()
        with patch("sys.stdout", captured), patch("sys.stderr", captured):
            exit_code = 0
            try:
                main_cli(["--data-dir", self.data_dir] + args)
            except SystemExit as e:
                exit_code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return exit_code, captured.getvalue()

    def test_add_interactive_and_list(self):
        # Interactive add
        inputs = ["2024-01-15", "expense", "food", "15000", "점심", "meal"]
        with patch("builtins.input", side_effect=inputs):
            code, out = self.run_cli(["add"])
            self.assertEqual(code, 0)
            self.assertIn("[저장 완료] id=TX-000001", out)

        # List
        code, out = self.run_cli(["list", "--limit", "5"])
        self.assertEqual(code, 0)
        self.assertIn("TX-000001", out)
        self.assertIn("15000", out)
        self.assertIn("food", out)

    def test_budget_and_summary(self):
        # Add transactions
        inputs1 = ["2024-01-10", "income", "salary", "3000000", "월급", ""]
        with patch("builtins.input", side_effect=inputs1):
            self.run_cli(["add"])

        inputs2 = ["2024-01-15", "expense", "food", "20000", "점심", ""]
        with patch("builtins.input", side_effect=inputs2):
            self.run_cli(["add"])

        # Set budget
        code, out = self.run_cli(["budget", "set", "--month", "2024-01", "--amount", "500000"])
        self.assertEqual(code, 0)
        self.assertIn("[저장 완료]", out)

        # Summary
        code, out = self.run_cli(["summary", "--month", "2024-01", "--top", "3"])
        self.assertEqual(code, 0)
        self.assertIn("총 수입: 3000000원", out)
        self.assertIn("총 지출: 20000원", out)
        self.assertIn("잔액: 2980000원", out)
        self.assertIn("사용률", out)

    def test_category_cli(self):
        # Add category
        with patch("builtins.input", return_value="hobby"):
            code, out = self.run_cli(["category", "add"])
            self.assertEqual(code, 0)
            self.assertIn("category=hobby", out)

        # List category
        code, out = self.run_cli(["category", "list"])
        self.assertEqual(code, 0)
        self.assertIn("hobby", out)

    def test_update_and_delete_cli(self):
        # Add tx
        inputs = ["2024-01-15", "expense", "food", "10000", "아침", ""]
        with patch("builtins.input", side_effect=inputs):
            self.run_cli(["add"])

        # Update
        code, out = self.run_cli(["update", "--id", "TX-000001", "--amount", "12000"])
        self.assertEqual(code, 0)
        self.assertIn("[수정 완료]", out)

        # Delete
        code, out = self.run_cli(["delete", "--id", "TX-000001"])
        self.assertEqual(code, 0)
        self.assertIn("[삭제 완료]", out)

        # Delete again (not found)
        code, out = self.run_cli(["delete", "--id", "TX-000001"])
        self.assertNotEqual(code, 0)
        self.assertIn("[오류]", out)


if __name__ == "__main__":
    unittest.main()
