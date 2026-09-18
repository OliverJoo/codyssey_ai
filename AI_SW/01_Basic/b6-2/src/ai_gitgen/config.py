"""선택 보너스인 프로젝트 규칙 파일을 읽습니다."""

from __future__ import annotations

import json
from pathlib import Path


class ConfigError(RuntimeError):
    """보너스 설정 파일을 읽을 수 없는 경우입니다."""


def load_convention(path_text: str | None) -> str:
    """JSON 설정의 convention 문자열을 반환합니다."""
    if not path_text:
        return ""
    path = Path(path_text)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"규칙 파일을 읽을 수 없습니다: {path}") from exc
    value = data.get("convention") if isinstance(data, dict) else None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("규칙 파일에 비어 있지 않은 convention 문자열이 필요합니다.")
    return value.strip()
