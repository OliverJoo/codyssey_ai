#!/usr/bin/env bash
# 제출 전 파일명, 링크, Python 문법, 기능 테스트를 순서대로 확인합니다.
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$project_dir"

echo "[1/3] 파일명과 문서 링크 검사"
python3 tests/verify_links.py

echo "[2/3] Python 문법 검사"
python3 -m compileall -q main.py src tests

echo "[3/3] 자동 테스트"
bash 03_run_tests.sh

echo "[OK] b6-2 제출물 검증을 모두 통과했습니다."
