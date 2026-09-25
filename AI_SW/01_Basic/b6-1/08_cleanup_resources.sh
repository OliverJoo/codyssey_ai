#!/usr/bin/env bash
# 이 프로젝트가 만든 AWS 리소스만 의존성의 역순으로 삭제하고 잔존 여부를 검증한다.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/.state"
STATE_FILE="$STATE_DIR/resources.env"
if [[ ! -r "$STATE_FILE" ]]; then
  echo "[PASS] 활성 상태 파일이 없어 정리할 대상이 없습니다."
  exit 0
fi
# shellcheck disable=SC1090
source "$STATE_FILE"

die() { echo "[ERROR] $*" >&2; exit 1; }
pass() { echo "[PASS] $*"; }

# VPC가 남아 있다면 ID와 Project 태그가 모두 일치해야만 진행한다.
VPC_ID_COUNT="$(aws ec2 describe-vpcs --region "$AWS_REGION" --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'length(Vpcs)' --output text)"
VPC_MATCH_COUNT="$(aws ec2 describe-vpcs --region "$AWS_REGION" \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Project,Values=$PROJECT_NAME" \
  --query 'length(Vpcs)' --output text)"
[[ "$VPC_ID_COUNT" == "0" || "$VPC_MATCH_COUNT" == "1" ]] || \
  die "VPC ID와 Project 태그가 일치하지 않아 중단합니다."

echo "삭제 대상: project=$PROJECT_NAME region=$AWS_REGION instance=$INSTANCE_ID vpc=$VPC_ID"
read -r -p "모두 삭제하려면 DELETE를 입력하세요: " answer
[[ "$answer" == "DELETE" ]] || { echo "취소했습니다."; exit 0; }

RETRY_ATTEMPTS="${B6_CLEANUP_ATTEMPTS:-18}"
RETRY_SLEEP="${B6_CLEANUP_SLEEP:-10}"
retry() {
  local attempt
  for ((attempt=1; attempt<=RETRY_ATTEMPTS; attempt++)); do
    if "$@"; then
      return 0
    fi
    echo "[WAIT] 자원 의존성 해제 $attempt/$RETRY_ATTEMPTS: $*" >&2
    sleep "$RETRY_SLEEP"
  done
  return 1
}

# EC2를 먼저 종료하고 ENI/EBS 해제를 기다린다.
INSTANCE_STATE="$(aws ec2 describe-instances --region "$AWS_REGION" \
  --filters "Name=instance-id,Values=$INSTANCE_ID" --query 'Reservations[0].Instances[0].State.Name' --output text)"
if [[ -n "$INSTANCE_STATE" && "$INSTANCE_STATE" != "None" && "$INSTANCE_STATE" != "terminated" ]]; then
  aws ec2 terminate-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" >/dev/null
  aws ec2 wait instance-terminated --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
fi
pass "EC2 terminated"

# 네트워크 리소스는 연결의 역순으로 제거한다. 중간 실패 후 재실행해도
# 이미 삭제된 자원은 건너뛰고, 실패를 숨기지 않고 잠시 재시도한다.
ROUTE_TABLE_COUNT="$(aws ec2 describe-route-tables --region "$AWS_REGION" \
  --filters "Name=route-table-id,Values=$ROUTE_TABLE_ID" --query 'length(RouteTables)' --output text)"
if [[ "$ROUTE_TABLE_COUNT" == "1" ]]; then
  ROUTE_ASSOC_COUNT="$(aws ec2 describe-route-tables --region "$AWS_REGION" \
    --route-table-ids "$ROUTE_TABLE_ID" \
    --query "length(RouteTables[0].Associations[?RouteTableAssociationId=='$ROUTE_ASSOC_ID'])" --output text)"
  [[ "$ROUTE_ASSOC_COUNT" == "0" ]] || aws ec2 disassociate-route-table --region "$AWS_REGION" --association-id "$ROUTE_ASSOC_ID"
  retry aws ec2 delete-route-table --region "$AWS_REGION" --route-table-id "$ROUTE_TABLE_ID"
fi

SG_COUNT="$(aws ec2 describe-security-groups --region "$AWS_REGION" \
  --filters "Name=group-id,Values=$SG_ID" --query 'length(SecurityGroups)' --output text)"
[[ "$SG_COUNT" == "0" ]] || retry aws ec2 delete-security-group --region "$AWS_REGION" --group-id "$SG_ID"

SUBNET_COUNT="$(aws ec2 describe-subnets --region "$AWS_REGION" \
  --filters "Name=subnet-id,Values=$SUBNET_ID" --query 'length(Subnets)' --output text)"
[[ "$SUBNET_COUNT" == "0" ]] || retry aws ec2 delete-subnet --region "$AWS_REGION" --subnet-id "$SUBNET_ID"

IGW_COUNT="$(aws ec2 describe-internet-gateways --region "$AWS_REGION" \
  --filters "Name=internet-gateway-id,Values=$IGW_ID" --query 'length(InternetGateways)' --output text)"
if [[ "$IGW_COUNT" == "1" ]]; then
  IGW_ATTACHED_COUNT="$(aws ec2 describe-internet-gateways --region "$AWS_REGION" \
    --internet-gateway-ids "$IGW_ID" \
    --query "length(InternetGateways[0].Attachments[?VpcId=='$VPC_ID'])" --output text)"
  [[ "$IGW_ATTACHED_COUNT" == "0" ]] || \
    aws ec2 detach-internet-gateway --region "$AWS_REGION" --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"
  retry aws ec2 delete-internet-gateway --region "$AWS_REGION" --internet-gateway-id "$IGW_ID"
fi

VPC_ID_COUNT="$(aws ec2 describe-vpcs --region "$AWS_REGION" --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'length(Vpcs)' --output text)"
[[ "$VPC_ID_COUNT" == "0" ]] || retry aws ec2 delete-vpc --region "$AWS_REGION" --vpc-id "$VPC_ID"

# 이 스크립트가 만든 키페어만 정리한다.
if [[ "${KEY_CREATED:-0}" == "1" ]]; then
  KEY_COUNT="$(aws ec2 describe-key-pairs --region "$AWS_REGION" \
    --filters "Name=key-name,Values=$KEY_NAME" --query 'length(KeyPairs)' --output text)"
  [[ "$KEY_COUNT" == "0" ]] || aws ec2 delete-key-pair --region "$AWS_REGION" --key-name "$KEY_NAME"
fi

# PDF의 EC2/EBS/EIP/IGW/VPC 정리 항목을 Project 태그로 재조회한다.
remaining_count() {
  local service="$1" query="$2"
  shift 2
  aws ec2 "$service" --region "$AWS_REGION" "$@" --query "$query" --output text
}

for ((attempt=1; attempt<=RETRY_ATTEMPTS; attempt++)); do
  INSTANCE_COUNT="$(remaining_count describe-instances \
    "length(Reservations[].Instances[?State.Name!='terminated'][])" \
    --filters "Name=tag:Project,Values=$PROJECT_NAME")"
  VOLUME_COUNT="$(remaining_count describe-volumes 'length(Volumes)' \
    --filters "Name=tag:Project,Values=$PROJECT_NAME")"
  ADDRESS_COUNT="$(remaining_count describe-addresses 'length(Addresses)' \
    --filters "Name=tag:Project,Values=$PROJECT_NAME")"
  IGW_COUNT="$(remaining_count describe-internet-gateways 'length(InternetGateways)' \
    --filters "Name=tag:Project,Values=$PROJECT_NAME")"
  VPC_COUNT="$(remaining_count describe-vpcs 'length(Vpcs)' \
    --filters "Name=tag:Project,Values=$PROJECT_NAME")"
  if [[ "$INSTANCE_COUNT,$VOLUME_COUNT,$ADDRESS_COUNT,$IGW_COUNT,$VPC_COUNT" == "0,0,0,0,0" ]]; then
    break
  fi
  echo "[WAIT] remaining instance=$INSTANCE_COUNT ebs=$VOLUME_COUNT eip=$ADDRESS_COUNT igw=$IGW_COUNT vpc=$VPC_COUNT"
  sleep "$RETRY_SLEEP"
done
[[ "$INSTANCE_COUNT,$VOLUME_COUNT,$ADDRESS_COUNT,$IGW_COUNT,$VPC_COUNT" == "0,0,0,0,0" ]] || \
  die "잔존 리소스가 있어 상태 파일을 보존합니다."
pass "EC2/EBS/EIP/IGW/VPC 잔존 자원 0개"

# 모든 AWS 검증을 통과한 뒤만 민감한 로컬 키와 활성 상태를 제거한다.
printf 'Cleaned: %s\nProject: %s\nRegion: %s\n' \
  "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$PROJECT_NAME" "$AWS_REGION" > "$STATE_DIR/last-cleanup.txt"
rm -f "$STATE_DIR/key.pem" "$STATE_DIR/known_hosts" "$STATE_DIR/user-data.sh" "$STATE_FILE"
chmod 0600 "$STATE_DIR/last-cleanup.txt"

echo "[DONE] 필수 리소스 삭제와 재검증이 끝났습니다. 상태 파일을 제거해 재실행 가능합니다."
echo "Billing Dashboard와 docs/cleanup-checklist.md는 반드시 사람이 마지막으로 확인하세요."
