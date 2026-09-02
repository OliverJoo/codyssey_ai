#!/usr/bin/env bash
# 환경 파일을 읽고 제공 앱을 올바른 사용자로 실행한다.
set -Eeuo pipefail

# 설치된 환경 파일이 읽을 수 있는지 확인한다.
ENV_FILE="${AGENT_ENV_FILE:-/etc/agent-app/agent.env}"
if [[ ! -r "$ENV_FILE" ]]; then
  echo "[ERROR] Cannot read environment file: $ENV_FILE" >&2
  exit 1
fi

# source한 값을 하위 앱에도 전달하도록 export한다.
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# root 실행을 막고 지정된 서비스 계정만 허용한다.
if [[ "$(id -un)" != "${AGENT_RUN_USER:-agent-admin}" ]]; then
  echo "[ERROR] Run this as ${AGENT_RUN_USER:-agent-admin}, not $(id -un)." >&2
  exit 1
fi

# 바이너리 존재와 실행 권한을 확인한다.
if [[ ! -x "${AGENT_EXECUTABLE:-$AGENT_HOME/agent_app}" ]]; then
  echo "[ERROR] Provided app is not executable: ${AGENT_EXECUTABLE:-$AGENT_HOME/agent_app}" >&2
  exit 1
fi

# 셸 프로세스를 앱 프로세스로 교체한다.
exec "${AGENT_EXECUTABLE:-$AGENT_HOME/agent_app}"
