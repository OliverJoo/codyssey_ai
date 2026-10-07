"""최종 파일의 링크·노트북 실행·Docstring·제약·버전을 검수한다."""

import ast
from importlib.metadata import version
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import markdown
from bs4 import BeautifulSoup
import nbformat

ROOT = Path(__file__).resolve().parents[1]


def verify_artifacts():
    """PDF 수치 테스트와 별도로 산출물의 재현·탐색 가능성을 확인한다."""
    missing_docstrings, forbidden_imports, eig_calls = [], [], []
    python_files = list((ROOT/'src').glob('*.py')) + list((ROOT/'scripts').glob('*.py')) + list((ROOT/'tests').glob('*.py'))
    for path in python_files:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and not ast.get_docstring(node):
                missing_docstrings.append(f'{path.relative_to(ROOT)}:{node.lineno}:{node.name}')
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or '']
            else:
                names = []
            for name in names:
                if name.split('.')[0] in ['torch', 'tensorflow', 'jax', 'sklearn']:
                    forbidden_imports.append(f'{path.relative_to(ROOT)}:{node.lineno}:{name}')
            if isinstance(node, ast.Call) and ast.unparse(node.func) == 'np.linalg.eig':
                eig_calls.append(f'{path.relative_to(ROOT)}:{node.lineno}')
                assert path.parent.name in ['tests', 'scripts']
    broken_links = []
    for path in [ROOT/'README.md', ROOT/'docs/code_walkthrough.md', ROOT/'docs/requirements_review.md',
                 ROOT/'data/SOURCE.md', ROOT/'README.html', ROOT/'docs/code_walkthrough.html']:
        content = path.read_text()
        if path.suffix == '.md':
            content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        soup = BeautifulSoup(content, 'html.parser')
        ids = [tag['id'] for tag in soup.find_all(id=True)]
        assert len(ids) == len(set(ids)), f'중복 ID: {path}'
        for tag, attribute in [(tag, 'href') for tag in soup.find_all('a', href=True)] + [
                (tag, 'src') for tag in soup.find_all('img', src=True)]:
            target = urlsplit(tag[attribute])
            if target.scheme:
                continue
            resolved = (path.parent/unquote(target.path)).resolve() if target.path else path
            if not resolved.exists():
                broken_links.append(f'{path.relative_to(ROOT)} -> {tag[attribute]}')
            if not target.path and target.fragment and path.suffix == '.html':
                assert soup.find(id=target.fragment), tag[attribute]
            if target.path and re.fullmatch(r'L\d+', target.fragment):
                assert int(target.fragment[1:]) <= len(resolved.read_text().splitlines())
        if path.suffix == '.html':
            assert not soup.find_all('script')
            assert not soup.find_all('link', rel='stylesheet')
            assert all(tag['src'].startswith('data:') for tag in soup.find_all('img'))
            assert not soup.find_all(['iframe', 'object', 'embed'])
            for svg in soup.find_all('svg'):
                children = [child for child in svg.children if getattr(child, 'name', None)]
                assert children[0].name == 'title'
                assert svg.get('role') == 'img'
                assert all(soup.find(id=id_) for id_ in svg['aria-labelledby'].split())
    notebooks = []
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        codes = [cell for cell in notebook.cells if cell.cell_type == 'code']
        assert all(cell.execution_count is not None for cell in codes)
        assert not any(output.output_type == 'error' for cell in codes for output in cell.outputs)
        assert 'np.random.seed(42)' in '\n'.join(cell.source for cell in codes)
        notebooks.append({'file':path.name,'executed_code_cells':len(codes),
                          'python_path_recorded': 'py312/bin/python' in json.dumps(notebook, ensure_ascii=False)})
    pinned = {}
    for line in (ROOT/'requirements.txt').read_text().splitlines():
        if '==' in line:
            name, expected = line.split('==')
            actual = version(name)
            assert actual == expected, (name, expected, actual)
            pinned[name] = actual
    assert not missing_docstrings and not forbidden_imports and not broken_links
    assert len(list((ROOT/'outputs').glob('*.png'))) == 15
    assert not list(ROOT.rglob('.gitignore'))
    report = {'missing_docstrings': missing_docstrings, 'forbidden_imports': forbidden_imports,
              'eig_verification_calls': eig_calls, 'broken_local_links': broken_links,
              'notebooks': notebooks, 'png_count': 15, 'pinned_versions': pinned,
              'html': {'no_remote_runtime_assets': True,
                       'source_citation_preserved': 'https://people.math.sc.edu/Burkardt/data/pgma/pgma.html',
                       'diagram_design_self_check_exception': 'remote reference on <a>: 공개 이미지 출처를 위한 일반 인용 링크. 외부 실행 자원이 아니며 원문 보존을 위해 유지했다.'}}
    (ROOT/'reports/artifact_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    verify_artifacts()
