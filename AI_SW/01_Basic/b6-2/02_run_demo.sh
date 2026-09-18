#!/usr/bin/env bash
# 임시 Git 저장소와 로컬 모의 API로 commit/PR 생성을 한 번에 시연합니다.
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/b6-2-demo.XXXXXX")"
demo_dir="$work_dir/repository"
port_file="$work_dir/mock-port"
server_log="$work_dir/mock-server.log"
server_pid=""

cleanup() {
  # 백그라운드 서버와 임시 저장소를 항상 정리합니다.
  if [[ -n "$server_pid" ]]; then
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
  rm -rf "$work_dir"
}
trap cleanup EXIT

# 변경 사항이 있는 독립 Git 저장소를 준비합니다.
mkdir -p "$demo_dir"
git -C "$demo_dir" init -q
git -C "$demo_dir" config user.email "student@example.com"
git -C "$demo_dir" config user.name "Student"
printf '%s\n' "print('before')" > "$demo_dir/app.py"
git -C "$demo_dir" add app.py
git -C "$demo_dir" commit -qm "initial"
printf '%s\n' "print('after')" "# TODO: add greeting" > "$demo_dir/app.py"

# 외부 비용이 없는 로컬 API 서버를 빈 포트에서 실행합니다.
python3 "$project_dir/tests/mock_ai_server.py" --port 0 --port-file "$port_file" > "$server_log" 2>&1 &
server_pid=$!
for _ in {1..50}; do
  [[ -s "$port_file" ]] && break
  sleep 0.1
done
[[ -s "$port_file" ]] || { echo "[ERROR] 모의 API 서버가 시작되지 않았습니다." >&2; exit 1; }

export AI_API_KEY="local-demo-key"
export AI_API_URL="http://127.0.0.1:$(<"$port_file")"

echo "[DEMO 1/2] commit 초안"
(cd "$demo_dir" && python3 "$project_dir/main.py" commit --temperature 0.2 --max-tokens 300)
echo
echo "[DEMO 2/2] PR 초안"
(cd "$demo_dir" && python3 "$project_dir/main.py" pr --temperature 0.2 --max-tokens 500)
echo
echo "[OK] 시연 완료: 외부 API와 실제 저장소는 변경하지 않았습니다."
