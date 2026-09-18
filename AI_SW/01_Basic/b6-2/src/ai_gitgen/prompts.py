"""commit과 PR 목적에 맞는 프롬프트를 만듭니다."""

from __future__ import annotations

from .models import GitChanges, SafetyReport


def build_prompt(command: str, changes: GitChanges, safe: SafetyReport, convention: str = "") -> str:
    """AI가 JSON만 반환하도록 구체적인 문맥과 형식을 제공합니다."""
    context = f"""당신은 신중한 Git 메시지 작성 도우미입니다.
추측하지 말고 제공된 변경 내용만 요약하세요. 한국어로 작성하세요.
브랜치: {changes.branch}
파일: {', '.join(changes.files[:safe.files_used])}
상태:
{safe.status}

diff:
{safe.diff}
"""
    if convention:
        context += f"\n프로젝트 규칙: {convention}\n"

    if command == "commit":
        return context + """
다음 JSON만 반환하세요. 마크다운 코드 블록은 쓰지 마세요.
{"title":"한 줄 제목","body":["변경 파일/모듈 또는 핵심 요약", "선택 요약"]}
규칙: title은 권장 50자, 최대 72자입니다. body는 0~2개 항목이며 각 항목은 짧게 씁니다.
"""
    return context + """
다음 JSON만 반환하세요. 마크다운 코드 블록은 쓰지 마세요.
{"title":"한 줄 PR 제목","why":["이유"],"what":["변경점"],"how_to_test":["검증법"]}
규칙: title은 최대 80자입니다. 세 배열에는 각각 하나 이상의 짧은 항목이 있어야 합니다.
"""
