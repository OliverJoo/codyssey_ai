"""공개 P2 흑백 이미지에서 8픽셀 간격으로 뽑은 64×64 배열을 준비한다."""

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load_ascii_pgm(path):
    """P2 헤더, 주석, 최대 회색값을 읽고 NumPy로 [0,1] 배열을 만든다."""
    lines = Path(path).read_text(encoding='ascii').splitlines()
    tokens = ' '.join(line.split('#', 1)[0] for line in lines).split()
    if tokens[0] != 'P2':
        raise ValueError('ASCII PGM(P2) 파일이어야 한다.')
    width, height, maximum = map(int, tokens[1:4])
    pixels = np.array(tokens[4:], dtype=float).reshape(height, width)
    return pixels / maximum


def prepare_image():
    """원본을 보존하고 실제 실험 입력, 출처 및 SHA-256을 저장한다."""
    source = ROOT / 'data' / 'baboon.ascii.pgm'
    original = load_ascii_pgm(source)
    if original.shape != (512, 512):
        raise ValueError('선택한 공개 이미지의 원본 크기는 512×512다.')
    image = original[::8, ::8]
    np.save(ROOT / 'data' / 'image64.npy', image)
    metadata = {
        'provider': 'John Burkardt, PGMA sample data',
        'source_page': 'https://people.math.sc.edu/Burkardt/data/pgma/pgma.html',
        'download_url': 'https://people.math.sc.edu/Burkardt/data/pgma/baboon.ascii.pgm',
        'license_on_source_page': 'GNU LGPL', 'retrieved_date': '2026-10-07',
        'raw_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'raw_shape': list(original.shape), 'input_shape': list(image.shape),
        'preprocessing': 'P2 maximum value로 정규화; original[::8, ::8]',
    }
    (ROOT / 'data' / 'source_metadata.json').write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    prepare_image()
