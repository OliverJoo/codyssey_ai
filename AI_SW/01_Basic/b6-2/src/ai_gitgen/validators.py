"""AI 응답을 파싱하고 제출 형식으로 검증·정리합니다."""

from __future__ import annotations

import json
import re

from .models import GeneratedMessage


class ValidationError(RuntimeError):
    """AI 응답이 필요한 형식을 만족하지 못한 경우입니다."""


def _parse_json(raw: str) -> dict:
    """코드 펜스를 제거한 뒤 JSON 객체를 읽습니다."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.IGNORECASE)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValidationError("AI 응답을 JSON으로 해석할 수 없습니다. 다시 실행하세요.") from exc
    if not isinstance(value, dict):
        raise ValidationError("AI 응답의 최상위 값은 JSON 객체여야 합니다.")
    return value


def _one_line(value: object, limit: int, label: str) -> tuple[str, list[str]]:
    """제목을 한 줄로 만들고 최대 길이를 넘으면 안전하게 자릅니다."""
    title = " ".join(str(value or "").split())
    if not title:
        raise ValidationError(f"{label}이 비어 있습니다.")
    warnings: list[str] = []
    if len(title) > limit:
        title = title[:limit].rstrip()
        warnings.append(f"{label}을 {limit}자로 잘랐습니다.")
    return title, warnings


def _items(value: object, label: str, required: bool) -> list[str]:
    """배열 항목을 한 줄 문자열 목록으로 정리합니다."""
    if not isinstance(value, list):
        value = []
    items = [" ".join(str(item).split()).lstrip("- ") for item in value]
    items = [item for item in items if item]
    if required and not items:
        raise ValidationError(f"{label}에 한 개 이상의 항목이 필요합니다.")
    return items


def format_commit(raw: str) -> GeneratedMessage:
    """commit 제목 72자 제한과 선택 본문 형식을 적용합니다."""
    data = _parse_json(raw)
    title, warnings = _one_line(data.get("title"), 72, "commit 제목")
    if len(title) > 50:
        warnings.append("commit 제목이 권장 길이 50자를 넘습니다.")
    body_items = _items(data.get("body"), "commit body", required=False)[:2]
    body = "\n".join(f"- {item}" for item in body_items)
    return GeneratedMessage(title, body, tuple(warnings))


def format_pr(raw: str) -> GeneratedMessage:
    """PR 제목과 세 개의 필수 본문 섹션을 만듭니다."""
    data = _parse_json(raw)
    title, warnings = _one_line(data.get("title"), 80, "PR 제목")
    sections = (
        ("Why", _items(data.get("why"), "Why", required=True)),
        ("What", _items(data.get("what"), "What", required=True)),
        ("How to Test", _items(data.get("how_to_test"), "How to Test", required=True)),
    )
    body_parts = []
    for heading, items in sections:
        body_parts.append(f"## {heading}\n" + "\n".join(f"- {item}" for item in items))
    return GeneratedMessage(title, "\n\n".join(body_parts), tuple(warnings))
