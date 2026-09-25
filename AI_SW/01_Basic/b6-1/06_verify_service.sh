#!/usr/bin/env bash
# PDF의 네트워크·보안·EC2·내부/외부 통신 조건을 읽기 전용으로 검증한다.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/.state"
STATE_FILE="$STATE_DIR/resources.env"
[[ -r "$STATE_FILE" ]] || { echo "[ERROR] 먼저 04_create_infrastructure.sh를 실행하세요." >&2; exit 1; }
# shellcheck disable=SC1090
source "$STATE_FILE"

pass() { echo "[PASS] $*"; }
fail() { echo "[FAIL] $*" >&2; exit 1; }

for command in aws curl ssh grep; do
  command -v "$command" >/dev/null 2>&1 || fail "명령을 찾을 수 없습니다: $command"
done

# VPC, Public Subnet, IGW, Subnet-Route Table 연결과 기본 경로를 각각 확인한다.
VPC_FACTS="$(aws ec2 describe-vpcs --region "$AWS_REGION" --vpc-ids "$VPC_ID" \
  --query 'Vpcs[0].[State,CidrBlock]' --output text)"
[[ "$VPC_FACTS" == $'available\t'"$VPC_CIDR" ]] && pass "VPC available, CIDR=$VPC_CIDR" || fail "VPC: $VPC_FACTS"

SUBNET_FACTS="$(aws ec2 describe-subnets --region "$AWS_REGION" --subnet-ids "$SUBNET_ID" \
  --query 'Subnets[0].[VpcId,CidrBlock,MapPublicIpOnLaunch]' --output text)"
[[ "$SUBNET_FACTS" == "$VPC_ID"$'\t'"$SUBNET_CIDR"$'\t'True ]] && \
  pass "Public Subnet CIDR/auto-assign public IPv4" || fail "Subnet: $SUBNET_FACTS"

ATTACHED_VPC="$(aws ec2 describe-internet-gateways --region "$AWS_REGION" --internet-gateway-ids "$IGW_ID" \
  --query 'InternetGateways[0].Attachments[0].VpcId' --output text)"
[[ "$ATTACHED_VPC" == "$VPC_ID" ]] && pass "IGW -> VPC attached" || fail "IGW attachment=$ATTACHED_VPC"

ROUTE_GATEWAY="$(aws ec2 describe-route-tables --region "$AWS_REGION" --route-table-ids "$ROUTE_TABLE_ID" \
  --query "RouteTables[0].Routes[?DestinationCidrBlock=='0.0.0.0/0' && State=='active'].GatewayId | [0]" --output text)"
ROUTE_SUBNET="$(aws ec2 describe-route-tables --region "$AWS_REGION" --route-table-ids "$ROUTE_TABLE_ID" \
  --query "RouteTables[0].Associations[?SubnetId=='$SUBNET_ID'].SubnetId | [0]" --output text)"
[[ "$ROUTE_GATEWAY" == "$IGW_ID" ]] && pass "0.0.0.0/0 -> IGW active" || fail "Route gateway=$ROUTE_GATEWAY"
[[ "$ROUTE_SUBNET" == "$SUBNET_ID" ]] && pass "Route Table -> Public Subnet associated" || fail "Route association"

# SG 인바운드는 TCP 80 공개와 TCP 22 학습자 /32, 두 규칙만 허용한다.
INGRESS_COUNT="$(aws ec2 describe-security-group-rules --region "$AWS_REGION" \
  --filters Name=group-id,Values="$SG_ID" --query 'length(SecurityGroupRules[?IsEgress==`false`])' --output text)"
HTTP_SOURCE="$(aws ec2 describe-security-group-rules --region "$AWS_REGION" --filters Name=group-id,Values="$SG_ID" \
  --query "SecurityGroupRules[?IsEgress==\`false\` && IpProtocol=='tcp' && FromPort==\`80\` && ToPort==\`80\`].CidrIpv4 | [0]" --output text)"
SSH_SOURCE="$(aws ec2 describe-security-group-rules --region "$AWS_REGION" --filters Name=group-id,Values="$SG_ID" \
  --query "SecurityGroupRules[?IsEgress==\`false\` && IpProtocol=='tcp' && FromPort==\`22\` && ToPort==\`22\`].CidrIpv4 | [0]" --output text)"
[[ "$INGRESS_COUNT" == "2" ]] || fail "SG 인바운드가 2개가 아닙니다: $INGRESS_COUNT"
[[ "$HTTP_SOURCE" == "0.0.0.0/0" ]] && pass "HTTP 80 public" || fail "HTTP source=$HTTP_SOURCE"
[[ "$SSH_SOURCE" == "$SSH_CIDR" ]] && pass "SSH 22 learner only: $SSH_SOURCE" || fail "SSH source=$SSH_SOURCE expected=$SSH_CIDR"

# EC2가 의도한 Subnet/SG/타입/퍼블릭 IP를 사용하며 루트 EBS가 8GiB 자동 삭제인지 확인한다.
INSTANCE_FACTS="$(aws ec2 describe-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].[State.Name,InstanceType,SubnetId,PublicIpAddress,SecurityGroups[0].GroupId]' --output text)"
EXPECTED_INSTANCE="running"$'\t'"$INSTANCE_TYPE"$'\t'"$SUBNET_ID"$'\t'"$PUBLIC_IP"$'\t'"$SG_ID"
[[ "$INSTANCE_FACTS" == "$EXPECTED_INSTANCE" ]] && pass "EC2 running/type/subnet/public-IP/SG" || fail "EC2: $INSTANCE_FACTS"

ROOT_DEVICE="$(aws ec2 describe-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].[Ebs.VolumeId,Ebs.DeleteOnTermination]' --output text)"
[[ "$ROOT_DEVICE" == "$VOLUME_ID"$'\t'True ]] && pass "Root EBS DeleteOnTermination=true" || fail "Root EBS: $ROOT_DEVICE"
VOLUME_SIZE="$(aws ec2 describe-volumes --region "$AWS_REGION" --volume-ids "$VOLUME_ID" \
  --query 'Volumes[0].Size' --output text)"
[[ "$VOLUME_SIZE" == "8" ]] && pass "Root EBS size=8GiB" || fail "EBS size=$VOLUME_SIZE"

aws ec2 wait instance-status-ok --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
pass "EC2 system/instance status checks OK"

# cloud-init을 기다리며 외부에서 /health 200 + OK를 확인한다.
VERIFY_ATTEMPTS="${B6_VERIFY_ATTEMPTS:-30}"
VERIFY_SLEEP="${B6_VERIFY_SLEEP:-10}"
echo "[INFO] Nginx 초기화를 최대 $((VERIFY_ATTEMPTS * VERIFY_SLEEP))초 기다립니다."
external_ok=0
for ((attempt=1; attempt<=VERIFY_ATTEMPTS; attempt++)); do
  if RESPONSE="$(curl --connect-timeout 5 --max-time 10 --fail --silent "http://$PUBLIC_IP/health" 2>/dev/null)" && \
     [[ "$RESPONSE" == "OK" ]]; then
    external_ok=1
    break
  fi
  echo "[WAIT] external /health $attempt/$VERIFY_ATTEMPTS"
  sleep "$VERIFY_SLEEP"
done
[[ "$external_ok" == "1" ]] && pass "External GET /health -> 200 OK" || fail "http://$PUBLIC_IP/health"

# 외부 루트 페이지가 실제 작성한 웹 소스이며 정상 응답하는지 확인한다.
ROOT_PAGE="$(curl --connect-timeout 5 --max-time 10 --fail --silent "http://$PUBLIC_IP/")" || fail "http://$PUBLIC_IP/"
grep -q 'data-project="codyssey-b6-1"' <<< "$ROOT_PAGE" && \
  grep -q 'Codyssey Cloud Lab' <<< "$ROOT_PAGE" && \
  pass "External GET / -> 200, authored web page" || fail "외부 루트 페이지 내용 불일치"

# SSH 접속, Nginx, localhost /health, 아웃바운드 인터넷을 인스턴스 안에서 검증한다.
KNOWN_HOSTS="$STATE_DIR/known_hosts"
REMOTE_CHECK='set -e; test -f /var/lib/codyssey-b6-1-ready; sudo systemctl is-active --quiet nginx; test "$(curl --fail --silent http://localhost/health)" = "OK"; curl --fail --silent http://localhost/ | grep -q "data-project=\"codyssey-b6-1\""; curl --fail --silent --max-time 15 https://checkip.amazonaws.com >/dev/null'
ssh -i "$STATE_DIR/key.pem" -o BatchMode=yes -o ConnectTimeout=10 \
  -o StrictHostKeyChecking=accept-new -o "UserKnownHostsFile=$KNOWN_HOSTS" \
  "${SSH_USER:-ec2-user}@$PUBLIC_IP" "$REMOTE_CHECK"
pass "SSH + Nginx + localhost / and /health + outbound internet"

echo "[PASS] PDF 필수 인프라/서비스 조건 자동 검증 완료"
