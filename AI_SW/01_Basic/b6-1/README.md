# b6-1 - AWS에 안전한 공개 웹 서비스 배포하기

이 폴더는 `b6-1.pdf`의 필수 요구사항을 AWS CLI로 재현한다. 서울 리전(`ap-northeast-2`)에 VPC, Public Subnet, Internet Gateway, Route Table, Security Group, EC2/Nginx를 생성하고 외부 검증 방식 **B: `GET /health` -> `200 OK` + `OK`**를 사용한다.

> 현재 상태: 2026-09-25에 IAM 사용자와 AWS CLI로 서울 리전에 실제 배포했다. 전체 인프라·SSH·Nginx·내부 및 외부 통신 검증과 증거 수집을 통과했다. 사용자가 직접 확인할 수 있도록 리소스는 현재 유지 중이며, 정리는 사용자 요청 후 `08_cleanup_resources.sh`로 수행한다.

- 웹 페이지: <http://52.78.119.46/>
- 방식 B 헬스체크: <http://52.78.119.46/health> (`200 OK`, 본문 `OK`)

## PDF 요구사항 대조

| PDF 항목 | 구현/산출물 | 현재 검증 |
|---|---|---|
| VPC, Public Subnet, IGW, `0.0.0.0/0 -> IGW` | `04_create_infrastructure.sh` | 실제 생성 및 `06` 속성/연결 검증 통과 |
| EC2 micro, 8GiB, SSH, Nginx | `04`, `05`, `06` | 실제 `t3.micro`, 8GiB gp3, SSH/Nginx 검증 통과 |
| SG: 80 공개, 22 학습자 `/32` | `03`, `04`, `06` | 실제 인바운드 규칙 2개와 소스 범위 검증 통과 |
| 외부 방식 B `/health` | `05`, `06`, `07` | 실제 외부 `HTTP/1.1 200 OK`, 본문 `OK` 확인 |
| 아키텍처 PNG | `docs/architecture.png` | VPC/Subnet/IGW/EC2/SG/요청 흐름 시각 확인 |
| 트러블슈팅 보고서 | `docs/troubleshooting.md` | 실제 cloud-init/Nginx 장애의 분석·해결·재발 방지 기록 |
| EC2/EBS/EIP/IGW/VPC 정리 | `08`, `docs/cleanup-checklist.md` | 정리 절차·검증 구현 완료; 사용자 확인을 위해 현재 리소스 유지 중 |
| IAM 최소권한 | `iam/least-privilege-policy.json` | 필요한 EC2/VPC 작업만 성공, IAM 조회는 `AccessDenied`, 관리자 권한 미사용 |

## 파일 구성

| 파일 | 역할 |
|---|---|
| [01_architecture.html](01_architecture.html) | 확대 가능한 아키텍처 SVG |
| [docs/architecture.png](docs/architecture.png) | PDF 제출용 PNG |
| [02_config.env.example](02_config.env.example) | 리전, CIDR, 인스턴스 설정 예시 |
| [03_validate_prerequisites.sh](03_validate_prerequisites.sh) | 도구·AWS 인증·`/32`·micro 타입 사전 검사 |
| [04_create_infrastructure.sh](04_create_infrastructure.sh) | VPC부터 EC2까지 생성, 상태 ID 저장 |
| [05_user_data.sh](05_user_data.sh) | Amazon Linux/Ubuntu Nginx와 `/health` 구성 |
| [web/index.html](web/index.html) | 실제 EC2에 배포되는 반응형 웹 페이지 원본 |
| [06_verify_service.sh](06_verify_service.sh) | AWS 속성, SG, SSH, 내부/외부 통신 검증 |
| [07_collect_evidence.sh](07_collect_evidence.sh) | 전체 검증 후 텍스트 증거 수집 |
| [08_cleanup_resources.sh](08_cleanup_resources.sh) | 역순 삭제, 잔존 자원 재조회, 재실행 상태 복구 |
| [tests/test_workflow.py](tests/test_workflow.py) | 비용 없는 2회 전체 생명주기 테스트 |

## 1. `conda py312` 검증 환경

레포 루트에서 다음처럼 실행한다.

```bash
cd /Users/oliverjoo/Dev/codyssey/2026/codyssey_missions
source /Users/oliverjoo/Dev/Anaconda/anaconda3/etc/profile.d/conda.sh
conda activate py312
python --version
```

이 검토에서 확인한 값은 `Python 3.12.2`다. 셸 스크립트 실행에 Python이 필수인 것은 아니지만, 요구된 환경에서 자동 검증을 통일했다.

```bash
python -m unittest discover \
  -s AI_SW/01_Basic/b6-1/tests \
  -p 'test_*.py' -v
```

테스트는 실제 AWS를 호출하지 않고 다음을 검증한다.

1. 생성 -> 구성/SSH/내부·외부 통신 검증 -> 증거 수집 -> 정리
2. 상태 파일과 개인키 제거
3. 같은 과정을 다시 생성·정리
4. 잘못된 IPv4 옥텋 거부, IAM 금지 권한, AWS JMESPath 필터

## 2. 실제 AWS 실행 시 주의

- 루트 계정과 `AdministratorAccess`를 사용하지 않는다.
- `t2.micro`/`t3.micro`가 자신의 계정에서 무료 대상인지 직접 확인한다.
- 실습 전 AWS Budget/비용 알림을 설정한다.
- 개인키, Access Key, Secret Key를 Git·스크린샷에 포함하지 않는다.
- 최종 확인이 끝난 즉시 `08_cleanup_resources.sh`를 실행한다.

IAM 예시는 [iam/least-privilege-policy.json](iam/least-privilege-policy.json)이다. 계정의 SCP·Permission Boundary에 따라 IAM 관리자와 조정할 수 있다.

## 3. 설정 작성

레포 루트에서:

```bash
cp AI_SW/01_Basic/b6-1/02_config.env.example \
   AI_SW/01_Basic/b6-1/config.env
curl -4 https://checkip.amazonaws.com
```

`AI_SW/01_Basic/b6-1/config.env`의 `SSH_CIDR`에 현재 공인 IPv4와 `/32`를 입력한다.

```bash
SSH_CIDR="203.0.113.10/32"
```

`0.0.0.0/0`, `CHANGE_ME/32`, `/32`가 아닌 대역, `999.0.0.1/32` 같은 잘못된 IPv4는 `03` 단계에서 거부된다.

## 4. 배포·검증·증거 수집

레포 루트에서 실제로 실행되는 명령은 다음과 같다. 각 스크립트는 자신의 위치를 기준으로 파일을 찾으므로 레포 루트에서 호출해도 된다.

```bash
bash AI_SW/01_Basic/b6-1/03_validate_prerequisites.sh
bash AI_SW/01_Basic/b6-1/04_create_infrastructure.sh
bash AI_SW/01_Basic/b6-1/06_verify_service.sh
bash AI_SW/01_Basic/b6-1/07_collect_evidence.sh
```

`04` 생성 순서:

1. Amazon Linux 2023 AMI와 AZ 조회
2. VPC `10.0.0.0/16`
3. Public Subnet `10.0.1.0/24`, public IPv4 자동 할당
4. IGW 생성/연결
5. Route Table, `0.0.0.0/0 -> IGW`, Subnet 연결
6. SG: TCP 80 `0.0.0.0/0`, TCP 22 `SSH_CIDR`
7. ED25519 키페어
8. micro EC2, 8GiB gp3, `DeleteOnTermination=true`, IMDSv2 필수
9. Nginx에 `web/index.html`과 `/health` 배포

`06` 검증 범위:

- VPC/Subnet CIDR, public IPv4 자동 할당
- IGW-VPC 연결, Route Table-Subnet 연결, active 기본 경로
- 인바운드 규칙이 80/22 두 개뿐인지와 SSH 소스 일치
- EC2 타입/Subnet/SG/public IP, 8GiB EBS 자동 삭제
- EC2 system/instance status check
- 외부 `GET /`의 작성된 페이지와 `GET /health`의 200/OK
- SSH 접속 후 Nginx, `localhost/`, `localhost/health`, 아웃바운드 HTTPS

프로젝트 디렉터리에서 실행하고 싶다면 다음도 같다.

```bash
cd AI_SW/01_Basic/b6-1
bash 03_validate_prerequisites.sh
bash 04_create_infrastructure.sh
bash 06_verify_service.sh
bash 07_collect_evidence.sh
```

## 5. 제출 증거

`07_collect_evidence.sh`는 먼저 `06_verify_service.sh`를 다시 통과한 뒤 `docs/evidence/aws-evidence-*.txt`를 만들었다. 아래 PNG는 현재 활성 배포의 외부 응답과 AWS API 결과를 수집해 만든 제출 증거다.

1. [00-web-page.png](docs/evidence/00-web-page.png): 외부에서 받은 실제 루트 HTML의 렌더링 결과
2. [01-health-check.png](docs/evidence/01-health-check.png): 방식 B, URL `http://52.78.119.46/health`, 외부 `200 OK`/`OK`
3. [02-ec2-running.png](docs/evidence/02-ec2-running.png): EC2 `running`, `t3.micro`, public IP, 8GiB gp3
4. [03-security-group.png](docs/evidence/03-security-group.png): HTTP 80 전체, SSH 22 학습자 IPv4 `/32`
5. [04-route-table.png](docs/evidence/04-route-table.png): `0.0.0.0/0 -> igw-*` active와 Subnet 연결

외부 접속 검증은 **방식 B**를 사용했다. 루트 페이지는 외부에서 `200 OK`로 받은 파일과 [web/index.html](web/index.html)의 SHA-256이 일치하는지도 확인했다. 실제 장애와 해결 과정은 [docs/troubleshooting.md](docs/troubleshooting.md)에 `증상 -> 가설 -> 검증 -> 조치 -> 결과 -> 재발 방지` 순서로 기록했다.

## 6. 정리와 재실행

레포 루트에서:

```bash
bash AI_SW/01_Basic/b6-1/08_cleanup_resources.sh
```

스크립트는 VPC ID와 `Project` 태그를 대조한 후 `DELETE` 입력을 요구한다. EC2 -> Route Table 연결/Route Table -> SG -> Subnet -> IGW -> VPC -> Key Pair 순으로 정리하고 EC2/EBS/EIP/IGW/VPC 잔존 수가 모두 0인지 재조회한다.

전체 검증이 성공해야 `.state/resources.env`와 `.state/key.pem`을 제거한다. 이후 `04_create_infrastructure.sh`를 다시 실행할 수 있다. 중간 실패 시 상태 파일을 남겨 재실행 또는 수동 확인을 가능하게 한다.

현재 배포는 사용자의 후속 확인을 위해 유지한다. 확인이 끝나면 위 명령을 실행하고 [docs/cleanup-checklist.md](docs/cleanup-checklist.md)에 EC2, EBS, EIP, IGW, VPC와 종속 리소스의 삭제 근거를 기록한다. Billing Dashboard 확인은 PDF의 권장 항목이다.

## 7. 아키텍처 PNG 재생성

macOS와 `py312`에서 HTML의 inline SVG를 PNG로 재생성할 수 있다.

```bash
python AI_SW/01_Basic/b6-1/tests/render_architecture.py
```

## 제출 전 최종 체크

- [x] 실제 AWS 배포에서 `06_verify_service.sh`가 통과했다.
- [x] `docs/architecture.png`에 VPC/Subnet/IGW/EC2/SG와 외부 흐름이 보인다.
- [x] 외부 `/health` 200/OK 스크린샷과 URL/IP가 있다.
- [x] `docs/troubleshooting.md`에 실제 장애 1건 이상을 기록했다.
- [ ] 사용자 확인 후 `08_cleanup_resources.sh`와 정리 체크리스트를 완료한다.
- [ ] 사용자 확인 후 프로젝트 태그의 필수·종속 리소스 잔존 수 0을 확인한다.
- [x] 비밀정보·개인키·Access Key가 제출물에 없다.
- [ ] Billing Dashboard 확인은 PDF의 선택/권장 항목이며 정리 후 계정 소유자가 콘솔에서 확인한다.

## 원문

- 과제: [b6-1.pdf](b6-1.pdf)
- 평가 질문 해설: [README_answer.md](README_answer.md), [README_answer.html](README_answer.html)
