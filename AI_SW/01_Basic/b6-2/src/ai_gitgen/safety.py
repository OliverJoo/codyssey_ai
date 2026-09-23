"""AI로 보내기 전 민감정보와 입력 크기를 줄입니다."""

from __future__ import annotations

import re

from .models import GitChanges, SafetyReport


MASK_PATTERNS = (
    # 이메일 주소
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    # sk-로 시작하는 API 키
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    # Authorization 헤더 등에 쓰이는 Bearer 토큰
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}=*"),
    # api_key, secret, password, token 형태의 키-값 쌍
    re.compile(
        r"(?i)(api[_-]?key|secret|password|token)(\s*[:=]\s*)([^\s,;]+)"
    ),
)


def _mask(text: str) -> tuple[str, int]:
    """알려진 민감정보 패턴을 고정 문자열로 바꿉니다."""
    count = 0
    for index, pattern in enumerate(MASK_PATTERNS):
        if index == 3:
            text, found = pattern.subn(r"\1\2[MASKED]", text)
        else:
            text, found = pattern.subn("[MASKED]", text)
        count += found
    return text, count


def protect_changes(
    changes: GitChanges,
    *,
    enabled: bool = True,
    max_files: int = 10,
    max_lines: int = 200,
) -> SafetyReport:
    """파일/줄 수를 제한하고 선택적으로 민감정보를 마스킹합니다."""
    selected_files = set(changes.files[:max_files])
    status_lines = [
        line for line in changes.status.splitlines() if line[3:].strip().split(" -> ")[-1].strip('"') in selected_files
    ]
    diff_lines = changes.diff.splitlines()
    limited_lines = diff_lines[:max_lines]
    status = "\n".join(status_lines)
    diff = "\n".join(limited_lines)
    masked_count = 0
    if enabled:
        status, status_masks = _mask(status)
        diff, diff_masks = _mask(diff)
        masked_count = status_masks + diff_masks

    return SafetyReport(
        status=status,
        diff=diff,
        masked_count=masked_count,
        files_used=len(selected_files),
        files_total=len(changes.files),
        lines_used=len(limited_lines),
        truncated=len(changes.files) > max_files or len(diff_lines) > max_lines,
    )
