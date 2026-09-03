#!/usr/bin/env python3
"""b1-1 문서 링크와 diagram-design 산출물 계약을 검사한다."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent
FILES = [
    ROOT / "01_README.md",
    ROOT / "16_README_answer.md",
    ROOT / "17_README_answer.html",
]


def local_links(path: Path) -> set[str]:
    """Markdown와 HTML에서 로컬 파일 링크만 반환한다."""
    text = path.read_text(encoding="utf-8")
    links = set(re.findall(r"\[[^]]*\]\(([^)]+)\)", text))
    links.update(re.findall(r'href=["\']([^"\']+)["\']', text))
    return {
        link
        for link in links
        if link and not link.startswith(("#", "http://", "https://", "mailto:"))
    }


def main() -> int:
    missing: list[str] = []
    for source in FILES:
        if not source.exists():
            missing.append(source.name)
            continue
        for link in local_links(source):
            target = unquote(urlparse(link).path)
            if target and not (source.parent / target).resolve().exists():
                missing.append(f"{source.name} -> {target}")

    diagram = ROOT / "02_mission-flow.html"
    if diagram.exists():
        html = diagram.read_text(encoding="utf-8")
        required = [
            'role="img"',
            'aria-labelledby="02_mission-flow-title 02_mission-flow-desc"',
            '<title id="02_mission-flow-title">',
            '<desc id="02_mission-flow-desc">',
            'id="zoom-fit"',
            'id="zoom-50"',
            'id="zoom-100"',
            'id="zoom-150"',
            'id="zoom-200"',
        ]
        missing.extend(f"02_mission-flow.html missing {item}" for item in required if item not in html)
        if "<script" in html.lower():
            missing.append("02_mission-flow.html must use static CSS zoom without JavaScript")
    else:
        missing.append(diagram.name)

    if missing:
        print("[FAIL] 정합성 오류")
        print("\n".join(f"- {item}" for item in missing))
        return 1
    print("[PASS] 문서 링크, inline SVG 접근성 ID, 5단계 CSS 배율 정합성")
    return 0


if __name__ == "__main__":
    sys.exit(main())
