"""Git 명령 실행과 변경 내용 수집을 담당합니다."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .models import GitChanges


class GitError(RuntimeError):
    """Git 저장소 또는 Git 명령 오류입니다."""


def _run_git(*args: str) -> str:
    """허용된 Git 조회 명령을 실행하고 문자열을 돌려줍니다."""
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise GitError("git 실행 파일을 찾을 수 없습니다.") from exc
    except subprocess.CalledProcessError as exc:
        reason = (exc.stderr or exc.stdout or "Git 명령 실행 실패").strip()
        raise GitError(reason) from exc
    # status의 첫 칸은 staged 상태를 뜻하므로 선행 공백을 보존합니다.
    return result.stdout.rstrip("\r\n")


def _parse_files(status: str) -> tuple[str, ...]:
    """git status --short 결과에서 파일 경로를 추출합니다."""
    paths: list[str] = []
    for line in status.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        # rename 표기에서는 변경 후 경로를 사용합니다.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip('"'))
    return tuple(dict.fromkeys(paths))


def collect_changes() -> GitChanges:
    """저장소 루트에서 staged/unstaged 변경을 모두 수집합니다."""
    root_text = _run_git("rev-parse", "--show-toplevel")
    root = Path(root_text).resolve()
    if Path.cwd().resolve() != root:
        raise GitError(f"Git 저장소 루트에서 실행하세요: {root}")

    status = _run_git("status", "--short")
    files = _parse_files(status)
    if not files:
        return GitChanges(str(root), _run_git("branch", "--show-current"), "", "", ())

    # git diff 범위 안에서 staged와 unstaged 변경을 각각 읽습니다.
    unstaged = _run_git("diff", "--no-ext-diff", "--unified=3", "--", *files)
    staged = _run_git("diff", "--cached", "--no-ext-diff", "--unified=3", "--", *files)
    sections = []
    if staged:
        sections.append("[STAGED]\n" + staged)
    if unstaged:
        sections.append("[UNSTAGED]\n" + unstaged)
    if not sections:
        sections.append("[DIFF 없음: 새 파일 경로는 status에서 확인]")
 
    return GitChanges(
        root=str(root),
        branch=_run_git("branch", "--show-current") or "(detached HEAD)",
        status=status,
        diff="\n\n".join(sections),
        files=files,
    )
