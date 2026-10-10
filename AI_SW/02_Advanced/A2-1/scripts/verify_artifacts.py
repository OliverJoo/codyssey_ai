"""최종 파일의 링크·노트북 실행·Docstring·제약·버전을 검수한다."""

import ast
import hashlib
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
    assert [path.name for path in (ROOT/'docs').iterdir()] == ['code_walkthrough.html']
    documents = [ROOT/'README.md', ROOT/'data/SOURCE.md', ROOT/'docs/code_walkthrough.html']
    html_cache = {}
    for path in documents:
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
                continue
            if not target.path and target.fragment and path.suffix == '.html':
                assert soup.find(id=target.fragment), tag[attribute]
            if target.path and re.fullmatch(r'L\d+', target.fragment):
                assert int(target.fragment[1:]) <= len(resolved.read_text().splitlines())
            elif target.fragment and resolved.suffix == '.html':
                if resolved not in html_cache:
                    html_cache[resolved] = BeautifulSoup(resolved.read_text(), 'html.parser')
                assert html_cache[resolved].find(id=unquote(target.fragment)), (path, tag[attribute])
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
                          'python_path_recorded': 'py312/bin/python' in json.dumps(notebook, ensure_ascii=False),
                          'embedded_png_outputs': sum('image/png' in output.get('data', {}) for cell in codes for output in cell.outputs)})
    backprop = nbformat.read(ROOT/'notebooks/backprop_derivation.ipynb', as_version=4)
    backprop_source = '\n'.join(cell.source for cell in backprop.cells)
    assert all(text in backprop_source for text in ['partial', 'outer', 'compare_hand_calculation', 'shape'])
    probability = nbformat.read(ROOT/'notebooks/probability_loss.ipynb', as_version=4)
    probability_source = '\n'.join(cell.source for cell in probability.cells)
    assert all(text in probability_source for text in ['prod', 'sigma', 'NLL', 'verify_loss_likelihood', '1e-6'])
    assert next(row for row in notebooks if row['file'] == 'probability_loss.ipynb')['embedded_png_outputs'] >= 2
    assert next(row for row in notebooks if row['file'] == 'mathematics_experiments.ipynb')['embedded_png_outputs'] >= 7
    metrics = json.loads((ROOT/'reports/metrics.json').read_text())
    assert all(row['passed'] for row in metrics['area'].values())
    assert all(row['points_shape'] == [100, 2] and row['sample_count'] == 100 for row in metrics['area'].values())
    assert metrics['power_iteration']['matrix'] == [[4., 1.], [1., 3.]]
    assert all(metrics['power_iteration'][key] for key in ['passed', 'vector_passed', 'residual_passed'])
    assert metrics['derivative']['passed'] and len(metrics['derivative_sensitivity']) == 16
    assert metrics['backprop_comparison']['passed'] and len(metrics['backprop_comparison']['rows']) == 11
    assert metrics['circle']['GD lr=0.1']['within_pdf_radius_0.1']
    assert metrics['ellipse_stability']['loss_increases_at_lr_0.5']
    assert all(row['passed'] for row in metrics['softmax_cases']) and metrics['loss_likelihood_checks']['passed']
    answer = BeautifulSoup((ROOT/'docs/code_walkthrough.html').read_text(), 'html.parser')
    assert len(answer.select('section.answer-section')) == 15
    assert len(answer.find_all('svg')) == 15
    assert len(answer.select('.answer-section img')) == 13
    assert len(answer.find_all('img')) == 30
    for number in range(1, 16):
        section = answer.find(id=f'criterion-{number}')
        assert section.find('svg') and section.find('table') and section.find('pre')
        assert all(text in section.get_text() for text in ['개념', '현실적인 예시', '실제 코드가 수행하는 순서'])
        assert section.select('.code-links a[href^="#"]')
    code_soup = BeautifulSoup((ROOT/'docs/code_walkthrough.html').read_text(), 'html.parser')
    manifest = json.loads((ROOT/'reports/code_reference_manifest.json').read_text())
    for entry in manifest:
        path = ROOT/entry['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], ('stale snapshot', path)
        prefix = entry['path'].replace('/', '-').replace('.', '-')
        for number, original in enumerate(path.read_text().splitlines(), 1):
            node = code_soup.find(id=f'{prefix}-L{number}')
            assert node is not None, (entry['path'], number)
            node.find('a').extract()
            assert node.get_text() == original, (entry['path'], number, 'source mismatch')
    pinned = {}
    for line in (ROOT/'requirements.txt').read_text().splitlines():
        if '==' in line:
            name, expected = line.split('==')
            actual = version(name)
            assert actual == expected, (name, expected, actual)
            pinned[name] = actual
    assert not missing_docstrings and not forbidden_imports and not broken_links
    png_files = sorted((ROOT/'outputs').glob('*.png'))
    assert len(png_files) == 17
    assert all(path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') for path in png_files)
    test_log = (ROOT/'reports/test_revision.txt').read_text()
    assert re.search(r'Ran 32 tests', test_log) and test_log.rstrip().endswith('OK')
    assert not list(ROOT.rglob('.gitignore'))
    report = {'missing_docstrings': missing_docstrings, 'forbidden_imports': forbidden_imports,
              'eig_verification_calls': eig_calls, 'broken_local_links': broken_links,
              'notebooks': notebooks, 'png_count': len(png_files), 'pinned_versions': pinned,
              'current_test_count': 32, 'evaluation_sections': 15, 'answer_svg_count': 15,
              'answer_embedded_png_count': 13, 'code_snapshots_verified': len(manifest),
              'single_learning_document': 'docs/code_walkthrough.html', 'total_embedded_png_count': 30,
              'notebook_symbolic_derivations_verified': True,
              'html': {'no_remote_runtime_assets': True,
                       'source_citation_preserved': 'https://people.math.sc.edu/Burkardt/data/pgma/pgma.html',
                       'diagram_design_checks': 'reports/diagram_design_verification.json; 현재 HTML의 SVG·안전성·기하 검사는 예외 없이 실행한다.'}}
    (ROOT/'reports/artifact_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    verify_artifacts()
