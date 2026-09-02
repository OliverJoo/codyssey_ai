#!/usr/bin/env bash
# 제출에 필요한 시스템 상태를 한 파일로 수집한다.
set -uo pipefail
export LC_ALL=C

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="${1:-$SCRIPT_DIR/mission-evidence-$(date '+%Y%m%d-%H%M%S').txt}"

# SSH·UFW·ACL을 읽기 위해 root 권한을 요구한다.
if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Run with sudo so protected configuration can be recorded." >&2
  exit 1
fi

# 섹션 제목과 실행 명령을 증거 파일에 보기 좋게 기록한다.
section() { printf '\n===== %s =====\n' "$1"; }
run() {
  printf '\n$ %s\n' "$*"
  "$@" 2>&1 || printf '[command exited %d]\n' "$?"
}

# 민감한 키 값은 제외하고 평가에 필요한 항목만 수집한다.
{
  echo "Codyssey b1-1 evidence"
  echo "Collected: $(date --iso-8601=seconds)"
  echo "Host: $(hostname)"

  section "SSH effective configuration"
  run /usr/sbin/sshd -T
  section "Listening ports"
  run ss -tulnp
  section "Firewall"
  run ufw status verbose

  section "Users and groups"
  run id agent-admin
  run id agent-dev
  run id agent-test

  section "Directories and ACL"
  run ls -ld /home/agent-admin/agent-app /home/agent-admin/agent-app/upload_files /home/agent-admin/agent-app/api_keys /var/log/agent-app
  run getfacl -p /home/agent-admin/agent-app/upload_files
  run getfacl -p /home/agent-admin/agent-app/api_keys
  run getfacl -p /var/log/agent-app
  run stat -c '%U:%G %a %n' /home/agent-admin/agent-app/bin/monitor.sh

  section "Environment (secret value intentionally omitted)"
  run sed -E '/AGENT_KEY_PATH/!p; /AGENT_KEY_PATH/s/=.*/=<configured>/' /etc/agent-app/agent.env

  section "Process, health endpoint, and port"
  run pgrep -a -x agent_app
  run ss -ltnp

  section "Monitor console run"
  run sudo -u agent-admin /home/agent-admin/agent-app/bin/monitor.sh
  section "Recent monitor log"
  run tail -n 10 /var/log/agent-app/monitor.log
  section "agent-admin crontab"
  run crontab -u agent-admin -l
  section "Log rotation policy"
  run sed -n '1,120p' /etc/logrotate.d/agent-app-monitor
  section "Automated verifier"
  run "$SCRIPT_DIR/14_verify_mission.sh"
} > "$OUTPUT"

# 생성된 증거 파일은 소유자·그룹만 읽게 제한한다.
chmod 0640 "$OUTPUT"
echo "[INFO] Evidence written to: $OUTPUT"
