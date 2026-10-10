# b6-1 트러블슈팅 보고서

## 사건 1 - Amazon Linux 2023에서 Nginx 설치 실패

| 단계 | 실제 수행 기록 |
|---|---|
| 증상 | EC2 생성과 상태 검사는 통과했지만 `06_verify_service.sh`가 외부 `/health` 응답을 기다리다 실패했다. SSH 접속은 가능했으며 `systemctl is-active nginx`는 서비스를 찾지 못했다. |
| 가설 | ① cloud-init이 아직 완료되지 않음 ② Nginx 패키지 설치 실패 ③ Nginx 설정 오류 ④ SG/Route/IGW 문제를 후보로 두었다. |
| 검증 | SSH로 `cloud-init status --long`, `systemctl status nginx`, cloud-init 출력 로그를 확인했다. AWS API에서는 SG의 80/22 규칙, active 기본 경로, IGW 연결, public IP가 모두 정상이었다. |
| 발견 | Amazon Linux 2023에 기본 설치된 `curl-minimal`과 사용자 데이터의 `dnf install -y nginx curl`이 충돌했다. 패키지 트랜잭션이 중단되어 Nginx가 설치되지 않았고 외부 연결이 거부됐다. |
| 조치 | `05_user_data.sh`의 Amazon Linux 분기에서 이미 제공되는 curl을 다시 설치하지 않고 `dnf install -y nginx`만 실행하도록 수정했다. 수정된 사용자 데이터를 SSH로 다시 실행했다. |
| 결과 | Nginx가 `active`가 되었고 인스턴스 내부 `curl localhost/health`, 아웃바운드 HTTPS, 외부 `GET /health`가 모두 통과했다. 외부 응답은 `HTTP/1.1 200 OK`, 본문은 `OK`였다. 이후 `06_verify_service.sh`와 `07_collect_evidence.sh`가 전체 통과했다. |
| 재발 방지 | 테스트가 Amazon Linux 분기의 `dnf install`에 `curl`을 다시 넣으면 실패하도록 회귀 검사를 추가했다. 배포 검증은 cloud-init 완료 여부와 Nginx 상태를 SSH로 확인한다. |

## 사건 2 - AWS CLI 옵션 호환성 오류

| 단계 | 실제 수행 기록 |
|---|---|
| 증상 | 사전 검사에서 AWS CLI가 `Unknown options: --max-results, 5`를 반환했다. |
| 가설 | 사용 중인 AWS CLI 버전의 해당 명령이 `--max-results` 옵션을 지원하지 않는 것으로 판단했다. |
| 검증 | 같은 명령을 옵션 없이 실행해 정상 응답을 확인하고 CLI 도움말의 지원 옵션을 대조했다. |
| 조치 | `03_validate_prerequisites.sh`에서 호환되지 않는 `--max-results 5`를 제거했다. |
| 결과 | 사전 검사의 AWS 인증·리전·도구·SSH 제한 검사가 모두 통과했다. |
| 재발 방지 | 테스트에서 사전 검사 스크립트에 해당 옵션이 다시 들어오지 않는지 확인한다. |
