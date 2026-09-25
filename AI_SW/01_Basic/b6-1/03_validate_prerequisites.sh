#!/usr/bin/env bash
# AWS 리소스를 만들기 전에 도구·계정·리전·설정을 읽기 전용으로 검사한다.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${B6_CONFIG_FILE:-$SCRIPT_DIR/config.env}"

die() { echo "[ERROR] $*" >&2; exit 1; }
pass() { echo "[PASS] $*"; }

# 필수 로컬 명령을 확인한다.
for command in aws curl ssh; do
  command -v "$command" >/dev/null 2>&1 || die "명령을 찾을 수 없습니다: $command"
  pass "$command 명령 확인"
done

# 사용자가 작성한 환경 설정을 읽는다.
[[ -r "$CONFIG_FILE" ]] || die "먼저 02_config.env.example을 config.env로 복사하세요."
set -a
# shellcheck disable=SC1090
source "$CONFIG_FILE"
set +a

# 과제 조건과 위험한 SSH 공개 설정을 차단한다.
[[ "${AWS_REGION:-}" == "ap-northeast-2" ]] || die "AWS_REGION은 ap-northeast-2여야 합니다."
[[ "${SSH_CIDR:-}" != "CHANGE_ME/32" && "${SSH_CIDR:-}" != "0.0.0.0/0" ]] || \
  die "SSH_CIDR을 현재 공인 IP/32로 설정하세요."
[[ "${SSH_CIDR:-}" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}/32$ ]] || \
  die "SSH_CIDR은 현재 공인 IPv4 하나를 /32로 입력하세요. 예: 203.0.113.10/32"
IFS='./' read -r octet1 octet2 octet3 octet4 prefix <<< "$SSH_CIDR"
for octet in "$octet1" "$octet2" "$octet3" "$octet4"; do
  (( 10#$octet <= 255 )) || die "SSH_CIDR에 유효하지 않은 IPv4 옥텋이 있습니다: $octet"
done
[[ "$prefix" == "32" ]] || die "SSH_CIDR 접두사는 /32여야 합니다."
[[ "${INSTANCE_TYPE:-}" == "t2.micro" || "${INSTANCE_TYPE:-}" == "t3.micro" ]] || \
  die "INSTANCE_TYPE은 과제 범위인 t2.micro 또는 t3.micro여야 합니다."
[[ "${PROJECT_NAME:-}" =~ ^[A-Za-z0-9._-]+$ ]] || die "PROJECT_NAME은 영문·숫자·._-만 사용하세요."
pass "서울 리전과 SSH 제한 설정 확인"

# 현재 자격 증명과 리전 접근 가능 여부를 확인한다.
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
CALLER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
aws ec2 describe-availability-zones --region "$AWS_REGION" >/dev/null
pass "AWS 인증 확인: account=$ACCOUNT_ID"
pass "호출 주체: $CALLER_ARN"

echo
echo "[READY] 사전 검사가 끝났습니다. 다음: ./04_create_infrastructure.sh"
