"""제목 길이와 PR 필수 섹션 검증을 확인합니다."""

import json
import unittest

from src.ai_gitgen.validators import ValidationError, format_commit, format_pr


class ValidatorTest(unittest.TestCase):
    def test_commit_title_is_at_most_72_characters(self) -> None:
        result = format_commit(json.dumps({"title": "가" * 90, "body": []}))
        self.assertEqual(len(result.title), 72)

    def test_pr_title_is_at_most_80_characters(self) -> None:
        result = format_pr(
            json.dumps(
                {"title": "P" * 100, "why": ["a"], "what": ["b"], "how_to_test": ["c"]}
            )
        )
        self.assertEqual(len(result.title), 80)

    def test_pr_requires_each_section(self) -> None:
        with self.assertRaises(ValidationError):
            format_pr(json.dumps({"title": "test", "why": [], "what": ["b"], "how_to_test": ["c"]}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
