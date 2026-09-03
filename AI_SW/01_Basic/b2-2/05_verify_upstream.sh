#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository="https://github.com/dave17code/b2-2-git-conflict-craft.git"
expected_head="daecf53b3583410c9f5a0c70d363a507e81683c5"
audit_dir="$(mktemp -d "${TMPDIR:-/tmp}/b2-2-upstream-check.XXXXXX")"

cleanup() {
  case "$audit_dir" in
    "${TMPDIR:-/tmp}"/b2-2-upstream-check.*) rm -rf "$audit_dir" ;;
    *) echo "안전하지 않은 임시 경로라 삭제하지 않습니다: $audit_dir" ;;
  esac
}
trap cleanup EXIT

git clone --quiet --branch main --single-branch "$repository" "$audit_dir"
actual_head="$(git -C "$audit_dir" rev-parse HEAD)"
if [[ "$actual_head" != "$expected_head" ]]; then
  echo "[FAIL] 원격 main이 기준 commit에서 변경되었습니다."
  echo "expected: $expected_head"
  echo "actual:   $actual_head"
  echo "최신 이력을 다시 감사한 뒤 manifest를 갱신하세요."
  exit 1
fi

diff -u -r "$audit_dir/src" "$project_dir/src"
diff -u "$audit_dir/docs/new-file.md" "$project_dir/docs/new-file.md"
diff -u "$audit_dir/docs/new_guide.md" "$project_dir/docs/new_guide.md"
diff -u "$audit_dir/docs/git-log.txt" "$project_dir/docs/git-log.txt"

git -C "$audit_dir" show --summary --oneline abe92b8
git -C "$audit_dir" log --first-parent --oneline --max-count=20
echo "[OK] 원격 daecf53와 보존 스냅샷이 일치합니다."
