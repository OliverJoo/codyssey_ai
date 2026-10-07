"""Markdown을 자체 포함 HTML로 조립하고 도식은 diagram-design 규칙으로 다시 그린다.

financial-services 프로필, flowchart/UML/bar 참조를 적용했다. Mermaid의 관계는
유지하되 배치는 SVG로 직접 구성했다. 수식 변환기는 이 문서에서 사용하는 TeX
명령만 지원하며 알 수 없는 명령은 오류로 표시해 원문이 조용히 누락되지 않게 했다.
"""

import base64
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAPER, INK, MUTED, GOLD = '#f3f5f7', '#14213d', '#475569', '#a67c20'


class DocumentMath:
    """문서의 제한된 TeX 표현을 재귀적으로 읽어 네이티브 MathML로 옮긴다."""

    SYMBOLS = {
        'theta': 'θ', 'sigma': 'σ', 'lambda': 'λ', 'beta': 'β', 'epsilon': 'ε',
        'Sigma': 'Σ', 'pi': 'π', 'mu': 'μ', 'nabla': '∇', 'partial': '∂', 'eta': 'η',
        'sum': '∑', 'prod': '∏', 'mapsto': '↦', 'approx': '≈', 'Rightarrow': '⇒',
        'Vert': '‖', 'in': '∈', 'odot': '⊙', 'cdot': '·',
    }

    def __init__(self, formula):
        """TeX 명령과 문자 단위 토큰을 준비한다."""
        self.tokens = re.findall(r'\\[A-Za-z]+|\\.|[^\s]', formula)
        self.position = 0

    def group(self):
        """중괄호 그룹 또는 TeX의 단일 문자 인수를 읽는다."""
        if self.position >= len(self.tokens):
            raise ValueError('수식 인수가 부족하다.')
        if self.tokens[self.position] == '{':
            self.position += 1
            result = self.sequence('}')
            if self.position >= len(self.tokens) or self.tokens[self.position] != '}':
                raise ValueError('수식 중괄호가 닫히지 않았다.')
            self.position += 1
            return result
        return self.atom(single=True)

    def text_group(self):
        """mathrm 등의 텍스트 인수를 읽는다."""
        if self.tokens[self.position] != '{':
            token = self.tokens[self.position]
            self.position += 1
            return token
        self.position += 1
        parts = []
        while self.tokens[self.position] != '}':
            token = self.tokens[self.position]
            parts.append(' ' if token == '\\ ' else token)
            self.position += 1
        self.position += 1
        return ''.join(parts)

    def atom(self, single=False):
        """기호·숫자·분수·제곱근·강조 명령 하나를 MathML로 바꾼다."""
        token = self.tokens[self.position]
        self.position += 1
        if token == '{':
            self.position -= 1
            return self.group()
        if token.startswith('\\'):
            command = token[1:]
            if command == 'frac':
                numerator, denominator = self.group(), self.group()
                return f'<mfrac>{numerator}{denominator}</mfrac>'
            if command == 'sqrt':
                return f'<msqrt>{self.group()}</msqrt>'
            if command == 'hat':
                return f'<mover>{self.group()}<mo>ˆ</mo></mover>'
            if command in ['mathrm', 'operatorname', 'mathcal']:
                if command == 'operatorname' and self.tokens[self.position] == '*':
                    self.position += 1
                value = html.escape(self.text_group())
                variant = 'script' if command == 'mathcal' else 'normal'
                return f'<mi mathvariant="{variant}">{value}</mi>'
            if command in ['left', 'right']:
                return ''
            if command in ['quad', 'qquad', ',', ';', ' ']:
                return '<mspace width="0.5em"/>'
            if command in ['ln', 'exp', 'cos', 'sin', 'max', 'det']:
                return f'<mi mathvariant="normal">{command}</mi>'
            if command in self.SYMBOLS:
                return f'<mo>{self.SYMBOLS[command]}</mo>'
            if command in ['{', '}', '|']:
                return f'<mo>{html.escape(command)}</mo>'
            raise ValueError(f'지원하지 않는 문서 수식 명령: {token}')
        if token.isdigit() or token == '.':
            number = token
            if not single:
                while self.position < len(self.tokens) and (
                        self.tokens[self.position].isdigit() or self.tokens[self.position] == '.'):
                    number += self.tokens[self.position]
                    self.position += 1
            return f'<mn>{number}</mn>'
        tag = 'mi' if token.isalpha() else 'mo'
        return f'<{tag}>{html.escape(token)}</{tag}>'

    def sequence(self, stop=None):
        """항들을 읽고 위·아래 첨자를 원래 항에 붙인다."""
        parts = []
        while self.position < len(self.tokens) and self.tokens[self.position] != stop:
            item = self.atom()
            subscript, superscript = None, None
            while self.position < len(self.tokens) and self.tokens[self.position] in ['_', '^']:
                kind = self.tokens[self.position]
                self.position += 1
                if kind == '_':
                    subscript = self.group()
                else:
                    superscript = self.group()
            if subscript is not None and superscript is not None:
                item = f'<msubsup>{item}{subscript}{superscript}</msubsup>'
            elif subscript is not None:
                item = f'<msub>{item}{subscript}</msub>'
            elif superscript is not None:
                item = f'<msup>{item}{superscript}</msup>'
            parts.append(item)
        return '<mrow>' + ''.join(parts) + '</mrow>'


def math_markup(formula, display=False):
    """원문 TeX를 주석으로 보존한 접근 가능한 MathML 수식을 만든다."""
    body = DocumentMath(formula).sequence()
    mode = 'block' if display else 'inline'
    math = (f'<math xmlns="http://www.w3.org/1998/Math/MathML" display="{mode}" '
            f'aria-label="{html.escape(formula, quote=True)}"><semantics>{body}'
            f'<annotation encoding="application/x-tex">{html.escape(formula)}</annotation>'
            '</semantics></math>')
    return f'<div class="formula">{math}</div>' if display else math


def svg_frame(slug, title, description, body, wide=False):
    """title/desc를 첫 자식으로 둔 doc-inline/wide 접근 가능 SVG를 만든다."""
    width, height = (1280, 720) if wide else (960, 600)
    return (f'<figure class="diagram"><svg viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="{slug}-title {slug}-desc">'
            f'<title id="{slug}-title">{html.escape(title)}</title>'
            f'<desc id="{slug}-desc">{html.escape(description)}</desc>'
            f'<defs><marker id="{slug}-arrow" markerWidth="8" markerHeight="8" '
            'refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="#475569"/></marker>'
            f'<marker id="{slug}-inherit" markerWidth="16" markerHeight="16" refX="16" '
            f'refY="8" orient="auto"><path d="M0 0 L16 8 L0 16 Z" fill="{PAPER}" '
            f'stroke="{INK}"/></marker></defs>{body}</svg>'
            f'<figcaption>{html.escape(description)}</figcaption></figure>')


def svg_text(x, y, value, size=20, anchor='middle', color=INK, mono=False):
    """네이비/슬레이트 테마의 SVG 텍스트를 안전하게 생성한다."""
    family = 'Geist Mono, monospace' if mono else 'Geist, Noto Sans KR, Apple SD Gothic Neo, sans-serif'
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}">{html.escape(value)}</text>')


def svg_node(x, y, w, h, lines, focal=False, rounded=8):
    """읽기 쉬운 다중 행 레이블을 가진 노드를 만든다."""
    fill, stroke = ('#f4eddf', GOLD) if focal else ('#ffffff', INK)
    result = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rounded}" fill="{fill}" stroke="{stroke}"/>'
    start = y + h / 2 - (len(lines) - 1) * 16 + 8
    for index, line in enumerate(lines):
        result += svg_text(x + w / 2, start + index * 32, line,
                           size=20 if index == 0 else 16, color=INK if index == 0 else MUTED)
    return result


def workflow_svg(slug):
    """Mermaid의 6개 작업 단계와 5개 관계를 세 행 흐름으로 다시 그린다."""
    labels = [('PDF 기준 정리', 'requirements'), ('테스트 작성 · Red', 'expected behavior'),
              ('NumPy 구현', 'mathematical code'), ('검증 · Green', '27 tests'),
              ('노트북 · PNG 실행', 'py312 / outputs'), ('PDF 재검토 · 문서', 'review / explanation')]
    positions = [(56, 72), (528, 72), (56, 232), (528, 232), (56, 392), (528, 392)]
    paths = ['M432 116 H528', 'M716 160 V184 Q716 192 708 192 H252 Q244 192 244 200 V232',
             'M432 276 H528', 'M716 320 V344 Q716 352 708 352 H252 Q244 352 244 360 V392',
             'M432 436 H528']
    body = ''.join(f'<path d="{path}" fill="none" stroke="{MUTED}" marker-end="url(#{slug}-arrow)"/>' for path in paths)
    for i, ((x, y), label) in enumerate(zip(positions, labels)):
        body += svg_node(x, y, 376, 88, label, focal=(i == 3), rounded=20 if i in [0, 5] else 8)
    body += f'<line x1="40" y1="540" x2="920" y2="540" stroke="#b8c2cf"/>'
    body += svg_text(40, 568, '화살표: 작업 순서 · 실패/통과의 근거는 실행 로그', 16, 'start', MUTED)
    return svg_frame(slug, '요구사항에서 검증·설명까지', 'PDF 기준을 테스트로 바꾸고 구현·실행 후 요구사항을 다시 검토한 여섯 단계.', body)


def network_svg(slug, backward=False):
    """순전파 6개 또는 역전파 7개 노드의 관계와 실제 shape/값을 표시한다."""
    if backward:
        labels = [('손실 L', 'BCE', 'scalar ()'), ('dL / dy_pred', '-1.5449', 'scalar ()'),
                  ('dL / dz2', '-0.3527', 'scalar ()'), ('dL / da1', '[-.1764,-.2116]', 'shape (2,)'),
                  ('dL / dz1', '[-.0440,-.0517]', 'shape (2,)'), ('dL / dW1', 'outer(dz1, x)', 'shape (2,2)')]
    else:
        labels = [('입력 x · 2개', '[1, 0]', 'shape (2,)'), ('z1 = W1 x + b1', '[.1000, .3000]', 'shape (2,)'),
                  ('a1 = sigmoid z1', '[.5250, .5744]', 'shape (2,)'), ('z2 = W2 a1 + b2', '.6072', 'scalar ()'),
                  ('y_pred = sigmoid z2', '.6473', 'scalar ()'), ('BCE 손실 L', '.4350, y_true=1', 'scalar ()')]
    body = svg_text(56, 88, '연쇄 법칙: 출력에서 입력 방향의 미분' if backward else '고정 예제: 입력 2 → 은닉 2 → 출력 1', 28, 'start')
    for i in range(5):
        body += (f'<path d="M{224 + i*200} 288 H{256 + i*200}" fill="none" '
                 f'stroke="{MUTED}" marker-end="url(#{slug}-arrow)"/>')
    if backward:
        body += f'<path d="M540 352 V432" fill="none" stroke="{MUTED}" marker-end="url(#{slug}-arrow)"/>'
    for i, label in enumerate(labels):
        # 수식이 긴 레이블은 두 줄로 나누어 글자 크기를 줄이지 않았다.
        result = f'<rect x="{56+i*200}" y="224" width="168" height="128" rx="8" fill="{("#f4eddf" if i == 2 else "#fff")}" stroke="{GOLD if i == 2 else INK}"/>'
        for j, line in enumerate(label):
            if not backward and j == 0 and i in [1, 2, 3, 4]:
                first, second = line.split(' = ', 1)
                result += svg_text(140+i*200, 248, first, 20)
                result += svg_text(140+i*200, 272, '= '+second, 12)
            else:
                result += svg_text(140+i*200, 260+j*32, line, 16 if j < 2 else 12, color=INK if j == 0 else MUTED)
        body += result
    if backward:
        body += svg_node(456, 432, 168, 112, ['dL / dW2', 'dz2 * a1', 'shape (2,)'])
    body += '<line x1="40" y1="660" x2="1240" y2="660" stroke="#b8c2cf"/>'
    body += svg_text(40, 692, '화살표: 값 또는 미분 계산의 의존 순서 · 표의 숫자는 표시 시점에만 반올림', 16, 'start', MUTED)
    return svg_frame(slug, '여섯 필수 미분의 계산 순서' if backward else '고정 신경망의 순전파',
                     '손실에서 입력 가중치까지 미분을 연결하고 출력 가중치 미분은 dz2에서 분기한다.' if backward
                     else '두 입력을 은닉층과 출력층에 통과시켜 예측 .6473과 BCE .4350을 계산한다.', body, wide=True)


def class_box(x, y, w, name, attributes, operations, focal=False):
    """실제 코드의 클래스 이름·속성·동작을 UML 구획으로 표시한다."""
    height = 52 + len(attributes) * 24 + 16 + len(operations) * 24 + 16
    fill, stroke = ('#f4eddf', GOLD) if focal else ('#ffffff', INK)
    result = f'<rect x="{x}" y="{y}" width="{w}" height="{height}" rx="8" fill="{fill}" stroke="{stroke}"/>'
    result += svg_text(x+w/2, y+32, name, 20)
    result += f'<line x1="{x}" y1="{y+52}" x2="{x+w}" y2="{y+52}" stroke="#b8c2cf"/>'
    for i, label in enumerate(attributes):
        result += svg_text(x+16, y+76+i*24, label, 16, 'start', MUTED, mono=True)
    separator = y+52+len(attributes)*24+16
    result += f'<line x1="{x}" y1="{separator}" x2="{x+w}" y2="{separator}" stroke="#b8c2cf"/>'
    for i, label in enumerate(operations):
        result += svg_text(x+16, separator+24+i*24, label, 16, 'start', INK, mono=True)
    return result


def uml_svg(slug):
    """Mermaid의 6개 클래스와 4개 상속 관계를 그대로 보존한다."""
    body = ''
    # 자식에서 부모를 향하는 빈 삼각형: 네 개 상속 관계에 서로 다른 접점을 사용했다.
    for path in ['M212 272 V188', 'M580 272 V240 Q580 232 572 232 H308 Q300 232 300 224 V188',
                 'M212 480 V428', 'M1044 360 V212']:
        body += f'<path d="{path}" fill="none" stroke="{INK}" marker-end="url(#{slug}-inherit)"/>'
    body += class_box(56, 56, 312, 'VanillaGD', ['+ lr: float'], ['+ step(point, gradient)'])
    body += class_box(56, 272, 312, 'Momentum', ['+ beta: float', '+ velocity: array'], ['+ step(point, gradient)'])
    body += class_box(400, 272, 360, 'NewtonMethod', ['+ hessian_function'], ['+ step(point, gradient)'])
    body += class_box(56, 480, 312, 'Adam', ['+ second_moment: array', '+ t: int'], ['+ step(point, gradient)'], focal=True)
    body += class_box(864, 56, 360, 'ProbabilityLoss', [], ['+ normal_pdf(x, mean, var)', '+ bernoulli_pmf(x, p)', '+ softmax(logits)'])
    body += class_box(864, 360, 360, 'InformationTheory', [], ['+ entropy(p)', '+ kl_divergence(p, q)', '+ cross_entropy(p, q)'])
    body += '<line x1="40" y1="660" x2="1240" y2="660" stroke="#b8c2cf"/>'
    legend = [('상속', ''), ('실체화', 'dashed'), ('합성', 'filled'), ('집합', 'hollow'), ('연관', 'open'), ('의존', 'dependency')]
    for i, (label, style) in enumerate(legend):
        x = 40 + i * 200
        dash = ' stroke-dasharray="4 4"' if style in ['dashed', 'dependency'] else ''
        body += f'<path d="M{x} 688 H{x+40}" fill="none" stroke="{INK}"{dash}/>'
        if style in ['', 'dashed']:
            body += f'<path d="M{x+28} 680 L{x+44} 688 L{x+28} 696 Z" fill="{PAPER}" stroke="{INK}"/>'
        elif style in ['filled', 'hollow']:
            body += f'<path d="M{x+20} 688 L{x+32} 680 L{x+44} 688 L{x+32} 696 Z" fill="{INK if style == "filled" else PAPER}" stroke="{INK}"/>'
        else:
            body += f'<path d="M{x+32} 680 L{x+44} 688 L{x+32} 696" fill="none" stroke="{INK}"/>'
        body += svg_text(x+56, 692, label, 16, 'start', MUTED)
    return svg_frame(slug, '필수 클래스와 보너스 상속',
                     'Adam은 Momentum, Newton은 VanillaGD, 정보 이론은 ProbabilityLoss를 상속한다. 본문의 네 관계는 상속이며 아래 범례는 UML 관계 문법이다.', body, wide=True)


def speed_svg(slug):
    """보너스 JSON의 실측 첫 도달 횟수를 0부터 시작하는 공통 축에 표시한다."""
    metrics = json.loads((ROOT / 'reports' / 'bonus_metrics.json').read_text())
    data = [(name.split()[0], item['first_update_loss_le_0.01'])
            for name, item in metrics['adam_comparison'].items()]
    data.append(('Newton', metrics['newton_comparison']['Newton']['first_update_loss_le_0.01']))
    body = svg_text(80, 40, '손실 .01 이하에 처음 도달한 업데이트 수', 24, 'start')
    for value in range(0, 1501, 300):
        y = 472 - value / 1500 * 400
        body += f'<line x1="112" y1="{y}" x2="896" y2="{y}" stroke="#b8c2cf" stroke-opacity=".5"/>'
        body += svg_text(96, y+4, str(value), 16, 'end', MUTED, mono=True)
    for index, (name, value) in enumerate(data):
        x = 144 + index * 184
        height = value / 1500 * 400
        y = 472 - height
        body += f'<rect x="{x}" y="{y}" width="120" height="{height}" fill="{GOLD if name == "Momentum" else "#cbd2da"}" stroke="{INK}"/>'
        body += svg_text(x+60, y-12, str(value), 20, color=INK, mono=True)
        body += svg_text(x+60, 512, name, 20)
    body += '<line x1="40" y1="540" x2="920" y2="540" stroke="#b8c2cf"/>'
    body += svg_text(40, 568, '타원 (5,5) · GD/Momentum/Adam lr=.01 · Newton은 Hessian을 사용한 전체 스텝', 16, 'start', MUTED)
    return svg_frame(slug, '동일 함수의 실제 수렴 속도 비교',
                     '같은 타원 함수에서 최초 도달 횟수는 GD 194, Momentum 78, Adam 1242, Newton 1이다. 최초 도달 뒤 손실이 다시 증가할 수 있다.', body)


def mermaid_markup(source, slug):
    """해당 Markdown에 있는 알려진 도식만 대응시켜 의미 누락을 막는다."""
    if source.startswith('classDiagram'):
        return uml_svg(slug)
    if 'PDF 기준 정리' in source:
        return workflow_svg(slug)
    if '입력 x · 2개' in source:
        return network_svg(slug)
    if 'dL / dy_pred' in source:
        return network_svg(slug, backward=True)
    raise ValueError('새 Mermaid 도식은 레이아웃과 원문 관계를 먼저 검토해야 한다.')


def render_markdown(path, output, prefix):
    """원문·수식·도식을 변환하고 로컬 링크와 이미지 경로를 출력 위치에 맞춘다."""
    source = path.read_text(encoding='utf-8')
    blocks = []

    def stash(fragment):
        """Markdown 변환 중 SVG/MathML을 보존할 고유 토큰을 만든다."""
        blocks.append(fragment)
        return f'HTMLBLOCK{len(blocks)-1}END'

    def diagram(match):
        """Mermaid 원문을 검토된 SVG 레이아웃에 연결한다."""
        return '\n\n' + stash(mermaid_markup(match.group(1), f'{prefix}-diagram-{len(blocks)}')) + '\n\n'

    source = re.sub(r'```mermaid\n(.*?)\n```', diagram, source, flags=re.S)
    source = re.sub(r'\$\$(.*?)\$\$', lambda m: '\n\n' + stash(math_markup(m.group(1), True)) + '\n\n', source, flags=re.S)
    source = re.sub(r'(?<!\$)\$([^$\n]+)\$(?!\$)', lambda m: stash(math_markup(m.group(1))), source)
    rendered = markdown.markdown(source, extensions=['tables', 'fenced_code', 'sane_lists'])
    for i, fragment in enumerate(blocks):
        token = f'HTMLBLOCK{i}END'
        rendered = rendered.replace(f'<p>{token}</p>', fragment).replace(token, fragment)
    soup = BeautifulSoup(rendered, 'html.parser')
    for heading in soup.find_all(re.compile('^h[1-6]$')):
        label = heading.get_text(' ', strip=True)
        slug = re.sub(r'[^\w가-힣-]', '', label.lower().replace(' ', '-'))
        heading['id'] = prefix + '-' + slug
    for image in soup.find_all('img'):
        image_path = (path.parent / unquote(image['src'])).resolve()
        image['src'] = 'data:image/png;base64,' + base64.b64encode(image_path.read_bytes()).decode()
        image['loading'] = 'lazy'
    for link in soup.find_all('a', href=True):
        target = urlsplit(link['href'])
        if target.scheme or not target.path:
            continue
        absolute = (path.parent / unquote(target.path)).resolve()
        if not absolute.is_relative_to(ROOT):
            raise ValueError('문서의 로컬 링크가 A2-1 범위 밖을 가리킨다.')
        relative = Path(os.path.relpath(absolute, output.parent)).as_posix()
        link['href'] = relative + ('#' + target.fragment if target.fragment else '')
    for table in list(soup.find_all('table')):
        wrapper = soup.new_tag('div', attrs={'class': 'table-scroll', 'tabindex': '0'})
        table.wrap(wrapper)
    return str(soup)


CSS = '''
:root{--paper:#f3f5f7;--paper2:#e7ebf0;--ink:#14213d;--muted:#475569;--rule:#b8c2cf;--gold:#a67c20}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:32px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:Geist,'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;font-size:17px;line-height:1.85}
a{color:#1d4ed8;text-decoration-thickness:1px;text-underline-offset:4px}a:hover{color:var(--ink)}
.top{border-bottom:1px solid var(--rule);padding:20px 4vw;display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap}
.eyebrow{font-family:'Geist Mono',monospace;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.top strong{font-size:20px}.top .links{display:flex;gap:24px;flex-wrap:wrap;font-size:15px}
.layout{max-width:1536px;margin:auto;display:grid;grid-template-columns:240px minmax(0,1fr);gap:48px;padding:40px 32px}
aside{position:sticky;top:24px;height:calc(100vh - 48px);overflow:auto;font-size:14px;border-right:1px solid var(--rule);padding-right:20px}
aside a{display:block;margin:12px 0;text-decoration:none;color:var(--muted);line-height:1.5}aside a:hover{color:var(--ink)}
main{min-width:0}article{margin-bottom:80px}h1{font-family:'Instrument Serif',Georgia,'Apple SD Gothic Neo',serif;font-size:clamp(32px,4vw,48px);font-weight:500;line-height:1.3;margin:8px 0 32px;word-break:keep-all}
h2{font-size:28px;line-height:1.45;border-top:1px solid var(--rule);padding-top:32px;margin-top:56px;word-break:keep-all}h3{font-size:22px;line-height:1.5;margin-top:40px;word-break:keep-all}
p{margin:20px 0}li{margin:6px 0}strong{font-weight:650}code,pre{font-family:'Geist Mono',Menlo,monospace;font-size:.87em}
code{background:var(--paper2);padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}pre{background:#e7ebf0;border:1px solid var(--rule);border-radius:6px;padding:20px;overflow:auto;line-height:1.7}pre code{background:none;padding:0;overflow-wrap:normal}
table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.65;min-width:600px}th,td{text-align:left;vertical-align:top;padding:14px 16px;border-bottom:1px solid var(--rule)}th{background:var(--paper2);font-weight:650}td:first-child{font-weight:550}
.table-scroll{overflow-x:auto;max-width:100%;margin:28px 0}.table-scroll:focus-visible,.diagram:focus-visible{outline:2px solid var(--gold)}
img{display:block;max-width:100%;height:auto;background:#fff;border:1px solid var(--rule);margin:32px auto}
.diagram{margin:40px 0;overflow-x:auto;max-width:100%}.diagram svg{display:block;width:100%;min-width:760px;height:auto}.diagram figcaption{font-size:14px;color:var(--muted);margin-top:16px;min-width:0}
.formula{overflow-x:auto;max-width:100%;padding:20px 16px;margin:28px 0;background:#fff;border-left:3px solid var(--gold)}math{font-size:1.15em}math[display=block]{margin:0;min-width:max-content}annotation{display:none}
.source-title{color:var(--muted);font-size:14px}.status{border-bottom:1px solid var(--rule);padding:12px 0;display:flex;gap:24px;flex-wrap:wrap;color:var(--muted);font-size:14px}.status b{color:var(--ink)}
footer{border-top:1px solid var(--rule);padding:24px 32px;color:var(--muted);font-size:13px}
@media(max-width:900px){.layout{display:block;padding:24px 20px}aside{position:static;height:auto;border-right:none;border-bottom:1px solid var(--rule);padding:0 0 20px;margin-bottom:32px}aside details{max-height:360px;overflow:auto}h2{font-size:24px}h3{font-size:20px}.top{padding:16px 20px}.formula{padding:16px 12px}body{font-size:16px}.diagram svg{min-width:760px}}
@media print{body{background:#fff;font-size:11pt}.top,aside{display:none}.layout{display:block;padding:0}.diagram svg{min-width:0}a{color:var(--ink)}pre,.formula,.diagram,table{break-inside:avoid}h2,h3{break-after:avoid}.table-scroll{overflow:visible}table{min-width:0;font-size:10pt}footer{font-size:9pt}}
'''


def build_document(output, sources, title):
    """소스별 링크를 유지한 문서, 목차, 오프라인 도식을 한 HTML에 저장한다."""
    articles = []
    for prefix, path in sources:
        body = render_markdown(path, output, prefix)
        if prefix != 'walkthrough' and len(sources) > 1:
            body = body.replace('<h1 ', '<h2 ').replace('</h1>', '</h2>')
        relative = Path(os.path.relpath(path, output.parent)).as_posix()
        articles.append(f'<article><p class="source-title">문서 원본: <a href="{relative}">{path.name}</a></p>{body}</article>')
    content = ''.join(articles)
    if len(sources) > 1:
        content += '<h2 id="measured-speed">보너스 속도 비교 도식</h2>' + speed_svg('measured-speed')
    soup = BeautifulSoup(content, 'html.parser')
    toc = ''.join(f'<a href="#{node["id"]}">{html.escape(node.get_text(" ", strip=True))}</a>' for node in soup.find_all('h2'))
    output.write_text(f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A2-1 AI 수학: 개념, 수식, 실제 코드와 검증 결과"><title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><header class="top"><strong>A2-1 · AI 수학 구현</strong><nav class="links" aria-label="문서 이동"><a href="{os.path.relpath(ROOT/'README.html',output.parent)}">README HTML</a><a href="{os.path.relpath(ROOT/'docs/code_walkthrough.html',output.parent)}">통합 설명 HTML</a></nav></header>
<div class="layout"><aside aria-label="문서 목차"><details open><summary>목차</summary>{toc}</details></aside><main>
<p class="eyebrow">NUMPY / PY312 / TDD</p><div class="status"><span><b>27</b> tests passed</span><span><b>3</b> notebooks executed</span><span><b>15</b> PNG outputs</span></div>
{content}</main></div><footer>financial-services · diagram-design · SVG + MathML + PNG 내장 · 네트워크 없이 표시<br>
폰트는 로컬 Geist/Instrument Serif가 있으면 사용하며, 없으면 Apple SD Gothic Neo/Georgia/Menlo 등의 시스템 폰트로 표시한다. 외부 폰트·스크립트를 내려받지 않는다.</footer></body></html>''', encoding='utf-8')
    return {'file': str(output.relative_to(ROOT)), 'source_files': [str(p.relative_to(ROOT)) for _, p in sources],
            'svg_count': len(soup.find_all('svg')), 'math_count': len(soup.find_all('math')),
            'embedded_png_count': len(soup.find_all('img'))}


def build_all():
    """README 전용 HTML과 설명·README·재검토 통합 HTML을 재생성한다."""
    results = [build_document(ROOT/'README.html', [('readme', ROOT/'README.md')], 'A2-1 README'),
               build_document(ROOT/'docs/code_walkthrough.html', [
                   ('walkthrough', ROOT/'docs/code_walkthrough.md'),
                   ('readme', ROOT/'README.md'), ('review', ROOT/'docs/requirements_review.md')],
                   'A2-1 개념·코드·실행·요구사항 통합 설명')]
    (ROOT/'reports/html_build.json').write_text(json.dumps(results, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    build_all()
