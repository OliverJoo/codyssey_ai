"""제출 문서의 로컬 링크와 답변 HTML 구조를 검사한다."""

from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def documents() -> list[Path]:
    """제출물에서 링크를 가진 문서를 모두 찾는다."""

    paths = [
        ROOT / "README.md",
        ROOT / "README_answer.md",
        ROOT / "README_answer.html",
        ROOT / "SUBMISSION.md",
        ROOT / "bonus/README.md",
        ROOT / ".github/pull_request_template.md",
    ]
    paths.extend(sorted((ROOT / "docs").glob("*.md")))
    paths.extend(sorted((ROOT / "diagrams").glob("*.html")))
    return paths


class LinkCollector(HTMLParser):
    """HTML의 href와 src 경로를 모은다."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)


def markdown_links(text: str) -> list[str]:
    """Markdown 링크와 이미지 경로를 추출한다."""

    return re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)


def is_local(link: str) -> bool:
    """웹 주소, 메일, 문서 내부 앵커를 검사 대상에서 뺀다."""

    parts = urlsplit(link)
    return not parts.scheme and not parts.netloc and bool(parts.path)


def check_link(document: Path, link: str) -> str | None:
    """문서를 기준으로 상대 경로가 실제 존재하는지 확인한다."""

    target = (document.parent / unquote(urlsplit(link).path)).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return f"{document.name}: 프로젝트 밖 링크 {link}"
    if not target.exists():
        return f"{document.name}: 없는 경로 {link}"
    return None


def main() -> None:
    """필수 문서, 로컬 링크, 질문 22개를 한 번에 검증한다."""

    errors: list[str] = []
    for document in documents():
        if not document.is_file():
            errors.append(f"필수 문서 없음: {document.name}")
            continue

        text = document.read_text(encoding="utf-8")
        if document.suffix == ".html":
            parser = LinkCollector()
            parser.feed(text)
            links = parser.links
            if text.count("</html>") != 1 or not text.rstrip().endswith("</html>"):
                errors.append(f"{document.name}: </html>은 문서 맨 끝에 한 번만 있어야 함")
        else:
            links = markdown_links(text)

        for link in links:
            if is_local(link):
                error = check_link(document, link)
                if error:
                    errors.append(error)

    answer_html = (ROOT / "README_answer.html").read_text(encoding="utf-8")
    for number in range(1, 23):
        if f'class="qnum">{number}</span>' not in answer_html:
            errors.append(f"README_answer.html: 질문 {number} 없음")

    # 파일별 접두사를 허용하면서 접근성 참조와 배율 기능을 검사한다.
    for diagram in sorted((ROOT / "diagrams").glob("*.html")):
        text = diagram.read_text(encoding="utf-8")
        slug = diagram.stem
        required = [
            'role="img"',
            f'id="{slug}-title"',
            f'id="{slug}-desc"',
            f'aria-labelledby="{slug}-title {slug}-desc"',
            "overflow:auto",
        ]
        for item in required:
            if item not in text:
                errors.append(f"{diagram.name}: 다이어그램 계약 누락 {item}")

        # CSS-only 버튼은 ID 이름보다 표시 배율과 실제 앵커 연결을 검증한다.
        for label in ("50%", "100%", "150%", "200%", "화면 맞춤"):
            if f">{label}</a>" not in text:
                errors.append(f"{diagram.name}: 배율 버튼 누락 {label}")
        for target in re.findall(r'href="#([^"]+)"', text):
            if f'id="{target}"' not in text:
                errors.append(f"{diagram.name}: 연결되지 않은 배율 앵커 #{target}")

    if errors:
        raise SystemExit("\n".join(f"[FAIL] {error}" for error in errors))
    print("[OK] README/답변 문서의 로컬 링크와 질문 22개를 확인했습니다.")


if __name__ == "__main__":
    main()
