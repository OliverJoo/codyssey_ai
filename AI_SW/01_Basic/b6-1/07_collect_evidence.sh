#!/usr/bin/env bash
# 제출용 AWS 구성과 접속 결과를 텍스트 증거로 수집한다.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="$SCRIPT_DIR/.state/resources.env"
EVIDENCE_DIR="$SCRIPT_DIR/docs/evidence"
[[ -r "$STATE_FILE" ]] || { echo "[ERROR] 리소스 상태 파일이 없습니다." >&2; exit 1; }
# shellcheck disable=SC1090
source "$STATE_FILE"

# 구성·SSH·내부/외부 통신이 모두 성공한 상태만 증거로 수집한다.
"$SCRIPT_DIR/06_verify_service.sh"

mkdir -p "$EVIDENCE_DIR"
OUTPUT="$EVIDENCE_DIR/aws-evidence-$(date '+%Y%m%d-%H%M%S').txt"

section() { printf '\n===== %s =====\n' "$1"; }
run() { printf '\n$ %s\n' "$*"; "$@" 2>&1 || printf '[exit=%d]\n' "$?"; }

# 비밀 키는 수집하지 않고 평가에 필요한 리소스 정보만 남긴다.
{
  echo "Codyssey b6-1 AWS evidence"
  echo "Collected: $(date '+%Y-%m-%dT%H:%M:%S%z')"
  echo "Region: $AWS_REGION"
  section "Caller"
  run aws sts get-caller-identity
  section "VPC and Subnet"
  run aws ec2 describe-vpcs --region "$AWS_REGION" --vpc-ids "$VPC_ID"
  run aws ec2 describe-subnets --region "$AWS_REGION" --subnet-ids "$SUBNET_ID"
  section "Internet Gateway and Route Table"
  run aws ec2 describe-internet-gateways --region "$AWS_REGION" --internet-gateway-ids "$IGW_ID"
  run aws ec2 describe-route-tables --region "$AWS_REGION" --route-table-ids "$ROUTE_TABLE_ID"
  section "Security Group"
  run aws ec2 describe-security-group-rules --region "$AWS_REGION" --filters Name=group-id,Values="$SG_ID"
  section "EC2 and EBS"
  run aws ec2 describe-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
  run aws ec2 describe-volumes --region "$AWS_REGION" --filters Name=attachment.instance-id,Values="$INSTANCE_ID"
  section "External health check"
  run curl --include --max-time 10 "http://$PUBLIC_IP/health"
} > "$OUTPUT"

chmod 0600 "$OUTPUT"
echo "[PASS] 증거 파일: $OUTPUT"
echo "브라우저 또는 터미널 화면도 PNG로 캡처해 docs/evidence/에 추가하세요."
