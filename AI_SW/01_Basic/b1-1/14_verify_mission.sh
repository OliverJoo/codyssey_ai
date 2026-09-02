#!/usr/bin/env bash
# 미션 필수 조건을 PASS·FAIL·WARN으로 일괄 검증한다.
set -uo pipefail
export LC_ALL=C

PASS=0
FAIL=0
WARN=0
AGENT_HOME="/home/agent-admin/agent-app"
LOG_FILE="/var/log/agent-app/monitor.log"

# 결과 출력과 개수 누적을 공통 함수로 처리한다.
pass() { printf '[PASS] %s\n' "$*"; PASS=$((PASS + 1)); }
fail() { printf '[FAIL] %s\n' "$*"; FAIL=$((FAIL + 1)); }
warn() { printf '[WARN] %s\n' "$*"; WARN=$((WARN + 1)); }
check() {
  local description="$1"; shift
  if "$@" >/dev/null 2>&1; then pass "$description"; else fail "$description"; fi
}

# 보호된 시스템 설정을 읽기 위해 root 권한을 요구한다.
if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Run with sudo so SSH, UFW, cron, and ownership can be verified." >&2
  exit 2
fi

echo "====== B1-1 MISSION VERIFICATION ======"

# SSH의 최종 해석값과 실제 20022 LISTEN을 확인한다.
SSHD_EFFECTIVE="$(/usr/sbin/sshd -T 2>/dev/null || true)"
grep -qx 'port 20022' <<<"$SSHD_EFFECTIVE" && pass "SSH effective port is 20022" || fail "SSH effective port is 20022"
grep -qx 'permitrootlogin no' <<<"$SSHD_EFFECTIVE" && pass "Root remote login is disabled" || fail "Root remote login is disabled"
ss -ltnH | awk '{print $4}' | grep -Eq '(^|:)20022$' && pass "sshd is listening on TCP 20022" || fail "sshd is listening on TCP 20022"

# UFW 활성화와 허용 포트가 정확히 두 개인지 확인한다.
UFW_STATUS="$(ufw status 2>/dev/null || true)"
grep -q '^Status: active' <<<"$UFW_STATUS" && pass "UFW is active" || fail "UFW is active"
grep -Eq '^20022/tcp[[:space:]]+ALLOW' <<<"$UFW_STATUS" && pass "UFW allows TCP 20022" || fail "UFW allows TCP 20022"
grep -Eq '^15034/tcp[[:space:]]+ALLOW' <<<"$UFW_STATUS" && pass "UFW allows TCP 15034" || fail "UFW allows TCP 15034"
EXTRA_RULES="$(awk '/ALLOW/ && $1 != "20022/tcp" && $1 != "15034/tcp" {print}' <<<"$UFW_STATUS")"
[[ -z "$EXTRA_RULES" ]] && pass "UFW has no extra ALLOW rules" || { fail "UFW has no extra ALLOW rules"; printf '%s\n' "$EXTRA_RULES"; }

# 세 계정의 공용 그룹과 핵심 그룹 분리를 확인한다.
for user in agent-admin agent-dev agent-test; do
  check "User exists: $user" id "$user"
  id -nG "$user" | tr ' ' '\n' | grep -qx agent-common && pass "$user belongs to agent-common" || fail "$user belongs to agent-common"
done
for user in agent-admin agent-dev; do
  id -nG "$user" | tr ' ' '\n' | grep -qx agent-core && pass "$user belongs to agent-core" || fail "$user belongs to agent-core"
done
if id -nG agent-test 2>/dev/null | tr ' ' '\n' | grep -qx agent-core; then
  fail "agent-test is excluded from agent-core"
else
  pass "agent-test is excluded from agent-core"
fi

# 디렉터리 그룹과 ACL이 역할 설계와 같은지 확인한다.
check "Upload directory exists" test -d "$AGENT_HOME/upload_files"
check "API key directory exists" test -d "$AGENT_HOME/api_keys"
check "Log directory exists" test -d /var/log/agent-app
[[ "$(stat -c '%G' "$AGENT_HOME/upload_files" 2>/dev/null)" == agent-common ]] && pass "upload_files group is agent-common" || fail "upload_files group is agent-common"
[[ "$(stat -c '%G' "$AGENT_HOME/api_keys" 2>/dev/null)" == agent-core ]] && pass "api_keys group is agent-core" || fail "api_keys group is agent-core"
[[ "$(stat -c '%G' /var/log/agent-app 2>/dev/null)" == agent-core ]] && pass "log directory group is agent-core" || fail "log directory group is agent-core"
getfacl -cp "$AGENT_HOME/upload_files" 2>/dev/null | grep -qx 'group:agent-common:rwx' && pass "upload_files ACL grants agent-common rwx" || fail "upload_files ACL grants agent-common rwx"
getfacl -cp "$AGENT_HOME/api_keys" 2>/dev/null | grep -qx 'group:agent-core:rwx' && pass "api_keys ACL grants agent-core rwx" || fail "api_keys ACL grants agent-core rwx"

# 스크립트 권한, 키 내용, 제공 앱 실행 권한을 확인한다.
[[ "$(stat -c '%U:%G:%a' "$AGENT_HOME/bin/monitor.sh" 2>/dev/null)" == 'agent-dev:agent-core:750' ]] && \
  pass "monitor.sh is agent-dev:agent-core mode 750" || fail "monitor.sh is agent-dev:agent-core mode 750"
check "Key file contains the required value" grep -qx 'agent_api_key_test' "$AGENT_HOME/api_keys/secret.key"
check "Architecture-matched provided app is executable" test -x "$AGENT_HOME/agent_app"

# 앱 프로세스와 TCP 15034 상태를 별도로 확인한다.
pgrep -x agent_app >/dev/null && pass "Provided agent app process is running" || fail "Provided agent app process is running"
ss -ltnH | awk '{print $4}' | grep -Eq '(^|:)15034$' && pass "App listens on TCP 15034" || fail "App listens on TCP 15034"

# 매분 모니터링 cron 등록 여부를 확인한다.
if crontab -u agent-admin -l 2>/dev/null | grep -Fq "$AGENT_HOME/bin/monitor.sh"; then
  pass "agent-admin crontab runs monitor.sh"
else
  fail "agent-admin crontab runs monitor.sh"
fi

# 최근 로그가 과제의 고정 포맷을 따르는지 확인한다.
if [[ -s "$LOG_FILE" ]] && tail -n 20 "$LOG_FILE" | \
  grep -Eq '^\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\] PID:[0-9]+ CPU:[0-9.]+% MEM:[0-9.]+% DISK_USED:[0-9]+%$'; then
  pass "monitor.log contains the required format"
else
  fail "monitor.log contains the required format"
fi

# 로그 계열 파일 수와 logrotate 정책을 확인한다.
ROTATE_COUNT="$(find /var/log/agent-app -maxdepth 1 -type f -name 'monitor.log*' 2>/dev/null | wc -l | tr -d ' ')"
(( ROTATE_COUNT <= 10 )) && pass "monitor log family is limited to 10 files" || fail "monitor log family is limited to 10 files"
[[ -f /etc/logrotate.d/agent-app-monitor ]] && pass "logrotate policy is installed" || warn "logrotate policy is not installed"

# FAIL이 하나라도 있으면 스크립트도 실패 상태로 끝낸다.
echo "----------------------------------------"
printf 'PASS=%d FAIL=%d WARN=%d\n' "$PASS" "$FAIL" "$WARN"
(( FAIL == 0 ))
