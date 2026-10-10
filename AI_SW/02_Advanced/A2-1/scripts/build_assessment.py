"""실제 코드·실행 JSON·노트북으로 단일 code_walkthrough.html과 README.md를 만든다.

diagram-design 2.6.12의 flowchart/doc-inline 및 financial-services 프로필을 적용한다.
HTML은 SVG, PNG, CSS를 내장한다. 코드 링크는 원본에서 만든 실제 행 번호로 이동한다.
"""

import ast
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import unicodedata

import markdown
import nbformat

from answer_content import ITEMS
from build_html import CSS, math_markup
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAPER, INK, MUTED, GOLD = '#f3f5f7', '#14213d', '#475569', '#a67c20'
SANS = "Geist, 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
MONO = "'Geist Mono', Menlo, monospace"
EXTRA_CSS = '''
.answer-section{padding-bottom:48px;border-bottom:1px solid var(--rule)}
.concept{border-left:3px solid var(--ink);padding:4px 24px;background:#fff}
.example{padding:4px 24px;border-left:3px solid var(--gold);background:#f4eddf}
.steps{padding-left:28px}.steps li{padding:8px 0 16px}.steps li strong{display:block}
.criterion{color:var(--muted);font-size:15px}.badge{font:600 13px Geist,sans-serif;border:1px solid var(--rule);padding:4px 8px;white-space:nowrap}
.source-line{display:block;scroll-margin-top:24px;min-height:1.7em}.source-line:target{background:#f4eddf;outline:1px solid var(--gold)}
.line-number{display:inline-block;min-width:5ch;margin-right:16px;color:var(--muted);text-align:right;text-decoration:none;user-select:none}
.code-file{margin:40px 0}.code-file pre{padding:16px 8px}.code-file code{font-size:13px}
.code-links{font-size:15px;line-height:2}.result-caption{font-size:15px;color:var(--muted)}
figure{margin:32px 0}figcaption{font-size:14px;color:var(--muted)}.equation{white-space:pre-wrap;overflow-wrap:anywhere;font:16px/1.9 Menlo,'Apple SD Gothic Neo',monospace}
.appendix{border-left:3px solid var(--gold);padding:8px 24px}.notebook-cell{margin:32px 0;scroll-margin-top:24px}.output{white-space:pre-wrap;overflow-wrap:anywhere}
@media print{details:not([open])>*{display:block}main{max-width:none}.answer-section{break-before:page}.equation{font-size:10pt}}
'''


def esc(value):
    """모든 파일·실행 결과 문자열을 HTML 데이터로 안전하게 이스케이프한다."""
    return html.escape(str(value), quote=True)


def slug(path):
    """코드 경로를 안정적인 HTML ID 접두사로 바꾼다."""
    return path.replace('/', '-').replace('.', '-')


def locate_symbol(path, symbol):
    """AST로 실제 클래스·함수 위치를 찾아 소스 링크와 발췌의 범위를 반환한다."""
    source = (ROOT / path).read_text(encoding='utf-8')
    tree = ast.parse(source)
    parts = symbol.split('.')
    node = next(node for node in tree.body if getattr(node, 'name', None) == parts[0])
    for part in parts[1:]:
        node = next(child for child in node.body if getattr(child, 'name', None) == part)
    return node.lineno, node.end_lineno, source.splitlines()


def source_links(item, markdown_mode=False):
    """원본 파일과 브라우저에서 실제 줄로 이동하는 뷰어 링크를 함께 만든다."""
    result = []
    for path, symbol in item['code']:
        line, _, _ = locate_symbol(path, symbol)
        anchor = f'{slug(path)}-L{line}'
        if markdown_mode:
            result.append(f'[{symbol} · {path}:{line}](code_walkthrough.html#{anchor}) '
                          f'([원본](../{path}#L{line}))')
        else:
            result.append(f'<a href="#{anchor}">{esc(symbol)} · {esc(path)}:{line}</a> '
                          f'(<a href="../{esc(path)}#L{line}">원본 .py</a>)')
    notebook = item['notebook']
    if markdown_mode:
        result.append(f'[실행 노트북과 기호식](code_walkthrough.html#{slug(notebook)}) '
                      f'([원본 ipynb](../notebooks/{notebook}))')
    else:
        result.append(f'<a href="#{slug(notebook)}">실행 노트북 · 기호식 · 출력</a> '
                      f'(<a href="../notebooks/{notebook}">원본 ipynb</a>)')
    return '\n\n'.join(result) if markdown_mode else '<br>'.join(result)


def table(headers, rows):
    """긴 숫자와 배열도 해당 영역에서 스크롤할 수 있는 접근 가능한 표를 만든다."""
    head = ''.join(f'<th scope="col">{esc(value)}</th>' for value in headers)
    body = ''.join('<tr>'+''.join(f'<td>{esc(format_value(value))}</td>' for value in row)+'</tr>' for row in rows)
    return f'<div class="table-scroll" tabindex="0"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def format_value(value):
    """표의 수치를 실측 정밀도를 보존한 간결한 표현으로 바꾼다."""
    if isinstance(value, bool):
        return 'PASS' if value else 'FAIL'
    if isinstance(value, float):
        return f'{value:.10g}'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return '관측 구간 내 도달 없음'
    return str(value)


def evidence(item_id, metrics):
    """각 평가 항목에 대응하는 실측 값과 조건만 추려 표로 제공한다."""
    m = metrics
    if item_id in [1, 2]:
        return ['변환', '점 shape / 샘플 수', '변환 전 면적', '변환 후 면적', 'det', '면적비', '오차(%)', '기준(%)', '판정'], [
            [name, f"{row['points_shape']} / {row['sample_count']}", row['before_area'], row['after_area'],
             row['determinant'], row['measured_area_ratio'], row['relative_error_percent'], row['tolerance_percent'], row['passed']]
            for name, row in m['area'].items()]
    if item_id == 3:
        row = m['power_iteration']
        keys = ['matrix', 'matrix_shape', 'iterations', 'eigenvalue', 'reference_eig', 'eigenvector', 'reference_eigenvector',
                'relative_error_percent', 'tolerance_percent', 'passed', 'sign_aligned_vector_l2_error',
                'vector_tolerance', 'vector_passed', 'residual_norm', 'residual_tolerance', 'residual_passed']
        return ['기록 필드', '실제 값'], [[key, row[key]] for key in keys]
    if item_id == 4:
        return ['원본 shape', '요청 k', '유효 k', 'MSE', '최대 픽셀 오차', '원본 값 수', '인자 값 수', '저장 비율'], [
            [row[key] for key in ['image_shape', 'requested_k', 'effective_k', 'mse', 'max_absolute_pixel_error',
                                  'original_values', 'factor_values', 'factor_to_original_ratio']] for row in m['svd']]
    if item_id == 5:
        return ['함수', 'x', 'h', '수치 미분', '해석 미분', '절대오차', '허용오차', '판정'], [
            [row[key] for key in ['function', 'x', 'h', 'numeric', 'analytic', 'absolute_error', 'tolerance', 'passed']]
            for row in m['derivative_sensitivity']]
    if item_id == 6:
        return ['기록', '실제 값'], [*list(m['gradient_visualization'].items()), ['접선 내적 절댓값', m['gradient_tangent_abs_dot']]]
    if item_id in [7, 8]:
        return ['방향', '체크포인트', 'shape', '손계산 4자리', 'NumPy 4자리', '판정'], [
            [row['group'], row['name'], row['shape'], row['hand_rounded_4'], row['numpy_rounded_4'], row['passed']]
            for row in m['backprop_comparison']['rows']]
    if item_id in [9, 11, 12]:
        names = ['circle'] if item_id == 9 else ['ellipse'] if item_id == 12 else ['circle', 'ellipse']
        return ['함수·조건', '업데이트', '최종 손실', '최종 반경', '손실 .01 첫 도달', '이후 유지 시작', '반경 .1 판정'], [
            [f'{name}: {label}', row['updates'], row['final_loss'], row['final_radius'],
             row['first_update_loss_le_0.01'], row['first_sustained_update_loss_le_0.01'], row['within_pdf_radius_0.1']]
            for name in names for label, row in m[name].items()]
    if item_id == 10:
        rows = [[f"circle: lr={row['learning_rate']}", row['coordinate_factor'], row['regime'], row['radius_ratio'],
                 m['learning_rates'][f"GD lr={row['learning_rate']}"]['final_loss']] for row in m['learning_rate_stability']]
        rows += [[f'ellipse: {label}', 1 - 20 * float(label.split('=')[1]),
                  '수렴 (별도 함수)' if label.endswith('=0.01') else 'y 크기 일정 진동 (별도 함수)' if label.endswith('=0.1') else '발산 (별도 함수)',
                  row['final_radius']/(50**.5), row['final_loss']] for label, row in m['ellipse_learning_rates'].items()]
        return ['함수·학습률', '원형/타원 y 배율', '구분', '20회 반경비', '최종 손실'], rows
    if item_id == 13:
        return ['분포', '매개변수', '확률/표준편차', '합/넓은 구간 적분', '판정'], [
            ['Normal', f"mean={row['mean']}, variance={row['variance']}", row['standard_deviation'], row['integral'], row['passed']]
            for row in m['distributions']['normal']] + [
            ['Bernoulli', f"p={row['p']}", row['pmf'], row['sum'], row['passed']] for row in m['distributions']['bernoulli']]
    if item_id == 14:
        return ['로짓', '확률 벡터', '확률 합', '합 절대오차', '허용오차', '판정'], [
            [row[key] for key in ['logits', 'probabilities', 'sum', 'absolute_sum_error', 'tolerance', 'passed']]
            for row in m['softmax_cases']]
    checks = m['loss_likelihood_checks']
    return ['분포', '분포에서 구한 NLL', '손실에서 구한 NLL/합', '오차', '허용오차'], [
        ['Gaussian', checks['gaussian']['nll_from_pdf'], checks['gaussian']['nll_from_mse'],
         checks['gaussian']['maximum_absolute_error'], checks['tolerance']],
        ['Bernoulli', checks['bernoulli']['nll'], checks['bernoulli']['bce_sum'], checks['bernoulli']['absolute_error'], checks['tolerance']],
        ['Categorical', checks['categorical']['nll'], checks['categorical']['ce_sum'], checks['categorical']['absolute_error'], checks['tolerance']]]


def text_width(value, size):
    """프로필의 Unicode wide/full-width 1em 예산으로 SVG 라벨 길이를 측정한다."""
    return sum(0 if unicodedata.category(c) in ('Mn', 'Me') else
               1 if unicodedata.east_asian_width(c) in ('W', 'F') else .60 for c in value) * size


def wrap_svg(value, limit=400, size=16):
    """한글을 축소하지 않고 텍스트를 고정 폭 안에서 여러 줄로 나눈다."""
    lines, current = [], ''
    for word in value.split():
        candidate = current+' '+word if current else word
        if current and text_width(candidate, size) > limit:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def svg_text(x, y, value, size=20, color=INK, anchor='start', mono=False):
    """4px 그리드에 읽기 쉬운 로컬 한글 폰트 폴백을 갖는 텍스트를 그린다."""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-family="{esc(MONO if mono else SANS)}">{esc(value)}</text>')


def diagram(item):
    """doc-inline 960×600 플로차트: 4단계·3직교 연결·1강조·아래 범례를 구성한다."""
    name = f'answer-{item["id"]:02d}'
    result = (f'<figure class="diagram" tabindex="0"><svg xmlns="http://www.w3.org/2000/svg" '
              f'viewBox="0 0 960 600" role="img" aria-labelledby="{name}-title {name}-desc">'
              f'<title id="{name}-title">{esc(item["title"])}</title>'
              f'<desc id="{name}-desc">{esc(item["nodes"][0][0])}에서 시작하여 '
              f'{esc(item["nodes"][-1][0])}까지 실제 구현의 네 계산 단계를 순서대로 보여준다.</desc><defs>')
    for suffix, color in [('arrow', MUTED), ('arrow-accent', GOLD), ('arrow-link', '#1d4ed8')]:
        result += (f'<marker id="{name}-{suffix}" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">'
                   f'<polygon points="0 0, 8 4, 0 8" fill="{color}"/></marker>')
    result += f'</defs><rect width="960" height="600" fill="{PAPER}"/>'
    result += svg_text(48, 44, f'항목 {item["id"]:02d} · 계산과 검증 순서', 24)
    # 네 노드의 연결은 수직이며 각 노드에 하나씩 독립된 접점을 가진다.
    for index in range(3):
        y = 80 + index * 112
        result += f'<path d="M232 {y+80} V{y+112}" stroke="{MUTED}" fill="none" marker-end="url(#{name}-arrow)"/>'
    for index, (label, technical) in enumerate(item['nodes']):
        y = 80 + index * 112
        focal = index == 3
        radius = 20 if index in [0, 3] else 8
        result += f'<rect x="48" y="{y}" width="368" height="80" rx="{radius}" fill="{PAPER}"/>'
        result += (f'<rect data-node="true" x="48" y="{y}" width="368" height="80" rx="{radius}" '
                   f'fill="{"#f4eddf" if focal else "#ffffff"}" stroke="{GOLD if focal else INK}"/>')
        assert text_width(label, 20) <= 336, label
        assert text_width(technical, 16) <= 336, technical
        result += svg_text(232, y+32, label, 20, anchor='middle')
        result += svg_text(232, y+60, technical, 16, MUTED, 'middle', mono=True)
        result += svg_text(464, y+24, f'{index+1:02d} / 관련 식과 확인 기준', 20)
        detail = item['formula'].splitlines()[min(index, len(item['formula'].splitlines())-1)]
        for offset, line in enumerate(wrap_svg(detail)):
            result += svg_text(464, y+52+offset*24, line, 16, MUTED)
    result += f'<line x1="48" y1="544" x2="912" y2="544" stroke="#b8c2cf"/>'
    result += svg_text(48, 576, '위 → 아래: 계산 순서  ·  흰색: 입력·계산  ·  금색: 최종 확인', 16, MUTED)
    result += '</svg><figcaption>diagram-design · financial-services · flowchart · doc-inline 960×600. '
    result += '도식의 네 단계는 개요이며, 아래 설명에 모든 세부 연산과 검증 기준을 풀어 쓴다.</figcaption></figure>'
    return result


def image_markup(filename):
    """실제 Matplotlib PNG를 내장하고 원본 출력 경로를 캡션의 링크로 보존한다."""
    encoded = base64.b64encode((ROOT/'outputs'/filename).read_bytes()).decode()
    captions = {
        'matrix_transformations.png': '45도 회전·S(2,.5)·Sh(.8)의 전후 겹침. 각 축 제목에서 면적비와 오차를 확인한다.',
        'svd_reconstructions.png': '원본과 k=10/50/100 요청 복원. 실제 10/50/64개 성분과 픽셀 MSE·인자 저장 비율을 확인한다.',
        'gradient_contours.png': '등고선 f=1/4/9 및 f=4 위 8점의 기울기. 화살표 길이는 실제 기울기의 1/5다.',
        'derivative_sensitivity.png': '왼쪽에서 오른쪽으로 h가 작아진다. sin의 절단오차 감소 뒤 매우 작은 h의 반올림오차 증가를 확인한다.',
        'circle_paths.png': '원형 함수의 GD·Momentum 경로. 같은 (5,5), lr=.1, 100회; o는 시작, x는 종료다.',
        'circle_loss.png': '원형 함수의 손실 변화. Momentum의 진동과 100회 최종 손실을 함께 읽는다.',
        'learning_rate_paths.png': '같은 원형 함수의 lr=.1/.5/1/1.1 경로. 넓은 범위는 lr=1.1의 발산을 포함한다.',
        'learning_rate_loss.png': '원형에서 .5는 0 도달, 1은 일정 손실의 진동, 1.1은 손실 증가. 로그 표시만 1e-20 하한을 적용한다.',
        'ellipse_learning_rate_loss.png': '추가 검증: 타원 함수에서 lr=.5와 .7의 손실이 폭증한다. 원형 .5 실험과 함수·곡률이 다르다.',
        'ellipse_paths.png': '타원 함수의 동일 조건 비교. lr=.01, β=.9, 200회; 시작·종료와 진동 방향을 읽는다.',
        'ellipse_loss.png': '타원 손실 .01 첫 도달 GD 194회·Momentum 78회. Momentum의 이후 유지 시작은 97회다.',
        'normal_pdf.png': 'N(0,1), N(2,.5)의 밀도. 후자의 분산은 .5이며 표준편차는 √.5다.',
        'bernoulli_pmf.png': 'B(.3), B(.7)의 x=0/1 확률. 두 막대의 합은 각 분포마다 1이다.',
    }
    caption = captions.get(filename, '선택 과제의 실제 실행 결과. 함수·학습률·업데이트 조건을 제목과 범례에서 확인한다.')
    return (f'<figure><img loading="lazy" src="data:image/png;base64,{encoded}" alt="{esc(caption)}">'
            f'<figcaption>{esc(caption)}<br>원본 출력: <a href="../outputs/{filename}">outputs/{filename}</a></figcaption></figure>')


def page(output, title, body, toc='', prefix=''):
    """외부 실행 자원이 없는 공통 문서 레이아웃으로 HTML을 저장한다."""
    navigation_css = 'html{scroll-behavior:auto}'
    output.write_text(f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<meta name="description" content="A2-1 미션의 15개 평가 항목: 개념, 예시, 실제 코드, 도식, 실측 검증">
<style>{CSS}{EXTRA_CSS}{navigation_css}</style></head><body>
<header class="top"><strong>A2-1 · 학습의 수학</strong><nav class="links" aria-label="문서 이동">
<a href="#learning-start">학습 순서</a><a href="#source-code">실제 코드</a>
<a href="#executed-notebooks">노트북 출력</a><a href="#reproduction">재현 방법</a><a href="../README.md">README.md</a></nav></header>
<div class="layout"><aside aria-label="목차"><details open><summary>바로 이동</summary>{toc}</details></aside>
<main>{body}</main></div><footer>diagram-design 2.6.12 · financial-services · SVG/PNG/CSS 내장 · 외부 스크립트 없음<br>
로컬 Geist/Instrument Serif가 있으면 사용하고, 없으면 Apple SD Gothic Neo/Georgia/Menlo로 대체한다.
코드 뷰어는 빌드 시점 원본에서 만든 스냅샷이다. 코드를 수정한 뒤 scripts/build_assessment.py를 다시 실행한다.</footer></body></html>''', encoding='utf-8')


def build_code_reference():
    """모든 구현·실험·테스트의 실제 소스와 모든 행 앵커 및 SHA-256을 생성한다."""
    paths = sorted([*(ROOT/'src').glob('*.py'), *(ROOT/'scripts').glob('*.py'), *(ROOT/'tests').glob('*.py')])
    body, toc, manifest = ['<h2 id="source-code">부록 2. 실제 코드 · 행 번호</h2><p>각 링크는 이 파일 안의 실제 코드 해당 줄로 이동한다. '
                           '줄 번호를 클릭하면 주소에 앵커가 남아 그대로 공유할 수 있다.</p>'], [], []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        key = slug(relative)
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        lines = data.decode().splitlines()
        toc.append(f'<a href="#{key}">{esc(relative)}</a>')
        source = ''.join(f'<span class="source-line" id="{key}-L{i}"><a class="line-number" '
                         f'href="#{key}-L{i}" aria-label="{i}번째 줄">{i}</a>{esc(line)}</span>'
                         for i, line in enumerate(lines, 1))
        body.append(f'<section class="code-file"><h2 id="{key}">{esc(relative)}</h2>'
                    f'<p><a href="../{relative}">원본 파일</a> · {len(lines)}줄<br><code>SHA-256: {digest}</code></p>'
                    f'<pre><code>{source}</code></pre></section>')
        manifest.append({'path': relative, 'sha256': digest, 'line_count': len(lines)})
    (ROOT/'reports/code_reference_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return ''.join(body), ''.join(toc)


def render_notebook_markdown(source):
    """노트북 Markdown과 원래 기호식을 보존하며 TeX 원문은 읽을 수 있게 표시한다."""
    blocks = []

    def store_formula(match):
        """복잡한 행렬 TeX를 누락하거나 틀리게 변환하지 않고 원문 블록으로 보존한다."""
        blocks.append('<pre class="equation" aria-label="수식 원문">'+esc(match.group(1))+'</pre>')
        return '\n\nNOTEBOOKFORMULA'+str(len(blocks)-1)+'END\n\n'

    source = re.sub(r'\$\$(.*?)\$\$', store_formula, source, flags=re.S)
    rendered = markdown.markdown(source, extensions=['tables', 'fenced_code'])
    for index, block in enumerate(blocks):
        rendered = rendered.replace(f'<p>NOTEBOOKFORMULA{index}END</p>', block)
    soup = BeautifulSoup(rendered, 'html.parser')
    for node in list(soup.find_all('table')):
        wrapper = soup.new_tag('div', attrs={'class': 'table-scroll', 'tabindex': '0'})
        node.wrap(wrapper)
    return str(soup)


def build_notebook_reference():
    """실행된 Markdown·코드·텍스트·PNG 출력을 셀 앵커가 있는 HTML로 펼친다."""
    body = ['<h2 id="executed-notebooks">부록 1. 실행 노트북 · 기호식 · 출력</h2><p>원본 ipynb의 모든 셀과 실행 출력을 보존했다. '
            '복잡한 행렬 수식은 원본 TeX를 표시한다. 15항목 답변에는 읽기 쉬운 수식과 수치표가 별도로 있다.</p>']
    toc = []
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        notebook = nbformat.read(path, as_version=4)
        key = slug(path.name)
        toc.append(f'<a href="#{key}">{esc(path.name)}</a>')
        body.append(f'<h2 id="{key}">{esc(path.name)}</h2><p><a href="../notebooks/{path.name}">원본 ipynb</a></p>')
        for index, cell in enumerate(notebook.cells):
            body.append(f'<section class="notebook-cell" id="{key}-cell-{index}">'
                        f'<p class="criterion">셀 {index} · {cell.cell_type} · 실행 {cell.get("execution_count", "—")}</p>')
            if cell.cell_type == 'markdown':
                body.append(render_notebook_markdown(cell.source))
            else:
                body.append('<pre><code>'+esc(cell.source)+'</code></pre>')
                for output in cell.get('outputs', []):
                    if output.output_type == 'stream':
                        body.append('<pre class="output">'+esc(output.text)+'</pre>')
                    elif 'image/png' in output.get('data', {}):
                        body.append(f'<img loading="lazy" src="data:image/png;base64,{output.data["image/png"]}" alt="{esc(path.name)} 셀 {index} 실제 실행 그림">')
                    elif 'text/plain' in output.get('data', {}):
                        body.append('<pre class="output">'+esc(output.data['text/plain'])+'</pre>')
                    elif output.output_type == 'error':
                        raise ValueError(f'노트북 실행 오류: {path.name} cell {index}')
            body.append('</section>')
    # 노트북 원본의 상대 링크는 notebooks/ 기준이므로 docs/에서도 같은 ../src, ../reports가 유효하다.
    return ''.join(body), ''.join(toc)


def extended_explanation(item_id):
    """추가 평가에서 요청한 수식 민감도와 함수별 발산 조건을 명시적으로 보충한다."""
    if item_id == 5:
        return ('<div class="appendix"><h3>추가 검증: h를 줄이면 항상 정확해지는가?</h3><p>'
                'x²의 중심차분은 대수적으로 정확해서 O(h²) 절단오차가 0이다. 아래 표의 차이는 주로 부동소수점 계산 영향이다. '
                '보조 함수 sin(x)의 x=1에서는 h=.1/.01/.001일 때 오차가 약 9.00e-4/9.00e-6/9.01e-8로 '
                '100배씩 줄어드는 O(h²) 구간을 볼 수 있다. 그러나 h=1e-13에서는 오차가 다시 커진다. '
                '민감도 표의 FAIL은 선택한 h가 기준을 만족하지 않았다는 실측 사실이다. 필수 h=1e-5의 x² 실험은 PASS다.</p></div>')
    if item_id == 10:
        return ('<div class="appendix"><h3>추가 검증: 같은 lr=.5라도 타원에서는 발산한다</h3><p>'
                '원형에서 초기값을 키워도 θ_next=0×θ이므로 한 번에 원점에 도달한다. 초기값으로 발산을 만들 수 없다. '
                '대신 PDF가 함께 요구한 타원 f=x²+10y²를 별도 실험으로 사용하면 lr=.5에서 x_next=0, y_next=−9y다. '
                '초기 손실은 275, 첫 업데이트의 손실은 20250이며 이후 y² 손실은 매번 81배 증가한다. '
                '20회 최종 손실은 약 3.6952e40이다. 새 그래프는 .01/.1/.5/.7을 비교한다. '
                '따라서 원형에서는 lr=1.1, 타원에서는 lr=.5라는 두 실제 발산 증거를 제시한다. '
                '“원형에서 lr≥.5가 모두 발산”이라는 문장은 그대로 증명할 수 없다는 사실을 유지한다.</p></div>')
    return ''


def build_answer(metrics):
    """15개를 개념→예시→도식→계산→코드→실측→해석 순서로 설명한다."""
    toc = ''.join(f'<a href="#criterion-{item["id"]}">#{item["id"]} {esc(item["title"])}</a>' for item in ITEMS)
    pdf_name = next(ROOT.glob('*.pdf')).name
    body = ['<p class="eyebrow">A2-1 / LEARN FROM THE CODE / NUMPY</p><h1 id="learning-start">AI는 어떻게 학습하는가<br>개념부터 실제 코드까지 순서대로</h1>'
            '<p>미션 PDF 1~8쪽과 두 차례의 평가 피드백을 대조해 구현·노트북·실험 증거를 보완했다. '
            '각 항목은 개념과 생활 예시부터 시작해 실제 코드의 계산 순서, 수식, 실행 결과, 해석으로 이어진다. '
            '숫자는 reports/metrics.json에서 읽고 코드는 원본 파일의 AST 위치에서 가져온다.</p>'
            '<div class="appendix"><p><strong>먼저 확인할 세 가지</strong>: PDF의 반경 기준은 <b>0.1</b>이다. '
            '원형 lr=.5는 수렴하고 lr>1은 발산한다. 64×64 SVD에서 요청 k=100의 실제 성분 수는 64다. '
            '이 차이를 숨기지 않고 각 항목의 근거와 해석에 표시한다.</p></div>'
            '<p><a href="../reports/experiment_run.txt">전체 실행 로그</a> · <a href="../reports/metrics.json">필수 실측 JSON</a> · '
            '<a href="../reports/test_revision.txt">32개 테스트 결과</a> · <a href="../reports/notebook_execution.txt">노트북 실행 기록</a> · '
            '<a href="#requirements-check">PDF·평가 대조</a></p>'
            '<p class="criterion">읽는 순서: #1~4 좌표와 행렬 → #5~8 미분과 역전파 → #9~12 업데이트 → #13~15 확률과 손실. '
            '도식과 실험 그림은 문서에 내장되어 네트워크 없이 보인다. 파일 링크는 A2-1 폴더 구조를 유지해야 한다.</p>']
    body.append(f'<p><a href="../{esc(pdf_name)}">원본 미션 PDF</a> · '
                '<a href="#reproduction">검증·발표 가이드</a></p>')
    body.append('<h2>전체 연결과 표기</h2><p>행렬은 데이터를 결합하고 공간을 변형한다. 미분은 손실의 변화율을 계산하고, '
                '역전파는 연쇄 법칙으로 가중치까지 이를 전달한다. 최적화는 그 기울기로 가중치를 움직인다. '
                '확률분포는 MSE·BCE·CE라는 손실을 쓰는 이유를 설명한다.</p>'
                '<p><code>@</code>는 행렬곱, <code>⊙</code>는 원소별 곱, <code>()</code>는 스칼라, '
                '<code>(2,)</code>는 두 성분의 벡터, <code>(2,2)</code>는 행렬이다. '
                '<code>lr</code>는 학습률, <code>β</code>는 속도 누적 계수, <code>h</code>는 수치미분 간격이다. '
                '자연로그를 쓰는 BCE·CE의 단위는 nats, MSE의 단위는 예측 대상 단위의 제곱이다.</p>')
    for item in ITEMS:
        number = item['id']
        body.append(f'<section class="answer-section" id="criterion-{number}"><h2>#{number}. {esc(item["title"])}</h2>'
                    f'<p class="criterion">미션 근거: {esc(item["pdf"])} · <a href="#requirements-check">대조 기록</a></p>'
                    f'<h3>개념</h3><div class="concept"><p>{esc(item["concept"])}</p></div>'
                    f'<h3>현실적인 예시</h3><div class="example"><p>{esc(item["example"])}</p></div>')
        body.append(diagram(item))
        body.append('<h3>실제 코드가 수행하는 순서</h3><ol class="steps">'+''.join(
            f'<li><strong>{esc(title)}</strong>{esc(text)}</li>' for title, text in item['steps'])+'</ol>')
        body.append('<h3>핵심 수식과 shape</h3><pre class="equation">'+esc(item['formula'])+'</pre>')
        if number == 15:
            for formula in [r'\mathcal L(\theta)=\prod_{i=1}^n p(y_i|x_i,\theta)',
                            r'-\ln\mathcal L=\frac n2\ln(2\pi\sigma^2)+\frac1{2\sigma^2}\sum_i(y_i-f_\theta(x_i))^2',
                            r'-\ln\mathcal L=-\sum_i[y_i\ln q_i+(1-y_i)\ln(1-q_i)]',
                            r'-\ln\mathcal L=-\sum_i\sum_c y_{ic}\ln q_{ic}']:
                body.append(math_markup(formula, True))
        body.append(extended_explanation(number))
        body.append('<h3>해당 코드로 바로 이동</h3><p class="code-links">'+source_links(item)+'</p>')
        path, symbol = item['code'][0]
        line, end, lines = locate_symbol(path, symbol)
        excerpt_end = min(end, line+27)
        excerpt = '\n'.join(lines[line-1:excerpt_end])
        body.append(f'<details open><summary>실제 소스 발췌: {esc(path)} {line}~{excerpt_end}줄</summary>'
                    f'<pre><code>{esc(excerpt)}</code></pre></details>')
        if excerpt_end < end:
            body.append('<p class="criterion">위는 함수 앞부분의 실제 발췌다. 함수 전체와 검증 위치는 행 번호 링크에서 확인한다.</p>')
        headers, rows = evidence(number, metrics)
        body.append('<h3>실제 실행 결과와 검증 기준</h3>'+table(headers, rows))
        body.append(f'<p class="result-caption">수치 원본: <a href="../reports/metrics.json">reports/metrics.json</a> · '
                    f'<a href="../reports/experiment_run.txt">reports/experiment_run.txt</a>. '
                    'PASS/FAIL은 해당 표의 조건에 대한 로컬 검증 결과이며 외부 평가자의 판정을 대신하지 않는다.</p>')
        body.extend(image_markup(filename) for filename in item['images'])
        body.append('<h3>결과를 설명할 때 짚을 점</h3><ul>'+''.join(f'<li>{esc(note)}</li>' for note in item['notes'])+'</ul></section>')
    return ''.join(body), toc


def markdown_table(headers, rows):
    """HTML과 같은 실측 데이터를 Markdown 표로 출력한다."""
    clean = lambda value: format_value(value).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join('---' for _ in headers)+' |',
                      *['| '+' | '.join(clean(value) for value in row)+' |' for row in rows]])


def update_readme(metrics):
    """PDF 필수 README만 갱신하고 추가 학습 문서는 단일 HTML로 연결한다."""
    readme = '''# A2-1 · AI가 어떻게 학습하는지 수학으로 직접 풀어보기

NumPy로 행렬 변환·Power Iteration·SVD·중심차분·역전파·GD/Momentum·확률/손실 연결을 직접 구현한다.
미션 PDF 1~8쪽과 두 평가 목록을 대조하여 구현, 기호 유도, 수치 기준, 그림 연결을 보완했다.

## 바로 읽을 문서

학습과 설명은 **[docs/code_walkthrough.html](docs/code_walkthrough.html) 하나**에 통합했다.
개념·현실 예시 → 15개 항목의 도식·수식·실제 코드·결과 → 선택 과제 → 재현 방법 → PDF 대조 → 노트북 출력 → 실제 코드 전체 순서다.
코드 링크와 노트북 링크는 같은 HTML 안의 해당 줄·셀로 이동한다.

통합 HTML은 15개의 diagram-design 도식과 실험 PNG, 수치표, 노트북 실행 출력, 실제 코드 전체를 내장한다.
HTML을 더블클릭해 브라우저로 열 수 있다. 코드·원본 파일 링크는 A2-1 폴더 구조를 유지한다.
내장 이미지·SVG·CSS는 네트워크 없이 표시되며 외부 실행 스크립트가 없다.

## 구조와 실행

`src/`는 수학 구현, `scripts/`는 실험·비교·실행·문서 생성, `tests/`는 수학 검증,
`notebooks/`는 기호 유도와 실행 증거, `outputs/`는 PNG, `reports/`는 원본 수치와 검수 기록이다.
이미지 입력과 출처는 `data/`에 있다. [requirements.txt](requirements.txt)에 버전을 고정했다.
현재 검증 환경의 Python은 `/Users/oliverjoo/Dev/Anaconda/anaconda3/envs/py312/bin/python`이다.
같은 버전이 준비된 환경에서 A2-1을 작업 디렉토리로 사용한다.

```sh
python scripts/run_experiments.py --bonus > reports/experiment_run.txt
MPLCONFIGDIR=.cache/matplotlib python -m unittest discover -s tests -v > reports/test_revision.txt 2>&1
python scripts/run_notebooks.py --bonus > reports/notebook_execution.txt
python scripts/build_assessment.py
python scripts/verify_artifacts.py
```

처음 환경을 구성해야 한다면 requirements.txt의 패키지가 필요하다. 이번 보완에서는 이미 설치된 환경을 재사용했다.
브라우저 검수 명령과 검사 범위는 [통합 문서의 재현 방법](docs/code_walkthrough.html#reproduction)에 있다.

## 주요 실제 결과

'''
    summary_rows = [
        ['행렬 면적', '(100,2) 점/100샘플; 세 변환 det·면적비≈1; 상대오차≤1%'],
        ['고유값', f"A=[[4,1],[1,3]]; λ={metrics['power_iteration']['eigenvalue']:.12f}; 20회; eig·벡터·잔차 PASS"],
        ['SVD', '(64,64), 요청10/50/100→유효10/50/64; k=50/64는 인자 값 수가 원본보다 많음'],
        ['미분', 'x², x=3, h=1e-5; 6.000000000039306; 절대오차3.93e-11≤1e-4; h 민감도도 표시'],
        ['역전파', '2→2→1, y=1; 11 체크포인트 shape+round(4) PASS; 전 파라미터 중심차분 검산'],
        ['원형 GD', 'lr=.1,100회; 반경1.4404e-9≤PDF .1; 경로와 손실 PNG 첨부'],
        ['발산', '원형 .5 수렴/1 진동/1.1 발산; 추가 타원 .5에서 손실275→20250→3.6952e40'],
        ['타원 비교', '같은 lr=.01; 손실 .01 첫 도달 GD194/Momentum78, 이후 유지194/97'],
        ['확률', 'N(0,1)/N(2,.5) 및 B(.3)/B(.7) 그림·노트북 출력·정규화 검산'],
        ['Softmax', '최대값 shift·5입력, 합오차≤1e-6 및 유한확률 검사 PASS'],
        ['MLE 연결', 'Normal→MSE, Bernoulli→BCE, categorical→CE의 기호식·독립 우도 검산 PASS'],
    ]
    readme += markdown_table(['실험', '결과'], summary_rows)
    readme += '''

## 기호로 보는 MLE와 손실의 연결

독립 관측에서 L(θ)=∏ᵢp(yᵢ|xᵢ,θ). 로그는 증가 함수여서 argmax L=argmin(−log L)이다.
정규 잡음 εᵢ~N(0,σ²), 같은 양의 고정 분산이라면

```text
log p = −(1/2)log(2πσ²) − (yᵢ−fθ(xᵢ))²/(2σ²)
NLL = n/2 log(2πσ²) + Σᵢ(yᵢ−fθ(xᵢ))²/(2σ²)
    = C + n×MSE/(2σ²)
```

θ에 무관한 C와 양의 고정 계수를 제거하면 MSE와 같은 최소점을 얻는다.
베르누이 p(yᵢ)=qᵢ^yᵢ(1−qᵢ)^(1−yᵢ)에 대해서는

```text
NLL = −log ∏ᵢqᵢ^yᵢ(1−qᵢ)^(1−yᵢ)
    = −Σᵢ[yᵢlog qᵢ+(1−yᵢ)log(1−qᵢ)] = BCE 합
```

카테고리 one-hot 정답의 p(yᵢ)=∏c qᵢc^yᵢc에 대해서는

```text
NLL = −log ∏ᵢ∏c qᵢc^yᵢc = −ΣᵢΣc yᵢc log qᵢc = CE 합
```

고정 n으로 나눈 평균 BCE/CE도 같은 최소점을 갖는다. 상세 수식·생활 예시·코드 검산은
[확률 손실 노트북](notebooks/probability_loss.ipynb)과 [통합 문서의 실행 출력](docs/code_walkthrough.html#executed-notebooks)에 있다.
“같은 손실 숫자”와 “같은 최소화 파라미터”를 구분한다.

## 출력과 검증 근거

'''
    for filename in sorted(path.name for path in (ROOT/'outputs').glob('*.png')):
        readme += f'- [{filename}](outputs/{filename})\n'
    readme += '''

[필수 수치](reports/metrics.json), [전체 실행](reports/experiment_run.txt), [32개 테스트](reports/test_revision.txt),
[4개 노트북 실행](reports/notebook_execution.txt), [우도 검산](reports/loss_likelihood_checks.json),
[산출물 검수](reports/artifact_verification.json), [브라우저 검수](reports/browser_verification.json)를 연결한다.
선택 과제는 [bonus_report.ipynb](notebooks/bonus_report.ipynb)와 [bonus_metrics.json](reports/bonus_metrics.json)으로 분리한다.
공개 이미지 출처·전처리·사용 범위는 [SOURCE.md](data/SOURCE.md)를 확인한다.

## PDF 해석과 제한

반경 요구는 .1, k=100의 유효값은64, 원형 .5는 정확한 수렴이다. 타원 .5는 실제 발산한다.
PDF의 y_true 빈칸과 참고 숫자 오류는 원래 입력·수식으로 보완하며 결과를 왜곡하지 않는다.
Momentum의 이점은 명시한 함수·lr·임계값 아래의 결과다. 수학 구현은 NumPy만 사용하고 eig는 비교 검증 전용이다.
과거 TDD·검증 기록은 그대로 보존하고 현재 실행 근거를 새 보고서에 기록한다. 원격 GitHub 제출은 이 작업 범위에 포함하지 않는다.
'''
    (ROOT/'README.md').write_text(readme, encoding='utf-8')


def supplementary_sections(metrics):
    """선택 과제·재현·PDF 대조·검증 가이드를 같은 파일의 순차 섹션으로 만든다."""
    bonus = json.loads((ROOT/'reports/bonus_metrics.json').read_text())
    body = ['<h2 id="bonus-learning">선택 과제 · 기본 구현에서 이어지는 학습</h2>'
            '<h3>Adam: 방향과 크기를 함께 누적하기</h3><p>Momentum은 과거 기울기로 이동 방향을 누적한다. '
            'Adam은 여기에 기울기 제곱의 이동평균을 더하여 좌표별 이동량을 조정한다. '
            '특징마다 수치 크기가 다른 상황에서 좌표별 조정이 도움이 될 수 있다. '
            '다만 이 실험에서는 같은 lr=.01의 Adam이 GD나 Momentum보다 느리다.</p>'
            '<pre class="equation">mₜ=β₁mₜ₋₁+(1−β₁)gₜ\nvₜ=β₂vₜ₋₁+(1−β₂)gₜ²\n'
            'm̂ₜ=mₜ/(1−β₁ᵗ), v̂ₜ=vₜ/(1−β₂ᵗ)\nθₜ₊₁=θₜ−lr m̂ₜ/(√v̂ₜ+ε)</pre>'
            '<p><a href="#src-bonus_optimizer-py">실제 Adam/Newton 코드</a> · '
            '<a href="#bonus_report-ipynb">실행된 보너스 노트북</a></p>']
    body.append(table(['알고리즘', '손실 .01 첫 도달', '관측 구간 내 유지 시작', '최종 손실'], [
        [label, row['first_update_loss_le_0.01'], row['first_sustained_update_loss_le_0.01'], row['final_loss']]
        for label, row in bonus['adam_comparison'].items()]))
    body.extend(image_markup(filename) for filename in ['bonus_adam_paths.png', 'bonus_adam_loss.png'])
    body.append('<h3>Newton: 기울기를 곡률로 보정하기</h3><p>Newton 방법은 Hessian이라는 2차 미분 행렬로 '
                '곡률까지 사용한다. 완만한 방향과 가파른 방향의 차이를 직접 보정한다. '
                '현재 이차함수의 Hessian은 diag(2,20)이며 H⁻¹g=(x,y)여서 전체 스텝이면 한 번에 원점에 도달한다. '
                '복잡한 모델에서는 Hessian 계산·저장·선형방정식 풀이 비용이 커지고 Hessian이 적절하지 않을 수도 있다.</p>'
                '<pre class="equation">θ_next=θ−solve(H,g)\nH=diag(2,20), g=(2x,20y)\n'
                'solve(H,g)=(x,y) → θ_next=(0,0)</pre>')
    body.extend(image_markup(filename) for filename in ['bonus_newton_paths.png', 'bonus_newton_loss.png'])
    info = bonus['information_theory']
    body.append('<h3>정보 이론: 불확실성과 분포의 차이</h3><p>엔트로피 H(p)는 실제 분포의 불확실성, '
                'KL(p‖q)는 모델 분포 q로 실제 p를 설명할 때 생기는 차이, 교차엔트로피 H(p,q)는 그 설명 비용이다. '
                '예를 들어 클릭/비클릭의 실제 확률이 [.3,.7]인데 모델이 [.6,.4]라면 아래 값을 얻는다. '
                '자연로그를 쓰므로 단위는 nats다.</p>'
                '<pre class="equation">H(p)=−Σp log p\nKL(p‖q)=Σp log(p/q)\n'
                'H(p,q)=−Σp log q=H(p)+KL(p‖q)</pre>')
    body.append(table(['H(p)', 'KL(p‖q)', 'H(p,q)'], [[info['entropy'], info['kl_divergence'], info['cross_entropy']]]))
    body.append('<p><a href="#src-bonus_probability-py">실제 정보 이론 코드</a> · '
                '<a href="../reports/bonus_metrics.json">선택 과제 수치 원본</a></p>'
                '<h2 id="reproduction">재현 방법과 설명 순서</h2>'
                '<p>프로젝트 A2-1 폴더에서 requirements.txt의 버전이 준비된 Python으로 실행한다. '
                '현재 검증 인터프리터는 conda py312의 Python 3.12다. 이번 작업에서는 기존 환경을 재사용했다.</p>'
                '<pre><code>python scripts/run_experiments.py --bonus &gt; reports/experiment_run.txt\n'
                'MPLCONFIGDIR=.cache/matplotlib python -m unittest discover -s tests -v &gt; reports/test_revision.txt 2&gt;&amp;1\n'
                'python scripts/run_notebooks.py --bonus &gt; reports/notebook_execution.txt\n'
                'python scripts/build_assessment.py\n'
                'python scripts/verify_artifacts.py\n'
                'node scripts/verify_answer_browser.cjs</code></pre>'
                '<p>추가 설명 문서는 이 HTML 하나다. 빌더는 README.md와 이 파일을 갱신한다. '
                '코드와 노트북을 수정했다면 빌더를 다시 실행해 내장 스냅샷을 갱신한다. '
                '브라우저 검수는 기존 로컬 Playwright와 Chrome을 사용하며 PLAYWRIGHT_MODULE·CHROME_PATH로 경로를 지정할 수 있다.</p>'
                '<ol class="steps"><li><strong>개념과 생활 예시</strong>평가 번호를 선택한 뒤 무엇을 계산하는지 먼저 말한다.</li>'
                '<li><strong>도식과 수식</strong>계산 순서를 따라가면서 행렬·벡터·스칼라 shape를 확인한다.</li>'
                '<li><strong>실제 코드</strong>링크를 눌러 같은 파일의 해당 줄로 이동하고 연산을 확인한다.</li>'
                '<li><strong>실험 결과</strong>입력·조건·오차·허용오차·판정과 그래프 축·범례를 함께 설명한다.</li>'
                '<li><strong>유도와 실행 증거</strong>노트북 부록의 수식 셀과 저장된 실제 출력으로 검산한다.</li></ol>'
                '<h2 id="requirements-check">PDF·두 평가 목록의 대조와 검증</h2>'
                '<p>PDF 1~8쪽의 텍스트와 수치 예시가 있는 3·4·7쪽 렌더를 확인했다. '
                '반경은 평가의 1보다 엄격한 PDF의 .1을 적용한다. 원형 lr=.5의 수렴과 타원 lr=.5의 발산은 별개 실험이다. '
                '64×64의 k=100 요청은 실제 64개이며 저장량 감소 여부와 복원 정확도를 구분한다. '
                'y_true 빈칸은 7쪽의 1로 채우고 참고 수치 오타는 원래 수식으로 재계산한다.</p>')
    body.append(table(['평가 번호', 'PDF 근거', '증거가 포함된 노트북', '실험 PNG'], [
        [item['id'], item['pdf'], item['notebook'], ', '.join(item['images']) or '실측 표·기호식·실행 출력'] for item in ITEMS]))
    body.append('<p>수학 구현은 NumPy, 시각화는 Matplotlib다. eig는 tests/scripts의 독립 비교에서만 사용하고 '
                'src에는 없다. 자동미분 프레임워크와 sklearn PCA·최적화는 사용하지 않는다. '
                '모든 함수·클래스의 Docstring, requirements 버전, seed=42, 64×64 입력 제약을 별도 검사했다. '
                '현재 32개 테스트, 4개 실행 노트북, 17개 PNG를 확인했다.</p>'
                '<p>코드 SHA-256과 모든 줄의 원문 일치를 검사하고, 문서의 내부 앵커와 원본 링크를 대조한다. '
                'diagram-design은 SVG 접근성·외부 실행 자원·도식 기하를 검사한다. '
                'Chrome에서는 1440px/390px 표시, 이미지 로드, 가로 넘침, 실제 코드 줄 이동을 확인한다. '
                '과거 TDD 기록은 보존하고 현재 상태의 보고서를 별도로 남겼다. 원격 push·GitHub 제출은 수행하지 않았다.</p>'
                '<p><a href="../reports/artifact_verification.json">현재 산출물 검수</a> · '
                '<a href="../reports/browser_verification.json">현재 브라우저 검수</a> · '
                '<a href="../reports/diagram_design_verification.json">도식 검수</a> · '
                '<a href="../reports/code_reference_manifest.json">코드 SHA-256</a> · '
                '<a href="../data/SOURCE.md">이미지 출처·전처리</a></p>')
    toc = '<a href="#bonus-learning">선택 과제 · Adam/Newton/정보 이론</a>'
    toc += '<a href="#reproduction">재현 방법과 설명 순서</a><a href="#requirements-check">PDF·평가 대조와 검증</a>'
    return ''.join(body), toc


def build_all():
    """README와 추가 학습용 HTML 하나에 모든 설명·코드·노트북을 통합한다."""
    metrics = json.loads((ROOT/'reports/metrics.json').read_text())
    update_readme(metrics)
    learning, toc = build_answer(metrics)
    supplementary, extra_toc = supplementary_sections(metrics)
    notebooks, notebook_toc = build_notebook_reference()
    source, source_toc = build_code_reference()
    page(ROOT/'docs/code_walkthrough.html', 'A2-1 · 개념·수식·실제 코드 통합 학습',
         learning + supplementary + notebooks + source,
         '<a href="#learning-start">전체 연결과 표기</a>' + toc + extra_toc
         + '<a href="#executed-notebooks">부록 1 · 실행 노트북</a>' + notebook_toc
         + '<a href="#source-code">부록 2 · 실제 코드 전체</a>' + source_toc)
    (ROOT/'reports/html_build.json').write_text(json.dumps({
        'file': 'docs/code_walkthrough.html', 'single_learning_document': True,
        'svg_count': 15, 'core_png_count': 13, 'total_embedded_png_count': 30,
        'integrated_code_files': 19, 'integrated_notebooks': 4,
        'sections_in_order': ['concepts_and_15_items', 'bonus', 'reproduction', 'requirements', 'notebook_outputs', 'actual_code'],
    }, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'document': 'docs/code_walkthrough.html', 'criteria': len(ITEMS),
                      'diagrams': len(ITEMS), 'integrated_code_files': 19, 'integrated_notebooks': 4},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    build_all()
