"""명령행 옵션과 전체 실행 흐름을 연결합니다."""

from __future__ import annotations

import argparse
import os
import sys

from .api_client import APIError, request_completion
from .config import ConfigError, load_convention
from .git_reader import GitError, collect_changes
from .prompts import build_prompt
from .safety import protect_changes
from .validators import ValidationError, format_commit, format_pr


DEFAULT_API_URL = "https://copa.codyssey.kr/v1/chat/completions"


def _parser() -> argparse.ArgumentParser:
    """PDF 요구사항의 두 하위 명령과 공통 옵션을 정의합니다."""
    parser = argparse.ArgumentParser(description="Git 변경 내용으로 commit/PR 초안을 만듭니다.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("commit", "pr"):
        sub = subparsers.add_parser(command, help=f"{command} 초안 생성")
        sub.add_argument("--model", "-model", default="gpt-5.4-mini", help="AI 모델 이름")
        sub.add_argument(
            "--temperature", "-temperature", type=float, default=0.2,
            help="창의성 정도(0~2, 기본 0.2)",
        )
        sub.add_argument(
            "--max-tokens", "-max_tokens", type=int, default=500,
            help="최대 출력 토큰(64~2000, 기본 500)",
        )
        sub.add_argument(
            "--safe-mode", action=argparse.BooleanOptionalAction, default=True,
            help="민감정보 마스킹 사용(기본 켜짐)",
        )
        sub.add_argument("--max-files", type=int, default=10, help="AI에 보낼 최대 파일 수")
        sub.add_argument("--max-diff-lines", type=int, default=200, help="AI에 보낼 최대 diff 줄 수")
        sub.add_argument(
            "--convention-file", help="[보너스] convention이 담긴 JSON 파일",
        )
        sub.add_argument("--dry-run", action="store_true", help="API 호출 없이 프롬프트만 확인")
    return parser


def _validate_options(args: argparse.Namespace) -> None:
    """API 비용과 오입력을 줄이도록 옵션 범위를 검사합니다."""
    if not 0 <= args.temperature <= 2:
        raise ValueError("temperature는 0 이상 2 이하여야 합니다.")
    if not 64 <= args.max_tokens <= 2000:
        raise ValueError("max-tokens는 64 이상 2000 이하여야 합니다.")
    if not 1 <= args.max_files <= 100:
        raise ValueError("max-files는 1 이상 100 이하여야 합니다.")
    if not 1 <= args.max_diff_lines <= 5000:
        raise ValueError("max-diff-lines는 1 이상 5000 이하여야 합니다.")


def _print_result(command: str, result, call_count: int) -> None:
    """복사하기 쉽도록 제목과 본문을 구분해서 출력합니다."""
    title_label = "COMMIT TITLE" if command == "commit" else "PR TITLE"
    body_label = "COMMIT BODY" if command == "commit" else "PR BODY"
    print(f"\n=== {title_label} ===")
    print(result.title)
    print(f"\n=== {body_label} ===")
    print(result.body or "(본문 없음)")
    if result.warnings:
        print("\n=== VALIDATION NOTES ===")
        for warning in result.warnings:
            print(f"- {warning}")
    print(f"\n[INFO] API 호출 횟수: {call_count}")
    print("[NOTICE] AI 초안입니다. 복사하기 전에 diff와 함께 사람이 검토하세요.")


def main(argv: list[str] | None = None) -> int:
    """Git 수집, 안전 처리, API 호출, 형식 검증을 순서대로 실행합니다."""
    args = _parser().parse_args(argv)
    try:
        _validate_options(args)
        changes = collect_changes()
        if not changes.files:
            print("[INFO] 변경 사항이 없습니다. AI API를 호출하지 않습니다.")
            return 0

        safe = protect_changes(
            changes,
            enabled=args.safe_mode,
            max_files=args.max_files,
            max_lines=args.max_diff_lines,
        )
        convention = load_convention(args.convention_file)
        prompt = build_prompt(args.command, changes, safe, convention)
        print(
            f"[INFO] safe-mode={'ON' if args.safe_mode else 'OFF'}, "
            f"파일 {safe.files_used}/{safe.files_total}, diff {safe.lines_used}줄, "
            f"마스킹 {safe.masked_count}건"
        )
        if safe.truncated:
            print("[INFO] 안전 제한에 따라 일부 변경 내용이 생략되었습니다.")
        if args.dry_run:
            print("\n=== API PROMPT (DRY RUN) ===")
            print(prompt)
            print("\n[INFO] API 호출 횟수: 0")
            return 0

        api_key = os.environ.get("AI_API_KEY", "").strip()
        if not api_key:
            raise APIError("AI_API_KEY 환경 변수가 없습니다. README의 설정 방법을 확인하세요.")
        api_url = os.environ.get("AI_API_URL", DEFAULT_API_URL).strip()
        raw = request_completion(
            api_url=api_url,
            api_key=api_key,
            prompt=prompt,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        result = format_commit(raw) if args.command == "commit" else format_pr(raw)
        _print_result(args.command, result, call_count=1)
        return 0
    except (GitError, APIError, ConfigError, ValidationError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
