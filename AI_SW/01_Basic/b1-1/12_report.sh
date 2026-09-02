#!/usr/bin/env bash
# monitor.log의 CPU·메모리·디스크 통계를 요약한다.
set -Eeuo pipefail
export LC_ALL=C

LOG_FILE="${AGENT_LOG_FILE:-/var/log/agent-app/monitor.log}"
FROM=""
TO=""

# 지원 옵션을 출력한다.
usage() {
  echo "Usage: $0 [--from 'YYYY-MM-DD HH:MM:SS'] [--to 'YYYY-MM-DD HH:MM:SS'] [--log FILE]"
}

# 기간과 입력 로그 옵션을 해석한다.
while (($#)); do
  case "$1" in
    --from) FROM="${2:?--from needs a value}"; shift 2 ;;
    --to) TO="${2:?--to needs a value}"; shift 2 ;;
    --log) LOG_FILE="${2:?--log needs a value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "[ERROR] Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

# 읽을 수 있는 로그만 분석한다.
[[ -r "$LOG_FILE" ]] || { echo "[ERROR] Cannot read $LOG_FILE" >&2; exit 1; }

# 고정 포맷 로그를 파싱해 평균·최대·최소를 계산한다.
awk -v from="$FROM" -v to="$TO" '
  function value(field, prefix, result) {
    # CPU:12.3% 형태에서 숫자만 꺼낸다.
    result=field
    sub("^" prefix ":", "", result)
    sub("%$", "", result)
    return result + 0
  }
  /^\[[0-9]{4}-[0-9]{2}-[0-9]{2} / {
    datepart=$1; sub(/^\[/, "", datepart)
    timepart=$2; sub(/\]$/, "", timepart)
    timestamp=datepart " " timepart
    # 지정한 기간 밖의 표본은 건너뛴다.
    if (from != "" && timestamp < from) next
    if (to != "" && timestamp > to) next

    cpu=value($4, "CPU")
    mem=value($5, "MEM")
    disk=value($6, "DISK_USED")
    count++
    cpu_sum+=cpu; mem_sum+=mem; disk_sum+=disk

    # 자원별 최솟값·최댓값과 발생 시각을 갱신한다.
    if (count == 1 || cpu < cpu_min) { cpu_min=cpu; cpu_min_at=timestamp }
    if (count == 1 || cpu > cpu_max) { cpu_max=cpu; cpu_max_at=timestamp }
    if (count == 1 || mem < mem_min) { mem_min=mem; mem_min_at=timestamp }
    if (count == 1 || mem > mem_max) { mem_max=mem; mem_max_at=timestamp }
    if (count == 1 || disk < disk_min) { disk_min=disk; disk_min_at=timestamp }
    if (count == 1 || disk > disk_max) { disk_max=disk; disk_max_at=timestamp }
  }
  END {
    # 표본이 없으면 잘못된 기간 또는 빈 로그로 판단한다.
    if (count == 0) {
      print "[WARNING] No samples matched the requested range." > "/dev/stderr"
      exit 2
    }
    print "====== STATISTICS REPORT ======"
    printf "[CPU]\nAverage : %.1f%%\nMaximum : %.1f%% at %s\nMinimum : %.1f%% at %s\n", cpu_sum/count, cpu_max, cpu_max_at, cpu_min, cpu_min_at
    printf "[Memory]\nAverage : %.1f%%\nMaximum : %.1f%% at %s\nMinimum : %.1f%% at %s\n", mem_sum/count, mem_max, mem_max_at, mem_min, mem_min_at
    printf "[Disk]\nAverage : %.1f%%\nMaximum : %.1f%% at %s\nMinimum : %.1f%% at %s\n", disk_sum/count, disk_max, disk_max_at, disk_min, disk_min_at
    printf "[Samples]\nData Points: %d samples\n", count
  }
' "$LOG_FILE"
