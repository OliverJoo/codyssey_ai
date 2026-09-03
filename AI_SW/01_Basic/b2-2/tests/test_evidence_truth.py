"""핵심 증거 판정이 다시 과장되지 않도록 검사한다."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class EvidenceTruthTest(unittest.TestCase):
    def test_submission_keeps_verified_and_unverified_claims_separate(self) -> None:
        submission = (ROOT / "SUBMISSION.md").read_text(encoding="utf-8")
        self.assertIn("5/19", submission)
        self.assertIn("미확인/미충족", submission)
        self.assertIn("자동 병합", submission)
        self.assertNotIn("| 충돌 2회, 비자명 1회 | 충족 |", submission)

    def test_answers_label_scenarios_and_bonus_evidence(self) -> None:
        answers = (ROOT / "README_answer.md").read_text(encoding="utf-8")
        self.assertIn("가상 시나리오 답변", answers)
        self.assertIn("보너스 수행 증빙은 확인되지 않는다", answers)
        self.assertIn("examples/team_utils_demo.py", answers)

    def test_conflict_replay_result_is_documented(self) -> None:
        conflict = (ROOT / "docs/conflict-resolution.md").read_text(encoding="utf-8")
        self.assertIn("Automatic merge went well", conflict)
        self.assertIn("R100", conflict)


if __name__ == "__main__":
    unittest.main()
