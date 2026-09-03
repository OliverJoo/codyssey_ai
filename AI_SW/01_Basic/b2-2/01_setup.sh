#!/usr/bin/env bash
set -euo pipefail

# 실행 위치를 프로젝트 루트로 고정한다.
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"

# 미션 최소 버전을 확인한다.
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ 필요"'
git --version

# 표준 라이브러리만 사용하므로 추가 설치는 없다.
echo "준비 완료: Python 3.10+ 및 Git을 확인했습니다."
