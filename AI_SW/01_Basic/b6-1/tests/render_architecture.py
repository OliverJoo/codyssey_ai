"""01_architecture.html의 접근 가능한 SVG를 제출용 PNG로 재생성한다(macOS)."""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
HTML = PROJECT / "01_architecture.html"
OUTPUT = PROJECT / "docs/architecture.png"


def main() -> None:
    match = re.search(r"<svg\b.*?</svg>", HTML.read_text(encoding="utf-8"), re.DOTALL)
    if match is None:
        raise RuntimeError("01_architecture.html에서 SVG를 찾지 못했습니다.")

    with tempfile.TemporaryDirectory(prefix="b6-1-architecture-") as temporary:
        temp_dir = Path(temporary)
        svg_path = temp_dir / "architecture.svg"
        svg_path.write_text(match.group(0), encoding="utf-8")
        subprocess.run(
            ["qlmanage", "-t", "-s", "2400", "-o", str(temp_dir), str(svg_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        rendered = temp_dir / "architecture.svg.png"
        if not rendered.exists():
            raise RuntimeError("Quick Look이 PNG를 생성하지 못했습니다.")
        # Quick Look은 SVG를 2400x2400 정사각형 캔버스 중앙에 배치한다.
        # 원래 viewBox(1200x680) 비율만 남겨 제출용 풍경형 PNG로 잘라낸다.
        subprocess.run(
            [
                "sips", "-c", "1360", "2400", "--cropOffset", "520", "0",
                str(rendered), "--out", str(OUTPUT),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    print(f"[PASS] {OUTPUT}")


if __name__ == "__main__":
    main()
