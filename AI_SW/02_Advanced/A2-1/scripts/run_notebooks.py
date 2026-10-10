"""현재 py312 인터프리터의 커널로 노트북을 실행하고 출력을 저장한다."""

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for variable, directory in {
    'MPLCONFIGDIR': 'matplotlib', 'IPYTHONDIR': 'ipython',
    'JUPYTER_RUNTIME_DIR': 'jupyter', 'XDG_CACHE_HOME': 'xdg', 'TMPDIR': 'tmp',
}.items():
    path = ROOT / '.cache' / directory
    path.mkdir(parents=True, exist_ok=True)
    os.environ[variable] = str(path)

import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager


def run_notebooks(include_bonus=False):
    """필수 두 노트북과 수학 실험 증거, 선택 시 보너스 노트북을 실행한다."""
    kernel_root = ROOT / '.cache' / 'kernels'
    kernel_dir = kernel_root / 'py312-local'
    kernel_dir.mkdir(parents=True, exist_ok=True)
    (kernel_dir / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'Python (py312)', 'language': 'python',
    }), encoding='utf-8')
    names = ['backprop_derivation.ipynb', 'probability_loss.ipynb', 'mathematics_experiments.ipynb']
    if include_bonus:
        names.append('bonus_report.ipynb')
    for name in names:
        path = ROOT / 'notebooks' / name
        notebook = nbformat.read(path, as_version=4)
        client = NotebookClient(notebook, timeout=180, kernel_name='py312-local',
                                resources={'metadata': {'path': str(ROOT)}})
        client.create_kernel_manager()
        client.km.kernel_spec_manager = KernelSpecManager(kernel_dirs=[str(kernel_root)])
        client.execute()
        nbformat.write(notebook, path)
        print(f'Executed: {name} with {sys.executable}')


if __name__ == '__main__':
    run_notebooks(include_bonus='--bonus' in sys.argv)
