#!/usr/bin/env bash
# VPC부터 EC2 웹 서버까지 과제의 필수 AWS 리소스를 순서대로 생성한다.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${B6_CONFIG_FILE:-$SCRIPT_DIR/config.env}"
STATE_DIR="$SCRIPT_DIR/.state"
STATE_FILE="$STATE_DIR/resources.env"

die() { echo "[ERROR] $*" >&2; exit 1; }
step() { echo; echo "[$1/9] $2"; }

trap 'echo "[ERROR] 생성이 중단됐습니다. .state/resources.env의 ID와 Project 태그를 확인한 뒤 08_cleanup_resources.sh로 정리하세요." >&2' ERR

[[ -r "$CONFIG_FILE" ]] || die "config.env가 없습니다. 02_config.env.example을 복사해 수정하세요."
set -a
# shellcheck disable=SC1090
source "$CONFIG_FILE"
set +a

# 생성 전 필수 도구·AWS 자격 증명·CIDR·micro 타입을 같은 기준으로 검사한다.
bash "$SCRIPT_DIR/03_validate_prerequisites.sh"

# 서울 리전과 제한된 SSH 소스를 다시 검증한다.
[[ "${AWS_REGION:-}" == "ap-northeast-2" ]] || die "서울 리전만 허용합니다."
[[ "${SSH_CIDR:-}" != "CHANGE_ME/32" && "${SSH_CIDR:-}" != "0.0.0.0/0" ]] || \
  die "SSH_CIDR을 본인 공인 IP/32로 제한하세요."
[[ ! -e "$STATE_FILE" ]] || die "$STATE_FILE이 이미 있습니다. 기존 리소스를 먼저 확인하거나 정리하세요."

# 상태 파일을 잃었더라도 동일 Project 태그 자원을 중복 생성하지 않는다.
EXISTING_VPCS="$(aws ec2 describe-vpcs --region "$AWS_REGION" \
  --filters "Name=tag:Project,Values=$PROJECT_NAME" --query 'Vpcs[].VpcId' --output text)"
[[ -z "$EXISTING_VPCS" || "$EXISTING_VPCS" == "None" ]] || \
  die "Project=$PROJECT_NAME VPC가 이미 있습니다: $EXISTING_VPCS"

# 기존 키와 이름이 충돌하면 리소스를 만들기 전에 중단한다.
if aws ec2 describe-key-pairs --region "$AWS_REGION" --key-names "$KEY_NAME" >/dev/null 2>&1; then
  die "AWS에 $KEY_NAME 키가 이미 있습니다. KEY_NAME을 바꾸거나 기존 키를 안전하게 확인하세요."
fi

mkdir -p "$STATE_DIR"
chmod 0700 "$STATE_DIR"

# 생성된 ID를 즉시 기록해 중간 실패 때도 추적할 수 있게 한다.
save_state() {
  local temporary_state
  temporary_state="$(mktemp "$STATE_DIR/resources.env.tmp.XXXXXX")"
  {
    printf 'AWS_REGION=%q\n' "$AWS_REGION"
    printf 'PROJECT_NAME=%q\n' "$PROJECT_NAME"
    printf 'KEY_NAME=%q\n' "$KEY_NAME"
    printf 'KEY_CREATED=%q\n' "${KEY_CREATED:-0}"
    printf 'SSH_CIDR=%q\n' "$SSH_CIDR"
    printf 'VPC_CIDR=%q\n' "$VPC_CIDR"
    printf 'SUBNET_CIDR=%q\n' "$SUBNET_CIDR"
    printf 'INSTANCE_TYPE=%q\n' "$INSTANCE_TYPE"
    printf 'AZ=%q\n' "${AZ:-}"
    printf 'AMI_ID=%q\n' "${AMI_ID:-}"
    printf 'VPC_ID=%q\n' "${VPC_ID:-}"
    printf 'SUBNET_ID=%q\n' "${SUBNET_ID:-}"
    printf 'IGW_ID=%q\n' "${IGW_ID:-}"
    printf 'ROUTE_TABLE_ID=%q\n' "${ROUTE_TABLE_ID:-}"
    printf 'ROUTE_ASSOC_ID=%q\n' "${ROUTE_ASSOC_ID:-}"
    printf 'SG_ID=%q\n' "${SG_ID:-}"
    printf 'INSTANCE_ID=%q\n' "${INSTANCE_ID:-}"
    printf 'VOLUME_ID=%q\n' "${VOLUME_ID:-}"
    printf 'PUBLIC_IP=%q\n' "${PUBLIC_IP:-}"
    printf 'SSH_USER=%q\n' "ec2-user"
  } > "$temporary_state"
  chmod 0600 "$temporary_state"
  mv "$temporary_state" "$STATE_FILE"
}

step 1 "가용 영역과 최신 Amazon Linux 2023 AMI 조회"
AZ="$(aws ec2 describe-availability-zones --region "$AWS_REGION" \
  --filters Name=state,Values=available --query 'AvailabilityZones[0].ZoneName' --output text)"
AMI_ID="$(aws ssm get-parameter --region "$AWS_REGION" --name "$AMI_SSM_PARAMETER" \
  --query 'Parameter.Value' --output text)"
echo "AZ=$AZ AMI=$AMI_ID"

step 2 "VPC 생성"
VPC_ID="$(aws ec2 create-vpc --region "$AWS_REGION" --cidr-block "$VPC_CIDR" \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$PROJECT_NAME-vpc},{Key=Project,Value=$PROJECT_NAME}]" \
  --query 'Vpc.VpcId' --output text)"
save_state
aws ec2 modify-vpc-attribute --region "$AWS_REGION" --vpc-id "$VPC_ID" --enable-dns-support '{"Value":true}'
aws ec2 modify-vpc-attribute --region "$AWS_REGION" --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'

step 3 "Public Subnet 생성"
SUBNET_ID="$(aws ec2 create-subnet --region "$AWS_REGION" --vpc-id "$VPC_ID" \
  --cidr-block "$SUBNET_CIDR" --availability-zone "$AZ" \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public},{Key=Project,Value=$PROJECT_NAME}]" \
  --query 'Subnet.SubnetId' --output text)"
save_state
aws ec2 modify-subnet-attribute --region "$AWS_REGION" --subnet-id "$SUBNET_ID" --map-public-ip-on-launch

step 4 "Internet Gateway 생성 및 연결"
IGW_ID="$(aws ec2 create-internet-gateway --region "$AWS_REGION" \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$PROJECT_NAME-igw},{Key=Project,Value=$PROJECT_NAME}]" \
  --query 'InternetGateway.InternetGatewayId' --output text)"
save_state
aws ec2 attach-internet-gateway --region "$AWS_REGION" --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"

step 5 "Route Table과 0.0.0.0/0 경로 구성"
ROUTE_TABLE_ID="$(aws ec2 create-route-table --region "$AWS_REGION" --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$PROJECT_NAME-public-rt},{Key=Project,Value=$PROJECT_NAME}]" \
  --query 'RouteTable.RouteTableId' --output text)"
save_state
aws ec2 create-route --region "$AWS_REGION" --route-table-id "$ROUTE_TABLE_ID" \
  --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID" >/dev/null
ROUTE_ASSOC_ID="$(aws ec2 associate-route-table --region "$AWS_REGION" --route-table-id "$ROUTE_TABLE_ID" \
  --subnet-id "$SUBNET_ID" --query 'AssociationId' --output text)"
save_state

step 6 "HTTP 공개·SSH 개인 IP 제한 Security Group 생성"
SG_ID="$(aws ec2 create-security-group --region "$AWS_REGION" --group-name "$PROJECT_NAME-web-sg" \
  --description 'Codyssey b6-1 HTTP public, SSH learner IP only' --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=$PROJECT_NAME-web-sg},{Key=Project,Value=$PROJECT_NAME}]" \
  --query 'GroupId' --output text)"
save_state
aws ec2 authorize-security-group-ingress --region "$AWS_REGION" --group-id "$SG_ID" \
  --ip-permissions "IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0,Description='Public HTTP'}]" \
                   "IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=$SSH_CIDR,Description='Learner SSH'}]" >/dev/null

step 7 "실습 전용 키페어 생성"
aws ec2 create-key-pair --region "$AWS_REGION" --key-name "$KEY_NAME" \
  --key-type ed25519 --key-format pem --query 'KeyMaterial' --output text > "$STATE_DIR/key.pem"
chmod 0400 "$STATE_DIR/key.pem"
KEY_CREATED=1
save_state

step 8 "EC2 생성 및 Nginx 자동 설치"
# 별도 관리하는 웹 페이지 원본을 user-data 환경 변수에 넣어 실제 EC2에 배포한다.
WEB_SOURCE="$SCRIPT_DIR/web/index.html"
[[ -r "$WEB_SOURCE" ]] || die "웹 페이지 원본이 없습니다: $WEB_SOURCE"
USER_DATA_FILE="$STATE_DIR/user-data.sh"
{
  printf '#!/usr/bin/env bash\n'
  printf 'export CODYSSEY_PAGE_BASE64=%q\n' "$(base64 < "$WEB_SOURCE" | tr -d '\n')"
  tail -n +2 "$SCRIPT_DIR/05_user_data.sh"
} > "$USER_DATA_FILE"
chmod 0600 "$USER_DATA_FILE"
INSTANCE_ID="$(aws ec2 run-instances --region "$AWS_REGION" --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" --subnet-id "$SUBNET_ID" --security-group-ids "$SG_ID" \
  --key-name "$KEY_NAME" --associate-public-ip-address \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":8,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
  --metadata-options 'HttpTokens=required,HttpEndpoint=enabled' \
  --user-data "file://$USER_DATA_FILE" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-web},{Key=Project,Value=$PROJECT_NAME}]" \
                       "ResourceType=volume,Tags=[{Key=Name,Value=$PROJECT_NAME-root},{Key=Project,Value=$PROJECT_NAME}]" \
  --query 'Instances[0].InstanceId' --output text)"
rm -f "$USER_DATA_FILE"
save_state
aws ec2 wait instance-running --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
VOLUME_ID="$(aws ec2 describe-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId' --output text)"
PUBLIC_IP="$(aws ec2 describe-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)"
save_state

step 9 "생성 완료"
echo "Instance : $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Web      : http://$PUBLIC_IP/"
echo "Health   : http://$PUBLIC_IP/health"
echo "SSH      : ssh -i $STATE_DIR/key.pem ec2-user@$PUBLIC_IP"
echo
echo "user-data 설치에 1~3분 걸릴 수 있습니다. 다음: ./06_verify_service.sh"
