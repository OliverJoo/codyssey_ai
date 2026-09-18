"""PDF 기능 요구사항을 실제 CLI 수준에서 검사합니다."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from tests.mock_ai_server import MockAIHandler, start_server


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN = PROJECT_ROOT / "main.py"


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """테스트용 외부 명령을 실행합니다."""
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8")


class CLITest(unittest.TestCase):
    """임시 Git 저장소와 로컬 API로 주요 기능을 검증합니다."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="b6-2-test-")
        self.repo = Path(self.temp.name)
        for args in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "student@example.com"],
            ["git", "config", "user.name", "Student"],
        ):
            result = run(args, self.repo)
            self.assertEqual(result.returncode, 0, result.stderr)
        (self.repo / "app.py").write_text("print('before')\n", encoding="utf-8")
        run(["git", "add", "app.py"], self.repo)
        run(["git", "commit", "-qm", "initial"], self.repo)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _changed_repo(self) -> None:
        (self.repo / "app.py").write_text("print('after')\n", encoding="utf-8")

    def test_no_changes_skips_api(self) -> None:
        result = run([sys.executable, str(MAIN), "commit"], self.repo, os.environ.copy())
        self.assertEqual(result.returncode, 0)
        self.assertIn("변경 사항이 없습니다", result.stdout)
        self.assertIn("호출하지 않습니다", result.stdout)

    def test_missing_key_reports_cause(self) -> None:
        self._changed_repo()
        env = os.environ.copy()
        env.pop("AI_API_KEY", None)
        result = run([sys.executable, str(MAIN), "commit"], self.repo, env)
        self.assertEqual(result.returncode, 1)
        self.assertIn("AI_API_KEY 환경 변수가 없습니다", result.stderr)

    def test_commit_and_pr_with_real_http_path(self) -> None:
        self._changed_repo()
        MockAIHandler.requests.clear()
        server = start_server()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        env = os.environ.copy()
        env["AI_API_KEY"] = "test-key-for-local-server"
        env["AI_API_URL"] = f"http://127.0.0.1:{server.server_port}"
        try:
            commit = run(
                [sys.executable, str(MAIN), "commit", "--temperature", "0.4", "--max-tokens", "320"],
                self.repo,
                env,
            )
            pr = run([sys.executable, str(MAIN), "pr"], self.repo, env)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(commit.returncode, 0, commit.stderr)
        self.assertIn("=== COMMIT TITLE ===", commit.stdout)
        self.assertIn("API 호출 횟수: 1", commit.stdout)
        self.assertEqual(pr.returncode, 0, pr.stderr)
        for heading in ("## Why", "## What", "## How to Test"):
            self.assertIn(heading, pr.stdout)
        self.assertEqual(len(MockAIHandler.requests), 2)
        self.assertEqual(MockAIHandler.requests[0]["temperature"], 0.4)
        self.assertEqual(MockAIHandler.requests[0]["max_tokens"], 320)

    def test_safe_mode_masks_email(self) -> None:
        (self.repo / "app.py").write_text("owner = 'private@example.com'\n", encoding="utf-8")
        result = run([sys.executable, str(MAIN), "commit", "--dry-run"], self.repo, os.environ.copy())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[MASKED]", result.stdout)
        self.assertNotIn("private@example.com", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
