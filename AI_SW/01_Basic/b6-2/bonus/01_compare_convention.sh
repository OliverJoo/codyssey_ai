#!/usr/bin/env bash
# 같은 변경에서 프로젝트 규칙 적용 전후 프롬프트를 비교합니다.
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"

echo "[BEFORE] 기본 프롬프트"
python3 "$project_dir/main.py" commit --dry-run
echo
echo "[AFTER] convention_example.json 적용"
python3 "$project_dir/main.py" commit --dry-run \
  --convention-file "$project_dir/bonus/convention_example.json"
