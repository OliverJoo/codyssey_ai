#!/usr/bin/env bash
set -Eeuo pipefail

# Linux 안에서 장애 시나리오 하나를 실행하고 증거를 표준 출력으로 모은다.
usage() {
  cat <<'USAGE'
Usage: ./05_run_case.sh CASE

CASE:
  oom-before | oom-after
  cpu-before | cpu-after
  deadlock-before | deadlock-after

Run this script inside Linux as a non-root user. It prints both application
and monitor evidence to standard output. Save it with tee if needed.
USAGE
}

# 실행할 Before/After 케이스를 첫 번째 인자로 받는다.
case_name=${1:-}
if [[ -z $case_name || $case_name == "-h" || $case_name == "--help" ]]; then
  usage
  [[ -n $case_name ]] && exit 0 || exit 2
fi

# 제공 바이너리는 Linux 전용이며 root 실행은 미션 조건에 어긋난다.
if [[ $(uname -s) != "Linux" ]]; then
  echo "ERROR: 05_run_case.sh requires Linux. On macOS use ./06_run_mission.sh." >&2
  exit 1
fi
if [[ $(id -u) -eq 0 ]]; then
  echo "ERROR: agent-leak-app must run as a non-root user." >&2
  exit 1
fi

# 현재 Linux 아키텍처와 맞는 제공 바이너리를 선택한다.
root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
case "$(uname -m)" in
  x86_64|amd64) app="$root_dir/agent-app-leak/agent-leak-app-x86" ;;
  aarch64|arm64) app="$root_dir/agent-app-leak/agent-leak-app-arm64" ;;
  *) echo "ERROR: unsupported Linux architecture: $(uname -m)" >&2; exit 1 ;;
esac

[[ -x $app ]] || { echo "ERROR: executable not found: $app" >&2; exit 1; }

# 먼저 안전한 기본값을 두고 케이스마다 변수 하나만 바꾼다.
memory_limit=512
cpu_max_occupy=10
multi_thread_enable=false
duration=18

case "$case_name" in
  oom-before)       memory_limit=50;  duration=12 ;;
  oom-after)        memory_limit=100; duration=18 ;;
  # 부하 증가 속도에는 작은 무작위 편차가 있으므로 임계치 위반(약 50%)을
  # 증거 로그에 확실히 남길 수 있도록 최대 관찰 시간을 넉넉히 둔다.
  cpu-before)       cpu_max_occupy=100; duration=70 ;;
  cpu-after)        cpu_max_occupy=10;  duration=25 ;;
  deadlock-before)  multi_thread_enable=true;  duration=20 ;;
  deadlock-after)   multi_thread_enable=false; duration=20 ;;
  *) echo "ERROR: unknown CASE: $case_name" >&2; usage; exit 2 ;;
esac

# 키·로그·업로드 파일은 격리된 임시 폴더에 만들고 종료 시 지운다.
run_dir=$(mktemp -d "${TMPDIR:-/tmp}/agent-b1-2.XXXXXX")
cleanup() {
  for pid in "${monitored_pid:-}" "${app_pid:-}"; do
    if [[ -n $pid ]] && kill -0 "$pid" 2>/dev/null; then
      kill -TERM "$pid" 2>/dev/null || true
    fi
  done
  sleep 1
  for pid in "${monitored_pid:-}" "${app_pid:-}"; do
    if [[ -n $pid ]] && kill -0 "$pid" 2>/dev/null; then
      kill -KILL "$pid" 2>/dev/null || true
    fi
  done
  rm -rf "$run_dir"
}
trap cleanup EXIT INT TERM

# PDF가 요구한 실행 환경변수를 앱에 전달한다.
export AGENT_HOME="$run_dir/home"
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR="$AGENT_HOME/upload_files"
export AGENT_KEY_PATH="$AGENT_HOME/api_keys"
export AGENT_LOG_DIR="$AGENT_HOME/logs"
export MEMORY_LIMIT="$memory_limit"
export CPU_MAX_OCCUPY="$cpu_max_occupy"
export MULTI_THREAD_ENABLE="$multi_thread_enable"

# 필수 디렉터리와 정확한 테스트 키 문자열을 준비한다.
mkdir -p "$AGENT_UPLOAD_DIR" "$AGENT_KEY_PATH" "$AGENT_LOG_DIR"
printf '%s' 'agent_api_key_test' > "$AGENT_KEY_PATH/secret.key"

app_log="$run_dir/application.log"
monitor_log="$run_dir/monitor.log"
started_at=$(date -Iseconds)

# 앱을 백그라운드로 실행해 관제 스크립트와 동시에 기록한다.
"$app" >"$app_log" 2>&1 &
app_pid=$!

# 런처가 만든 자식 프로세스를 찾아 실제 워크로드 PID를 관제한다.
monitored_pid=$app_pid
for _ in {1..30}; do
  child_pid=$(pgrep -P "$app_pid" 2>/dev/null | head -n 1 || true)
  if [[ $child_pid =~ ^[0-9]+$ ]]; then
    monitored_pid=$child_pid
    break
  fi
  kill -0 "$app_pid" 2>/dev/null || break
  sleep 0.1
done

# 실제 워크로드 PID를 1초 간격으로 관제한다.
"$root_dir/04_monitor.sh" "$monitored_pid" 1 >"$monitor_log" 2>&1 &
monitor_pid=$!

# 앱이 먼저 끝나는지, 안전 관찰 시간이 먼저 끝나는지 기다린다.
deadline=$((SECONDS + duration))
timed_out=false
while kill -0 "$app_pid" 2>/dev/null && (( SECONDS < deadline )); do
  sleep 1
done

# Deadlock처럼 멈춘 앱은 제한 시간 뒤 이 실험의 PID만 종료한다.
if kill -0 "$app_pid" 2>/dev/null; then
  timed_out=true
  kill -TERM "$monitored_pid" 2>/dev/null || true
  kill -TERM "$app_pid" 2>/dev/null || true
  sleep 1
  kill -KILL "$monitored_pid" 2>/dev/null || true
  kill -KILL "$app_pid" 2>/dev/null || true
fi

# 장애 종료 코드도 증거이므로 set -e를 잠시 풀어 저장한다.
set +e
wait "$app_pid" 2>/dev/null
app_status=$?
wait "$monitor_pid" 2>/dev/null
set -e

# 실험 정보·관제 CSV·앱 로그를 한 증거 파일 형식으로 합친다.
cat <<EOF
===== EXPERIMENT =====
CASE=$case_name
STARTED_AT=$started_at
PID=$monitored_pid
LAUNCHER_PID=$app_pid
ARCH=$(uname -m)
MEMORY_LIMIT=$MEMORY_LIMIT
CPU_MAX_OCCUPY=$CPU_MAX_OCCUPY
MULTI_THREAD_ENABLE=$MULTI_THREAD_ENABLE
TIME_LIMIT_SECONDS=$duration
TIMED_OUT=$timed_out
PROCESS_EXIT_STATUS=$app_status

===== MONITOR =====
EOF
cat "$monitor_log"
printf '\n===== APPLICATION =====\n'
cat "$app_log"
printf '\n===== END =====\n'
