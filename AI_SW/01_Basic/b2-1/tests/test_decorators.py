import unittest
import io
import sys
from budget_app.decorators import handle_cli_errors, measure_execution_time
from budget_app.models import ValidationError


class TestDecorators(unittest.TestCase):
    def test_handle_cli_errors_success(self):
        @handle_cli_errors
        def sample_func(x):
            return x * 2

        self.assertEqual(sample_func(5), 10)

    def test_handle_cli_errors_validation_error(self):
        @handle_cli_errors
        def sample_fail():
            raise ValidationError("잘못된 값입니다.", hint="1 이상의 숫자를 입력하세요.")

        captured_out = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_out
        try:
            with self.assertRaises(SystemExit) as ctx:
                sample_fail()
            self.assertEqual(ctx.exception.code, 1)
            output = captured_out.getvalue()
            self.assertIn("[오류] 잘못된 값입니다.", output)
            self.assertIn("[힌트] 1 이상의 숫자를 입력하세요.", output)
        finally:
            sys.stdout = original_stdout

    def test_measure_execution_time(self):
        logs = []

        @measure_execution_time(callback=lambda msg: logs.append(msg))
        def sample_calc():
            return sum(range(100))

        result = sample_calc()
        self.assertEqual(result, 4950)
        self.assertEqual(len(logs), 1)
        self.assertIn("sample_calc", logs[0])


if __name__ == "__main__":
    unittest.main()
