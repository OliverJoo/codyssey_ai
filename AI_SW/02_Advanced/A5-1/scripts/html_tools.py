"""Standalone Markdown, accessible SVG and code-link rendering for A5-1."""

import base64
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = []

CSS = """
:root{--paper:#f3f5f7;--ink:#14213d;--muted:#475569;--gold:#a67c20;--rule:#b8c2cf}
*{box-sizing:border-box}html{scroll-behavior:auto}body{margin:0;background:var(--paper);color:var(--ink);overflow-wrap:anywhere;font:17px/1.85 'Geist','Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif}
main{max-width:1100px;margin:auto;padding:48px 40px}h1{font:400 42px/1.4 'Instrument Serif','Noto Serif KR',Georgia,serif;margin:16px 0 28px}h2{font-size:27px;line-height:1.5;margin-top:60px;border-bottom:1px solid var(--rule);padding-bottom:16px}h3{font-size:20px;margin-top:32px}p{margin:16px 0;overflow-wrap:anywhere}a{color:#1d4ed8;text-underline-offset:4px;overflow-wrap:anywhere}code,pre{font-family:'Geist Mono',Menlo,Consolas,monospace}code{font-size:.9em}pre{background:#e7ebf0;border:1px solid var(--rule);padding:20px;overflow-x:auto;line-height:1.6;font-size:13px;border-radius:6px}pre code{font-size:inherit}.source-line{display:block;scroll-margin-top:16px;white-space:pre}.source-line:target{background:#fff0c7;outline:2px solid var(--gold)}.ln{display:inline-block;width:4em;color:var(--muted);text-decoration:none}.table-scroll,.diagram,.formula{overflow-x:auto;max-width:100%}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--rule)}th{background:#e7ebf0}figure{margin:32px 0}figure img{max-width:100%;height:auto;display:block;margin:auto;border:1px solid var(--rule)}figcaption{color:var(--muted);font-size:14px;text-align:center}.diagram svg{display:block;width:100%;min-width:600px;height:auto}.formula{padding:20px 0}math{font-size:21px}nav{padding:24px 0;border-block:1px solid var(--rule)}nav ul{columns:2;padding-left:24px}.status{border-left:4px solid var(--gold);padding:16px 24px;background:#ebe6d8}.tag{font:12px 'Geist Mono',Menlo,monospace;letter-spacing:.12em;color:var(--muted)}details{margin:24px 0}summary{cursor:pointer;font-weight:600}.source-section{margin-top:60px}.source-section pre{max-height:none}footer{font-size:13px;color:var(--muted);margin-top:60px;padding-top:24px;border-top:1px solid var(--rule)}
:root{--code-bg:#e7ebf0;--code-fg:#14213d;--code-muted:#475569;--code-target:#f4eddf}
code{background:var(--code-bg);color:var(--code-fg);padding:2px 5px;border-radius:4px}
pre{background:var(--code-bg);color:var(--code-fg);line-height:1.7;color-scheme:light}
pre code{background:transparent;color:inherit;padding:0;border:0;border-radius:0;font-size:inherit;overflow-wrap:normal}
.source-line{background:transparent;color:inherit;min-height:1.7em}
.ln{background:transparent;color:var(--code-muted);text-align:right;margin-right:16px;user-select:none}
.source-line:target{background:var(--code-target);color:var(--code-fg);outline:1px solid var(--gold)}
.source-line:target .ln{color:var(--code-muted)}
@media(max-width:640px){main{padding:24px 18px}h1{font-size:32px}h2{font-size:23px}body{font-size:16px}nav ul{columns:1}table{min-width:620px}pre{padding:14px;font-size:12px}}
@media print{main{max-width:none;padding:0}body{font-size:11pt}pre{white-space:pre-wrap;overflow-wrap:anywhere}nav{display:none}.diagram svg{min-width:0}h2{break-after:avoid}figure,.formula{break-inside:avoid}details{display:block}}
"""

def anchor(file, line):
    """문서 전체에서 유일한 파일·줄 ID를 만든다."""
    return "code-"+file.replace("/", "-").replace(".", "-")+f"-L{line}"

def inline(text):
    """이 문서에서 사용하는 링크·코드·강조를 안전하게 HTML로 바꾼다."""
    protected = []
    def keep(value):
        protected.append(value)
        return f"@@INLINE{len(protected)-1}@@"
    text = re.sub(r"`([^`]+)`", lambda m: keep("<code>"+escape(m[1])+"</code>"), text)
    def link(match):
        label, url = match[1], match[2]
        if url.startswith("https://"):
            return keep(escape(label)+" <span class=\"reference\">("+escape(url)+")</span>")
        normalized = url.removeprefix("../")
        code = re.fullmatch(r"(.+\.py)#L(\d+)", normalized)
        if code:
            url = "#"+anchor(code[1], int(code[2]))
        elif normalized.endswith(".py") and (ROOT/normalized).is_file():
            url = "#"+anchor(normalized, 1)
        elif normalized in {"docs/code_walkthrough.md", "docs/code_walkthrough.html"}:
            url = "#guide"
        elif url.startswith("../"):
            url = "../"+normalized
        elif not url.startswith(("http", "#")):
            url = "../"+url
        return keep(f'<a href="{escape(url, quote=True)}">{escape(label)}</a>')
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    for index, value in enumerate(protected):
        text = text.replace(f"@@INLINE{index}@@", value)
    return text

def diagram(slug, title, nodes):
    """diagram-design flowchart와 financial-services 토큰의 정적 SVG."""
    parts = [f'<div class="diagram"><svg viewBox="0 0 960 600" role="img" aria-labelledby="{slug}-title {slug}-desc"><title id="{slug}-title">{escape(title)}</title><desc id="{slug}-desc">'+escape(" → ".join(node[0] for node in nodes))+"의 처리 순서를 보여 줍니다.</desc><defs>"]
    for name, color in [("arrow", "#475569"), ("arrow-accent", "#a67c20"), ("arrow-link", "#1d4ed8")]:
        parts.append(f'<marker id="{slug}-{name}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{color}"/></marker>')
    parts.append('</defs><rect width="960" height="600" fill="#f3f5f7"/>')
    ys = [80, 244, 408]
    for index in range(2):
        parts.append(f'<line x1="480" y1="{ys[index]+96}" x2="480" y2="{ys[index+1]}" stroke="#475569" stroke-width="1.2" marker-end="url(#{slug}-arrow)"/>')
    for index, ((label, sublabel), y) in enumerate(zip(nodes, ys)):
        stroke, fill = ("#a67c20", "#eee7d7") if index == 1 else ("#14213d", "#ffffff")
        parts.append(f'<rect x="320" y="{y}" width="320" height="96" rx="{8 if index == 1 else 20}" fill="{fill}" stroke="{stroke}"/>')
        parts.append(f'<text x="480" y="{y+40}" text-anchor="middle" font-family="Geist, Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif" font-size="20" font-weight="600" fill="#14213d">{escape(label)}</text>')
        parts.append(f'<text x="480" y="{y+68}" text-anchor="middle" font-family="Geist Mono, Menlo, monospace" font-size="12" fill="#475569">{escape(sublabel)}</text>')
    parts.append('</svg></div>')
    return "".join(parts)

def formula(text):
    """수식을 MathML로 렌더링하고 텍스트 대체를 함께 제공한다."""
    def label(value):
        return "<mtext>"+escape(value)+"</mtext>"
    def fraction(numerator, denominator):
        return "<mfrac><mrow>"+numerator+"</mrow><mrow>"+denominator+"</mrow></mfrac>"
    if text.startswith("RMSE="):
        expression=label("RMSE=")+"<msqrt>"+fraction(label("Σᵢ(yᵢ−ŷᵢ)²"),label("n"))+"</msqrt>"
    elif text.startswith("R²="):
        expression=label("R²=1−")+fraction(label("Σᵢ(yᵢ−ŷᵢ)²"),label("Σᵢ(yᵢ−ȳ)²"))
    elif text.startswith("z="):
        expression=label("z=")+fraction(label("x−μtrain"),label("σtrain"))
    elif text.startswith("p(overdue"):
        expression=label("p(overdue=1|x)=")+fraction(label("1"),label("1+exp(−s)"))
    elif text.startswith("class_weight"):
        expression=label("class_weight(c)=")+fraction(label("n_train"),label("2×n_c"))
    elif text.startswith("Precision="):
        expression=label("Precision=")+fraction(label("TP"),label("TP+FP"))+label(", Recall=")+fraction(label("TP"),label("TP+FN"))
    elif text.startswith("Accuracy="):
        expression=label("Accuracy=")+fraction(label("TP+TN"),label("TP+TN+FP+FN"))
    elif text.startswith("income_per_card="):
        expression=label("income_per_card=")+fraction(label("annual_income"),label("credit_card_count"))
    elif text.startswith("Lasso:"):
        expression=label("Lasso: ")+fraction(label("Σᵢ(yᵢ−ŷᵢ)²"),label("2n"))+label("+αΣⱼ|wⱼ|")
    elif text.startswith("IDF(t)="):
        expression = label("IDF(t)=ln(")+fraction(label("N+1"),label("DF(t)+1"))+label(")+1")
    elif text.startswith("cos(q,d)="):
        expression = label("cos(q,d)=")+fraction(label("q·d"),label("‖q‖₂‖d‖₂"))
    elif text.startswith("x̂="):
        expression = label("x̂=")+fraction("<mi>x</mi>","<msqrt><mrow><mo>Σ</mo><msup><msub><mi>x</mi><mi>j</mi></msub><mn>2</mn></msup></mrow></msqrt>")
    elif text.startswith("BM25(q,d)="):
        expression = label("BM25(q,d)=Σₜ IDFbm25(t)×")+fraction(label("tf(t,d)(k1+1)"),label("tf(t,d)+k1(1−b+b×len(d)/avglen)"))
    elif text.startswith("F1="):
        expression = label("F1=")+fraction(label("2×Precision×Recall"),label("Precision+Recall"))
    else:
        expression = label(text)
    return '<div class="formula"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow>'+expression+'</mrow><annotation encoding="text/plain">'+escape(text)+'</annotation></semantics></math></div>'


def markdown_html(markdown, prefix):
    """추가 문서 라이브러리 없이 제한된 Markdown 문법을 렌더링한다."""
    lines = markdown.splitlines()
    result, i, heading_count = [], 0, 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            contents = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                contents.append(lines[i]); i += 1
            result.append("<pre><code>"+escape("\n".join(contents))+"</code></pre>")
        elif line.startswith("$$ "):
            result.append(formula(line[3:-3]))
        elif line.startswith("<!-- diagram:"):
            slug = line.split(":", 1)[1].split()[0]
            section = next(section for section in SECTIONS if section["id"] == slug)
            result.append(diagram(slug, section["title"], section["diagram"]))
        elif line.startswith("!["):
            match = re.match(r"!\[([^\]]+)\]\(([^)]+)\)", line)
            path = (ROOT/"docs"/match[2]).resolve()
            encoded = base64.b64encode(path.read_bytes()).decode()
            result.append(f'<figure><img src="data:image/png;base64,{encoded}" alt="{escape(match[1], quote=True)}"><figcaption>{escape(match[1])}</figcaption></figure>')
        elif line.startswith("|"):
            table = []
            while i < len(lines) and lines[i].startswith("|"):
                table.append(lines[i]); i += 1
            rows = []
            for index, row in enumerate(table):
                if index == 1 and re.fullmatch(r"[| :\-]+", row):
                    continue
                tag = "th" if index == 0 else "td"
                rows.append("<tr>"+"".join(f"<{tag}>"+inline(cell.strip())+f"</{tag}>" for cell in row.strip("|").split("|"))+"</tr>")
            result.append('<div class="table-scroll"><table>'+"".join(rows)+"</table></div>")
            continue
        elif re.match(r"^#{1,6} ", line):
            level = len(line)-len(line.lstrip("#"))
            heading_count += 1
            title = line[level+1:]
            section = next((section for section in SECTIONS if section["title"] == title), None)
            identifier = section["id"] if section and prefix == "guide" else f"{prefix}-h{heading_count}"
            result.append(f'<h{level} id="{identifier}">'+inline(title)+f"</h{level}>")
        elif line.startswith("- ") or re.match(r"\d+\. ", line):
            tag = "ul" if line.startswith("- ") else "ol"
            items = []
            while i < len(lines) and (lines[i].startswith("- ") if tag == "ul" else bool(re.match(r"\d+\. ", lines[i]))):
                items.append("<li>"+inline(re.sub(r"^(?:- |\d+\. )", "", lines[i]))+"</li>"); i += 1
            result.append(f"<{tag}>"+"".join(items)+f"</{tag}>")
            continue
        else:
            result.append("<p>"+inline(line)+"</p>")
        i += 1
    return "\n".join(result)
