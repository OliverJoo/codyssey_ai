"""실제 4인 팀 유틸리티의 정상·경계 사례를 검사한다."""

from pathlib import Path
import sys
import unittest


# src 모듈을 설치 없이 불러온다.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from count_utils import count_words
from list_utils import remove_duplicates
from math_utils import is_even
from string_utils import reverse_string


class TeamUtilsTest(unittest.TestCase):
    def test_dave17code_reverse_string(self) -> None:
        self.assertEqual(reverse_string("abc"), "cba")
        self.assertEqual(reverse_string(""), "")
        with self.assertRaises(TypeError):
            reverse_string(123)  # type: ignore[arg-type]

    def test_heeyoung35_count_words(self) -> None:
        self.assertEqual(count_words("  Hello   Git  "), 2)
        self.assertEqual(count_words(""), 0)

    def test_OliverJoo_remove_duplicates(self) -> None:
        result = remove_duplicates([1, 2, 2, 3, 3])
        self.assertEqual(set(result), {1, 2, 3})
        self.assertEqual(len(result), 3)

    def test_hyunn9799_is_even(self) -> None:
        self.assertTrue(is_even(0))
        self.assertTrue(is_even(-4))
        self.assertFalse(is_even(3))


if __name__ == "__main__":
    unittest.main()
