#!/usr/bin/env bash
# 표준 라이브러리 unittest로 전체 자동 테스트를 실행합니다.
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$project_dir"
python3 -m unittest discover -s tests -p 'test_*.py' -v
