#!/usr/bin/env bash
set -euo pipefail

# 어떤 위치에서 호출해도 동일한 테스트를 실행한다.
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
