#!/usr/bin/env bash
# 민감정보가 있는 변경에서 safe-mode ON/OFF 프롬프트를 비교합니다.
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"

echo "[SAFE MODE ON] 이메일과 키가 [MASKED]로 표시됩니다."
python3 "$project_dir/main.py" commit --dry-run --safe-mode
echo
echo "[SAFE MODE OFF] 실제 API 전송에는 사용하지 마세요."
python3 "$project_dir/main.py" commit --dry-run --no-safe-mode
