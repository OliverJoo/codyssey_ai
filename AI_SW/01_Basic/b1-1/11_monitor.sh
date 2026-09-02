#!/usr/bin/env bash
# 앱 상태와 서버 자원을 확인하고 한 줄 로그로 기록한다.
set -uo pipefail
export LC_ALL=C

# 설치 환경이 있으면 읽어 기본값을 덮어쓴다.
ENV_FILE="${AGENT_ENV_FILE:-/etc/agent-app/agent.env}"
if [[ -r "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

# 대상, 로그 위치, 회전 크기와 경고 임계치를 정의한다.
AGENT_PORT="${AGENT_PORT:-15034}"
AGENT_EXECUTABLE="${AGENT_EXECUTABLE:-/home/agent-admin/agent-app/agent_app}"
AGENT_PROCESS_NAME="${AGENT_PROCESS_NAME:-agent_app}"
AGENT_LOG_DIR="${AGENT_LOG_DIR:-/var/log/agent-app}"
LOG_FILE="${AGENT_LOG_FILE:-$AGENT_LOG_DIR/monitor.log}"
MAX_BYTES="${MONITOR_MAX_BYTES:-10485760}"
CPU_LIMIT="${MONITOR_CPU_LIMIT:-20}"
MEM_LIMIT="${MONITOR_MEM_LIMIT:-10}"
DISK_LIMIT="${MONITOR_DISK_LIMIT:-80}"

die() {
  # 필수 health check 실패는 즉시 종료한다.
  echo "[ERROR] $*" >&2
  exit 1
}

is_greater() {
  # 소수도 비교할 수 있도록 awk를 사용한다.
  awk -v value="$1" -v limit="$2" 'BEGIN { exit !(value > limit) }'
}

rotate_log() {
  # 10MiB 이상이면 활성 로그와 백업 9개를 유지한다.
  local size index
  [[ -f "$LOG_FILE" ]] || return 0
  size="$(stat -c '%s' "$LOG_FILE" 2>/dev/null || printf '0')"
  (( size < MAX_BYTES )) && return 0

  # 높은 번호부터 옮겨 기존 백업이 덮어써지지 않게 한다.
  for ((index = 9; index >= 2; index--)); do
    [[ -f "$LOG_FILE.$((index - 1))" ]] && mv -f "$LOG_FILE.$((index - 1))" "$LOG_FILE.$index"
  done
  mv -f "$LOG_FILE" "$LOG_FILE.1"
  : > "$LOG_FILE"
  chmod 0660 "$LOG_FILE"
}

cpu_usage() {
  # /proc/stat을 1초 간격으로 읽어 CPU 사용률을 계산한다.
  local -a first second
  local idle1 total1 idle2 total2 value
  read -r -a first < /proc/stat
  sleep 1
  read -r -a second < /proc/stat
  idle1=$((first[4] + first[5]))
  idle2=$((second[4] + second[5]))
  total1=0
  total2=0
  for value in "${first[@]:1}"; do total1=$((total1 + value)); done
  for value in "${second[@]:1}"; do total2=$((total2 + value)); done
  awk -v idle="$((idle2 - idle1))" -v total="$((total2 - total1))" \
    'BEGIN { if (total <= 0) print "0.0"; else printf "%.1f", 100 * (total - idle) / total }'
}

memory_usage() {
  # 사용 메모리는 MemTotal - MemAvailable로 계산한다.
  awk '
    /^MemTotal:/ { total=$2 }
    /^MemAvailable:/ { available=$2 }
    END { if (total <= 0) print "0.0"; else printf "%.1f", 100 * (total-available) / total }
  ' /proc/meminfo
}

# 로그 디렉터리의 존재와 쓰기 권한을 확인한다.
mkdir -p "$AGENT_LOG_DIR" 2>/dev/null || true
[[ -d "$AGENT_LOG_DIR" && -w "$AGENT_LOG_DIR" ]] || die "Log directory is not writable: $AGENT_LOG_DIR"

# cron 실행이 겹치지 않도록 잠금 파일을 사용한다.
exec 9>"$AGENT_LOG_DIR/monitor.lock"
flock -n 9 || { echo "[WARNING] A previous monitor run is still active."; exit 0; }

echo "====== SYSTEM MONITOR RESULT ======"
echo "[HEALTH CHECK]"

# 프로세스 이름과 TCP LISTEN 상태를 각각 검사한다.
PID="$(pgrep -x -- "$AGENT_PROCESS_NAME" | head -n 1 || true)"
[[ -n "$PID" ]] || die "Provided app is not running: $AGENT_EXECUTABLE"
echo "Checking process '$(basename "$AGENT_EXECUTABLE")'... [OK] (PID: $PID)"

if ! ss -ltnH | awk '{print $4}' | grep -Eq "(^|:)${AGENT_PORT}$"; then
  die "TCP port $AGENT_PORT is not in LISTEN state."
fi
echo "Checking port $AGENT_PORT... [OK]"

# 방화벽 문제는 데이터 수집을 막지 않고 경고만 남긴다.
FIREWALL_ACTIVE=0
if command -v ufw >/dev/null 2>&1 && sudo -n ufw status 2>/dev/null | grep -q '^Status: active'; then
  FIREWALL_ACTIVE=1
elif command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state 2>/dev/null | grep -q '^running$'; then
  FIREWALL_ACTIVE=1
fi
(( FIREWALL_ACTIVE == 1 )) || echo "[WARNING] UFW/firewalld is not active or cannot be queried."

# CPU, 메모리, 루트 디스크 사용률을 수집한다.
echo "[RESOURCE MONITORING]"
CPU="$(cpu_usage)"
MEM="$(memory_usage)"
DISK="$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')"
echo "CPU Usage : ${CPU}%"
echo "MEM Usage : ${MEM}%"
echo "DISK Used : ${DISK}%"

# 임계치 초과는 서비스 장애가 아니므로 경고 후 계속한다.
is_greater "$CPU" "$CPU_LIMIT" && echo "[WARNING] CPU threshold exceeded (${CPU}% > ${CPU_LIMIT}%)"
is_greater "$MEM" "$MEM_LIMIT" && echo "[WARNING] MEM threshold exceeded (${MEM}% > ${MEM_LIMIT}%)"
is_greater "$DISK" "$DISK_LIMIT" && echo "[WARNING] DISK threshold exceeded (${DISK}% > ${DISK_LIMIT}%)"

# 회전 확인 후 고정 포맷 한 줄을 누적한다.
rotate_log
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
printf '[%s] PID:%s CPU:%s%% MEM:%s%% DISK_USED:%s%%\n' \
  "$TIMESTAMP" "$PID" "$CPU" "$MEM" "$DISK" >> "$LOG_FILE"
echo "[INFO] Log appended: $LOG_FILE"
