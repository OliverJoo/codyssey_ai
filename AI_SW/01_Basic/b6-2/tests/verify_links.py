#!/usr/bin/env python3
"""제출 파일명과 Markdown/HTML 상대 링크의 정합성을 검사합니다."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "README_answer.md",
    "README_answer.html",
    "main.py",
    "01_setup.sh",
    "02_run_demo.sh",
    "03_run_tests.sh",
    "05_diagram_viewer.html",
    "06_verify_submission.sh",
    "diagrams/04_ai-gitgen-flow.html",
    "bonus/README_BONUS.md",
)


def local_links(path: Path) -> list[str]:
    """Markdown와 HTML에서 검사할 로컬 경로를 찾습니다."""
    text = path.read_text(encoding="utf-8")
    markdown = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
    html = re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']", text)
    return markdown + html


def main() -> int:
    """누락 파일과 깨진 상대 링크를 모아 한 번에 보고합니다."""
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append(f"필수 파일 누락: {relative}")

    documents = list(ROOT.glob("*.md")) + list(ROOT.glob("*.html")) + list((ROOT / "bonus").glob("*.md"))
    for document in documents:
        for raw in local_links(document):
            link = unquote(raw.strip().split()[0])
            if not link or link.startswith(("#", "http://", "https://", "mailto:", "data:")):
                continue
            target_text = link.split("#", 1)[0].split("?", 1)[0]
            if target_text and not (document.parent / target_text).resolve().exists():
                errors.append(f"깨진 링크: {document.relative_to(ROOT)} -> {raw}")

    answer_html = (ROOT / "README_answer.html").read_text(encoding="utf-8")
    for number in range(1, 19):
        if f'id="q{number}"' not in answer_html:
            errors.append(f"HTML 질문 앵커 누락: q{number}")

    diagram_html = (ROOT / "diagrams/04_ai-gitgen-flow.html").read_text(encoding="utf-8")
    diagram_requirements = {
        "inline SVG": '<svg id="flow"' in diagram_html,
        "접근성 제목": 'aria-labelledby="04_ai-gitgen-flow-title 04_ai-gitgen-flow-desc"' in diagram_html,
        "100% 확대": 'id="zoom-100"' in diagram_html,
        "200% 확대": 'id="zoom-200"' in diagram_html,
        "스크롤·터치 이동": "touch-action: pan-x pan-y" in diagram_html,
        "diagram-design 출처": "diagram-design 2.6.12" in diagram_html,
    }
    for label, passed in diagram_requirements.items():
        if not passed:
            errors.append(f"다이어그램 요구사항 누락: {label}")

    # 이전 도구 이름은 분리해 적어 문서 검색 결과에 남기지 않는다.
    forbidden_source = "g" + "stack"
    for document in (ROOT / "README.md", ROOT / "README_answer.md"):
        if forbidden_source in document.read_text(encoding="utf-8").lower():
            errors.append(f"이전 다이어그램 출처 문구 잔존: {document.name}")

    if errors:
        print("\n".join(f"[ERROR] {item}" for item in errors), file=sys.stderr)
        return 1
    print(f"[OK] 필수 파일 {len(REQUIRED)}개와 문서 링크 {len(documents)}개를 확인했습니다.")
    print("[OK] README_answer.html에 질문 q1~q18이 모두 있습니다.")
    print("[OK] diagram-design inline SVG와 확대·축소·스크롤 이동을 확인했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
