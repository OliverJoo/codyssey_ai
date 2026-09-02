#!/usr/bin/env bash
# Apple Silicon과 Intel Mac에서 공통으로 쓰는 Docker 일괄 테스트다.
set -Eeuo pipefail

# 현재 폴더와 제공 바이너리 위치를 계산한다.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${B1_AGENT_APP_DIR:-$SCRIPT_DIR/agent-app}"
CONTAINER_NAME="codyssey-b1-1-$(date '+%Y%m%d%H%M%S')-$$"

cleanup() {
  # 정상 종료와 오류 종료 모두에서 테스트 컨테이너를 제거한다.
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

# Docker 설치 여부와 데몬 상태를 먼저 확인한다.
command -v docker >/dev/null 2>&1 || {
  echo "[ERROR] Docker Desktop is required. Install/start Docker, then retry." >&2
  exit 1
}
docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not running." >&2
  exit 1
}

# Mac CPU에 맞는 Linux 플랫폼과 제공 앱을 선택한다.
SELECTED_ARCH="${B1_TEST_ARCH:-$(uname -m)}"
case "$SELECTED_ARCH" in
  arm64|aarch64)
    PLATFORM="linux/arm64"
    APP_FILE="agent-app-linux-arm64"
    ;;
  x86_64|amd64)
    PLATFORM="linux/amd64"
    APP_FILE="agent-app-linux-x86"
    ;;
  *)
    echo "[ERROR] Unsupported architecture: $SELECTED_ARCH" >&2
    exit 1
    ;;
esac

# 테스트에 필요한 파일이 모두 같은 폴더에 있는지 확인한다.
for required in 11_monitor.sh 12_report.sh 05_agent.env.example; do
  [[ -f "$SCRIPT_DIR/$required" ]] || {
    echo "[ERROR] Missing $required. Keep 03_portable_lab.sh with the numbered mission files." >&2
    exit 1
  }
done
[[ -f "$APP_DIR/$APP_FILE" ]] || {
  echo "[ERROR] Missing provided app: $APP_DIR/$APP_FILE" >&2
  exit 1
}

echo "[INFO] Host architecture : $(uname -m)"
[[ -z "${B1_TEST_ARCH:-}" ]] || echo "[INFO] Test override     : $B1_TEST_ARCH"
echo "[INFO] Docker platform   : $PLATFORM"
echo "[INFO] Provided app      : $APP_FILE"
echo "[INFO] Container         : $CONTAINER_NAME (auto-remove enabled)"

# 미션 폴더와 원본 앱은 읽기 전용으로 마운트한다.
docker run --name "$CONTAINER_NAME" --rm --platform "$PLATFORM" \
  -v "$SCRIPT_DIR:/mission:ro" \
  -v "$APP_DIR:/provided:ro" \
  ubuntu:22.04 bash -lc '
    set -Eeuo pipefail
    # 최소 패키지와 실습용 계정·그룹을 준비한다.
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq gawk iproute2 procps sudo util-linux >/dev/null

    groupadd agent-common
    groupadd agent-core
    useradd -m -s /bin/bash agent-admin
    usermod -aG agent-common,agent-core agent-admin

    # 앱 디렉터리, 실행 파일, 환경 파일과 키를 컨테이너에 설치한다.
    install -d -m 2770 -o agent-admin -g agent-core /home/agent-admin/agent-app
    install -d -m 2770 -o agent-admin -g agent-common /home/agent-admin/agent-app/upload_files
    install -d -m 2770 -o agent-admin -g agent-core /home/agent-admin/agent-app/api_keys /home/agent-admin/agent-app/bin /var/log/agent-app
    install -m 0750 -o agent-admin -g agent-core "/provided/'"$APP_FILE"'" /home/agent-admin/agent-app/agent_app
    install -m 0750 -o agent-admin -g agent-core /mission/11_monitor.sh /home/agent-admin/agent-app/bin/monitor.sh
    install -m 0750 -o agent-admin -g agent-core /mission/12_report.sh /home/agent-admin/agent-app/bin/report.sh
    install -d -m 0750 -o root -g agent-core /etc/agent-app
    install -m 0640 -o root -g agent-core /mission/05_agent.env.example /etc/agent-app/agent.env
    printf "%s\n" agent_api_key_test > /home/agent-admin/agent-app/api_keys/secret.key
    chown agent-admin:agent-core /home/agent-admin/agent-app/api_keys/secret.key
    chmod 0640 /home/agent-admin/agent-app/api_keys/secret.key

    # 컨테이너 종료 전에 백그라운드 앱을 정리한다.
    stop_app() { pkill -TERM -x agent_app >/dev/null 2>&1 || true; }
    trap stop_app EXIT

    # root가 아닌 agent-admin으로 제공 앱을 실행한다.
    su -s /bin/bash -c "set -a; source /etc/agent-app/agent.env; set +a; exec /home/agent-admin/agent-app/agent_app" agent-admin > /tmp/agent-app.out 2>&1 &

    # 최대 20초 동안 Agent READY 출력을 기다린다.
    ready=0
    for _ in $(seq 1 20); do
      if grep -q "Agent READY" /tmp/agent-app.out 2>/dev/null; then ready=1; break; fi
      sleep 1
    done
    cat /tmp/agent-app.out
    [[ $ready -eq 1 ]] || { echo "[FAIL] Agent READY was not observed." >&2; exit 1; }

    # 모니터링과 통계 리포트까지 연속으로 점검한다.
    echo
    echo "===== MONITOR SMOKE TEST ====="
    su -s /bin/bash -c "AGENT_ENV_FILE=/etc/agent-app/agent.env /home/agent-admin/agent-app/bin/monitor.sh" agent-admin
    echo
    echo "===== REPORT SMOKE TEST ====="
    su -s /bin/bash -c "/home/agent-admin/agent-app/bin/report.sh" agent-admin
    echo
    echo "[PASS] Provided app, port 15034, monitor log, and report were verified."
  '

echo "[PASS] Docker smoke test completed. The test container was removed automatically."
