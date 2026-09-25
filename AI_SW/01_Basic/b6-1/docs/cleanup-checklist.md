# b6-1 리소스 정리 체크리스트

실습 종료 후 레포 루트에서 다음을 실행하고 콘솔 또는 AWS CLI로 다시 확인한다. 체크 시각과 근거를 함께 적는다.

```bash
bash AI_SW/01_Basic/b6-1/08_cleanup_resources.sh
```

`AI_SW/01_Basic/b6-1`에서 실행한다면 `bash 08_cleanup_resources.sh`를 사용한다.

> 현재 배포는 사용자의 직접 확인을 위해 유지 중이다. 아래 항목은 사용자가 정리를 지시한 뒤 실행하고 체크한다.

| 필수 확인 | 완료 | 확인 근거/시각 |
|---|---|---|
| EC2 인스턴스가 `terminated`인가? | [ ] | 현재 `running` — 후속 확인 후 정리 예정 |
| Project 태그의 EBS 볼륨이 남지 않았는가? | [ ] | 현재 8GiB gp3 사용 중 — 후속 확인 후 정리 예정 |
| Elastic IP를 할당했다면 Release했는가? 이 기본 스크립트는 EIP를 만들지 않는다. | [x] | Elastic IP를 생성하지 않음 |
| Internet Gateway가 Detach 및 삭제됐는가? | [ ] | 현재 웹 접속을 위해 연결 상태 유지 |
| VPC, Public Subnet, 사용자 Route Table, Security Group이 삭제됐는가? | [ ] | 현재 웹 접속을 위해 유지 |

## 생성했다면 확인할 선택 리소스

| 추가 확인 | 해당 없음/완료 | 근거 |
|---|---|---|
| NAT Gateway 삭제 | 해당 없음 | 생성하지 않음 |
| ALB/ELB 및 Target Group 삭제 | 해당 없음 | 생성하지 않음 |
| RDS 삭제 | 해당 없음 | 생성하지 않음 |
| EBS Snapshot/AMI 확인 | 해당 없음 | 스냅샷과 사용자 AMI를 생성하지 않음 |

## CLI 확인 명령

```bash
aws ec2 describe-instances --region ap-northeast-2 \
  --filters Name=tag:Project,Values=codyssey-b6-1
aws ec2 describe-volumes --region ap-northeast-2 \
  --filters Name=tag:Project,Values=codyssey-b6-1
aws ec2 describe-addresses --region ap-northeast-2
aws ec2 describe-internet-gateways --region ap-northeast-2 \
  --filters Name=tag:Project,Values=codyssey-b6-1
aws ec2 describe-vpcs --region ap-northeast-2 \
  --filters Name=tag:Project,Values=codyssey-b6-1
```

## 마지막 확인

- [ ] 사용자 확인 후 AWS CLI로 `Project=codyssey-b6-1`의 EC2/EBS/EIP/IGW/VPC/Subnet/Route Table/Security Group/Key Pair 잔존 수 0을 확인한다.
- [ ] 정리 확인 결과를 `docs/evidence/05-cleanup-verified.png`로 저장한다(선택).
- [ ] Billing Dashboard 확인은 PDF의 권장 항목이다. 정리 후 계정 소유자가 콘솔에서 확인한다.
