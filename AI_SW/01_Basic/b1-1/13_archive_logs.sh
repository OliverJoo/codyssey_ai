#!/usr/bin/env bash
# 오래된 로그를 압축·보관하고 만료된 보관본을 삭제한다.
set -Eeuo pipefail

LOG_DIR="${AGENT_LOG_DIR:-/var/log/agent-app}"
ARCHIVE_DIR="${AGENT_ARCHIVE_DIR:-/var/log/monitor/agent-app/archive}"

# /var/log를 관리하므로 root 권한이 필요하다.
if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Run archive_logs.sh with sudo because it manages /var/log." >&2
  exit 1
fi
if [[ ! -d "$LOG_DIR" ]]; then
  echo "[WARNING] Log directory does not exist: $LOG_DIR"
  exit 0
fi

# 7일 지난 .log 파일을 gzip으로 압축해 보관소로 옮긴다.
install -d -m 0750 -o root -g agent-core "$ARCHIVE_DIR"
compressed=0
while IFS= read -r -d '' file; do
  stamp="$(date -r "$file" '+%Y%m%d%H%M%S')"
  gzip -f "$file"
  mv -f "$file.gz" "$ARCHIVE_DIR/$(basename "$file").$stamp.gz"
  compressed=$((compressed + 1))
done < <(find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -mtime +6 -print0)

# 30일 지난 압축 보관본을 삭제한다.
deleted=0
while IFS= read -r -d '' archive; do
  rm -f -- "$archive"
  deleted=$((deleted + 1))
done < <(find "$ARCHIVE_DIR" -maxdepth 1 -type f -name '*.gz' -mtime +29 -print0)

echo "[INFO] Compressed and archived: $compressed file(s)"
echo "[INFO] Deleted archives older than 30 days: $deleted file(s)"
