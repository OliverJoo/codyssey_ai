#!/usr/bin/env bash
set -euo pipefail

# 실행 위치를 프로젝트 루트로 고정한다.
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"

echo "[1/4] 원격 daecf53의 src/main.py 실행"
PYTHONDONTWRITEBYTECODE=1 python3 src/main.py

echo "[2/4] 제출 패키지의 4인 통합 추가 예제 실행"
PYTHONDONTWRITEBYTECODE=1 python3 examples/team_utils_demo.py

# 아래 두 사례는 원천 Git 이력 자체가 아니라 임시 저장소에서 만든 추가 학습 재현이다.
demo_dir="$(mktemp -d "${TMPDIR:-/tmp}/b2-2-actual-demo.XXXXXX")"
cleanup() {
  case "$demo_dir" in
    "${TMPDIR:-/tmp}"/b2-2-actual-demo.*) rm -rf "$demo_dir" ;;
    *) echo "안전하지 않은 임시 경로라 삭제하지 않습니다: $demo_dir" ;;
  esac
}
trap cleanup EXIT

git -C "$demo_dir" init -q -b main
git -C "$demo_dir" config user.name "Mission Demo"
git -C "$demo_dir" config user.email "demo@example.com"
mkdir -p "$demo_dir/src" "$demo_dir/docs"
printf 'print("=== Python Utils Demo ===")\n' > "$demo_dir/src/main.py"
printf '# Old Guide\n' > "$demo_dir/docs/old-guide.md"
git -C "$demo_dir" add .
git -C "$demo_dir" commit -q -m "chore: prepare synthetic conflict examples"

echo "[3/4] PR #14·#15를 바탕으로 한 동일 영역 충돌 추가 재현"
git -C "$demo_dir" switch -q -c feature/dave17code-main-conflict
printf 'from string_utils import reverse_string\n\nprint("dave17code:", reverse_string("Hello"))\n' > "$demo_dir/src/main.py"
git -C "$demo_dir" commit -qam "feat: add dave17code result to main runner"
git -C "$demo_dir" switch -q main
printf 'from count_utils import count_words\n\nprint("heeyoung35:", count_words("Hello Git"))\n' > "$demo_dir/src/main.py"
git -C "$demo_dir" commit -qam "feat: add heeyoung35 result to main runner"
if git -C "$demo_dir" merge --no-edit feature/dave17code-main-conflict >/dev/null 2>&1; then
  echo "오류: 예상한 같은 영역 충돌이 발생하지 않았습니다."
  exit 1
fi
printf 'from string_utils import reverse_string\nfrom count_utils import count_words\n\nprint("dave17code:", reverse_string("Hello"))\nprint("heeyoung35:", count_words("Hello Git"))\n' > "$demo_dir/src/main.py"
git -C "$demo_dir" add src/main.py
git -C "$demo_dir" commit -q -m "fix: combine both main runner outputs"

echo "[4/4] 원격 사례와 별개인 modify/delete 충돌 추가 예제"
git -C "$demo_dir" switch -q -c example/remove-guide
git -C "$demo_dir" rm -q docs/old-guide.md
git -C "$demo_dir" commit -q -m "docs: remove old guide for conflict example"
git -C "$demo_dir" switch -q main
printf '# Old Guide\n\n다른 작업자가 내용을 보강했습니다.\n' > "$demo_dir/docs/old-guide.md"
git -C "$demo_dir" commit -qam "docs: expand old guide content"
if git -C "$demo_dir" merge --no-edit example/remove-guide >/dev/null 2>&1; then
  echo "오류: 예상한 modify/delete 충돌이 발생하지 않았습니다."
  exit 1
fi
git -C "$demo_dir" rm -q docs/old-guide.md
# 마지막 파일 삭제로 사라진 docs 디렉터리를 다시 만든다.
mkdir -p "$demo_dir/docs"
printf '# New Guide\n\n다른 작업자의 보강 내용을 새 경로에 보존했습니다.\n' > "$demo_dir/docs/new-file.md"
git -C "$demo_dir" add docs/new-file.md
git -C "$demo_dir" commit -q -m "fix: move modified guide content to new file"
git -C "$demo_dir" log --oneline --graph --all

echo "시연 완료: 원격 원본과 추가 예제를 실행하고, 확인된 동일 영역 충돌 및 별도 modify/delete 예제를 재현했습니다."
