#!/usr/bin/env bash
# 실행에 필요한 Git과 Python 버전을 확인합니다.
set -euo pipefail

command -v git >/dev/null || { echo "[ERROR] Git이 필요합니다." >&2; exit 1; }
command -v python3 >/dev/null || { echo "[ERROR] Python 3가 필요합니다." >&2; exit 1; }

# PDF 요구 버전인 Python 3.10 이상인지 검사합니다.
python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' \
  || { echo "[ERROR] Python 3.10 이상이 필요합니다." >&2; exit 1; }

echo "[OK] $(git --version)"
echo "[OK] $(python3 --version)"
echo "[NEXT] 실제 API 사용 시: export AI_API_KEY='발급받은-키'"
