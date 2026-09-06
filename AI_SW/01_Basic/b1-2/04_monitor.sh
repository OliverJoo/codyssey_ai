#!/usr/bin/env bash
set -Eeuo pipefail

# 지정한 PID의 CPU·메모리·상태를 1초 간격 CSV로 기록한다.
usage() {
  echo "Usage: $0 <PID> [interval_seconds]" >&2
}

# 첫 번째 인자는 숫자 PID여야 한다.
if [[ $# -lt 1 || ! ${1:-} =~ ^[0-9]+$ ]]; then
  usage
  exit 2
fi

pid=$1
interval=${2:-1}
# 두 번째 인자는 선택 사항인 관제 간격(초)이다.
if [[ ! $interval =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "interval_seconds must be a positive number" >&2
  exit 2
fi

# 프로세스가 살아 있는 동안 ps 값을 같은 열 순서로 출력한다.
echo "TIMESTAMP,PID,CPU_PERCENT,RSS_KB,MEM_MB,STATE,THREADS,ELAPSED"
while kill -0 "$pid" 2>/dev/null; do
  sample=$(ps -p "$pid" -o %cpu=,rss=,stat=,nlwp=,etime= 2>/dev/null || true)
  if [[ -n $sample ]]; then
    read -r cpu rss state threads elapsed <<<"$sample"
    # ps의 RSS(KB)를 읽기 쉬운 MB로 변환한다.
    mem_mb=$(awk -v rss="$rss" 'BEGIN { printf "%.2f", rss / 1024 }')
    printf '%s,%s,%s,%s,%s,%s,%s,%s\n' \
      "$(date -Iseconds)" "$pid" "$cpu" "$rss" "$mem_mb" "$state" "$threads" "$elapsed"
  fi
  sleep "$interval"
done
# 종료 시각도 남겨 앱 로그와 시간축을 맞춘다.
printf '%s,%s,EXITED,,,,,\n' "$(date -Iseconds)" "$pid"
