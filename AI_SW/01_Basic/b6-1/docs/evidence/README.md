# 제출 증거 저장 위치

다음 이름을 권장한다.

1. `00-web-page.png` - 외부에서 받은 루트 웹 페이지의 실제 렌더링
2. `01-health-check.png` - 외부 `GET /health`의 200/OK
3. `02-ec2-running.png` - EC2 running, `t3.micro`, 퍼블릭 IP, 8GiB gp3
4. `03-security-group.png` - HTTP 80 전체, SSH 22 개인 IPv4 `/32`
5. `04-route-table.png` - Public Subnet 연결과 `0.0.0.0/0 -> igw-*` active

2026-09-25 실제 배포에서 수집했다. 현재 웹 페이지와 `/health`는 `52.78.119.46`에서 접근 가능하다. 리소스는 사용자의 후속 확인이 끝날 때까지 유지한다.

`07_collect_evidence.sh`가 만드는 `aws-evidence-*.txt`도 이 폴더에 저장된다. 개인키, Access Key, Secret Key는 절대 캡처하거나 제출하지 않는다.
