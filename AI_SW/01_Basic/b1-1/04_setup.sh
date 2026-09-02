#!/usr/bin/env bash
# Ubuntu VM에 미션 환경 전체를 설치하는 메인 스크립트다.
set -Eeuo pipefail

# 원본 파일과 설치 대상 경로를 정의한다.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
AGENT_HOME="/home/agent-admin/agent-app"
PROVIDED_DIR="$SCRIPT_DIR/agent-app"

usage() {
  cat <<'USAGE'
Usage: sudo ./04_setup.sh [--yes]

Configures a disposable Ubuntu 22.04+ VM for Codyssey b1-1. The script changes
the SSH port to 20022, enables UFW, creates local users/groups, and installs a
cron task. Keep VM console access open until SSH on port 20022 is verified.
USAGE
}

# 도움말, root 권한, Ubuntu 환경을 차례로 확인한다.
[[ "${1:-}" != "-h" && "${1:-}" != "--help" ]] || { usage; exit 0; }
if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Run with sudo: sudo ./04_setup.sh" >&2
  exit 1
fi

if [[ -r /etc/os-release ]]; then
  # shellcheck disable=SC1091
  source /etc/os-release
fi
if [[ "${ID:-}" != "ubuntu" ]]; then
  echo "[ERROR] This learning setup targets Ubuntu 22.04+; detected ${PRETTY_NAME:-unknown}." >&2
  exit 1
fi

# SSH와 방화벽 변경 전 사용자 확인을 받는다.
if [[ "${1:-}" != "--yes" ]]; then
  echo "This will change SSH/UFW and create agent-* accounts on this Ubuntu machine."
  read -r -p "Type YES to continue: " answer
  [[ "$answer" == "YES" ]] || { echo "Cancelled."; exit 0; }
fi

echo "[1/8] Installing required packages"
# 계정·ACL·SSH·방화벽·cron 점검에 필요한 패키지를 설치한다.
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  acl cron curl gawk iproute2 openssh-server procps sudo ufw util-linux

echo "[2/8] Creating groups and users"
# 공용 그룹과 핵심 운영 그룹을 역할에 맞게 구성한다.
getent group agent-common >/dev/null || groupadd agent-common
getent group agent-core >/dev/null || groupadd agent-core
for user in agent-admin agent-dev agent-test; do
  id "$user" >/dev/null 2>&1 || useradd --create-home --shell /bin/bash "$user"
  usermod -aG agent-common "$user"
done
usermod -aG agent-core agent-admin
usermod -aG agent-core agent-dev

echo "[3/8] Creating directories, ACLs, and key file"
# setgid와 ACL로 새 파일에도 그룹 권한이 이어지게 한다.
install -d -m 2770 -o agent-admin -g agent-core "$AGENT_HOME"
install -d -m 2770 -o agent-dev -g agent-core "$AGENT_HOME/bin"
install -d -m 2770 -o agent-admin -g agent-common "$AGENT_HOME/upload_files"
install -d -m 2770 -o agent-admin -g agent-core "$AGENT_HOME/api_keys"
install -d -m 2770 -o agent-admin -g agent-core /var/log/agent-app

setfacl -m u::rwx,g::rwx,g:agent-common:rwx,m::rwx,o::--- "$AGENT_HOME/upload_files"
setfacl -m d:u::rwx,d:g::rwx,d:g:agent-common:rwx,d:m::rwx,d:o::--- "$AGENT_HOME/upload_files"
setfacl -m u::rwx,g::rwx,g:agent-core:rwx,m::rwx,o::--- "$AGENT_HOME/api_keys" /var/log/agent-app
setfacl -m d:u::rwx,d:g::rwx,d:g:agent-core:rwx,d:m::rwx,d:o::--- "$AGENT_HOME/api_keys" /var/log/agent-app

# 제공 바이너리가 실제로 요구하는 키 파일을 만든다.
printf '%s\n' 'agent_api_key_test' > "$AGENT_HOME/api_keys/secret.key"
chown agent-admin:agent-core "$AGENT_HOME/api_keys/secret.key"
chmod 0640 "$AGENT_HOME/api_keys/secret.key"

echo "[4/8] Installing application and Bash scripts"
# Linux CPU 아키텍처에 맞는 제공 바이너리를 선택한다.
case "$(uname -m)" in
  arm64|aarch64) PROVIDED_APP="$PROVIDED_DIR/agent-app-linux-arm64" ;;
  x86_64|amd64) PROVIDED_APP="$PROVIDED_DIR/agent-app-linux-x86" ;;
  *) echo "[ERROR] Unsupported Linux architecture: $(uname -m)" >&2; exit 1 ;;
esac
[[ -f "$PROVIDED_APP" ]] || { echo "[ERROR] Missing provided app: $PROVIDED_APP" >&2; exit 1; }
# 실행 파일별 소유자·그룹·권한을 지정해 설치한다.
install -m 0750 -o agent-admin -g agent-core "$PROVIDED_APP" "$AGENT_HOME/agent_app"
install -m 0750 -o agent-admin -g agent-core "$SCRIPT_DIR/10_run_agent.sh" "$AGENT_HOME/bin/run_agent.sh"
install -m 0750 -o agent-dev -g agent-core "$SCRIPT_DIR/11_monitor.sh" "$AGENT_HOME/bin/monitor.sh"
install -m 0750 -o agent-dev -g agent-core "$SCRIPT_DIR/12_report.sh" "$AGENT_HOME/bin/report.sh"
install -m 0750 -o root -g agent-core "$SCRIPT_DIR/13_archive_logs.sh" "$AGENT_HOME/bin/archive_logs.sh"

install -d -m 0750 -o root -g agent-core /etc/agent-app
install -m 0640 -o root -g agent-core "$SCRIPT_DIR/05_agent.env.example" /etc/agent-app/agent.env

echo "[5/8] Configuring SSH on TCP 20022"
# SSH 설정을 설치하고 문법 검사 후 서비스를 재시작한다.
install -d -m 0755 /etc/ssh/sshd_config.d
install -m 0644 -o root -g root "$SCRIPT_DIR/06_sshd-agent-mission.conf" /etc/ssh/sshd_config.d/00-agent-mission.conf
ssh-keygen -A
/usr/sbin/sshd -t
systemctl restart ssh 2>/dev/null || service ssh restart

echo "[6/8] Enabling UFW (only TCP 20022 and 15034 are added)"
# 외부에서 필요한 SSH와 앱 포트만 허용한다.
ufw default deny incoming
ufw default allow outgoing
ufw allow 20022/tcp comment 'Codyssey SSH'
ufw allow 15034/tcp comment 'Codyssey agent app'
ufw --force enable

echo "[7/8] Installing cron, log rotation, and narrow firewall status permission"
# 자동 모니터링, 로그 회전, 제한된 UFW 조회 권한을 설치한다.
install -m 0644 -o root -g root "$SCRIPT_DIR/08_agent-app-monitor.logrotate" /etc/logrotate.d/agent-app-monitor
install -m 0644 -o root -g root "$SCRIPT_DIR/09_agent-app-archive.cron" /etc/cron.d/agent-app-archive
printf '%s\n' 'agent-admin ALL=(root) NOPASSWD: /usr/sbin/ufw status' | \
  install -m 0440 -o root -g root /dev/stdin /etc/sudoers.d/agent-monitor-firewall
visudo -cf /etc/sudoers.d/agent-monitor-firewall
crontab -u agent-admin "$SCRIPT_DIR/07_agent-admin.cron"
systemctl enable --now cron 2>/dev/null || service cron restart

echo "[8/8] Completed"
# 다음에 수행할 명령을 안내한다.
echo
echo "Next steps:"
echo "  1) Set a lab password: sudo passwd agent-admin"
echo "  2) Start the app:      sudo -iu agent-admin $AGENT_HOME/bin/run_agent.sh"
echo "  3) In another shell:   sudo -u agent-admin $AGENT_HOME/bin/monitor.sh"
echo "  4) Verify:             sudo $SCRIPT_DIR/14_verify_mission.sh"
echo
echo "Do not close the VM console until: ssh -p 20022 agent-admin@<VM_IP> succeeds."
