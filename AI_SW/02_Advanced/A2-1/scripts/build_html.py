"""통합 HTML의 CSS·MathML 도구. 실행하면 단일 학습 문서 빌더로 연결한다."""

import html
import re

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


CSS = '''
:root{--paper:#f3f5f7;--paper2:#e7ebf0;--ink:#14213d;--muted:#475569;--rule:#b8c2cf;--gold:#a67c20}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:32px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:Geist,'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;font-size:17px;line-height:1.85;overflow-wrap:anywhere}
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


def build_all():
    """추가 파일을 만들지 않고 README와 code_walkthrough.html만 재생성한다."""
    from build_assessment import build_all as build_walkthrough
    build_walkthrough()


if __name__ == '__main__':
    build_all()
