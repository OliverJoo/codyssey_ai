# b1-1 컴퓨터가 알아서 자기 상태를 점검하게 만들기

이 폴더는 `b1-1.pdf`의 필수 요구사항을 Ubuntu 22.04 이상에서 직접 구성하고 검증하기 위한 학습용 실행 세트다. 먼저 Linux 환경을 준비한 다음 보안, 계정/권한, 제공 앱, 모니터링, cron, 증거 수집 순서로 진행한다.

파일명 앞의 번호가 곧 학습·시연 순서다. `01` 안내 → `02` 전체 흐름 → `03` 휴대용 Docker 예행연습 → `04`~`09` 시스템 구성 → `10` 앱 실행 → `11`~`13` 모니터링·통계·보존 → `14`~`15` 검증·증거 수집 → `16`~`17` 질문 답변·튜토리얼 순으로 살펴본다.

> **중요:** `04_setup.sh`는 SSH 포트와 방화벽을 변경한다. 개인용 Mac이나 운영 서버에서 직접 실행하지 말고, 새 Ubuntu VM에서 실행한다. SSH 설정을 바꾸는 동안에는 VM 콘솔을 닫지 않는다.

## 0. 가장 먼저: Mac에 Linux 실습 환경 만들기

### Mac 아키텍처 확인

```bash
uname -m
```

| Mac | 결과 | Ubuntu/제공 앱 |
|---|---|---|
| M1/M2/M3/M4 Mac | `arm64` | Ubuntu ARM64, `agent-app-linux-arm64` |
| Intel iMac/MacBook | `x86_64` | Ubuntu AMD64, `agent-app-linux-x86` |

`04_setup.sh`와 `03_portable_lab.sh`가 아키텍처를 자동 판별한다. 다른 아키텍처의 바이너리를 억지로 실행하지 않는다.

### 방법 A - UTM의 완전한 Ubuntu VM (권장, Docker/OrbStack 외 방법 1)

이 미션은 `sshd`, UFW, 다중 사용자, ACL, cron을 다루므로 가장 예측 가능한 방식이다.

1. [UTM](https://mac.getutm.app/)을 설치한다.
2. M3는 Ubuntu Server ARM64 ISO, Intel iMac은 Ubuntu AMD64 ISO를 받는다.
3. UTM에서 **+ → Virtualize → Linux**를 선택한다.
4. CPU 2개 이상, 메모리 4GB, 디스크 25GB 이상을 배정하고 Ubuntu를 설치한다.
5. Ubuntu에서 다음을 확인한다.

```bash
uname -m
cat /etc/os-release
```

UTM 공식 Ubuntu 안내: <https://docs.getutm.app/guides/ubuntu/>

### 방법 B - Canonical Multipass VM (권장, Docker/OrbStack 외 방법 2)

macOS 13.3 이상인 M 시리즈와 Intel Mac에서 모두 사용할 수 있다.

1. [공식 Multipass 설치 안내](https://documentation.ubuntu.com/multipass/en/latest/how-to-guides/install-multipass/)의 macOS `.pkg`를 설치한다.
2. 터미널에서 VM을 만든다.

```bash
multipass launch 22.04 --name b1-1 --cpus 2 --memory 4G --disk 25G
multipass mount "/Users/$USER/Dev/codyssey/2026/codyssey_missions/AI_SW/01_Basic/b1-1" b1-1:/home/ubuntu/b1-1
multipass shell b1-1
cd /home/ubuntu/b1-1
```

### 방법 C - OrbStack Ubuntu 머신

OrbStack의 Linux machine은 init system과 `systemctl`을 지원하므로 일반 컨테이너보다 이 미션에 적합하다.

```bash
orb create ubuntu:jammy b1-1
orb -m b1-1
cd /mnt/mac/Users/$USER/Dev/codyssey/2026/codyssey_missions/AI_SW/01_Basic/b1-1
```

공식 안내: <https://docs.orbstack.dev/machines/>

### 방법 D - Docker Desktop 휴대용 스모크 테스트

Docker는 제공 앱/포트/모니터/리포트의 빠른 확인용이다. 컨테이너 네트워크 안의 UFW는 Mac으로 들어오는 실제 트래픽을 보호하지 않으므로 **SSH·UFW 제출 증거는 UTM, Multipass 또는 OrbStack Linux machine에서 만든다.**

Docker Desktop을 실행한 뒤 이 폴더에서 단일 파일을 실행한다.

```bash
chmod +x 03_portable_lab.sh
./03_portable_lab.sh
```

이 파일은 M3에서 ARM64 앱, Intel iMac에서 x86-64 앱을 자동 선택한다. 테스트 컨테이너에는 `--rm`이 적용되고 종료/중단 시 정리 트랩이 실행된다. 공식 설치 안내: <https://docs.docker.com/desktop/setup/install/mac-install/>

## 1. 10분 빠른 시작 - 완전한 Ubuntu VM

### 1-1. 실행 권한 부여

```bash
cd /path/to/b1-1
chmod +x 03_portable_lab.sh 04_setup.sh 10_run_agent.sh 11_monitor.sh 12_report.sh 13_archive_logs.sh 14_verify_mission.sh 15_collect_evidence.sh
```

### 1-2. 시스템 구성

```bash
sudo ./04_setup.sh
```

확인 질문을 건너뛸 때만 `sudo ./04_setup.sh --yes`를 사용한다. 스크립트가 수행하는 작업은 다음과 같다.

- SSH 포트 `20022`, `PermitRootLogin no`
- UFW 기본 인바운드 거부, TCP `20022`, `15034` 허용
- `agent-admin`, `agent-dev`, `agent-test`와 `agent-common`, `agent-core` 생성
- 공유/보안 디렉터리, setgid, ACL 설정
- 호스트 아키텍처에 맞는 제공 앱 설치
- `monitor.sh`, cron, logrotate, 선택 보너스 보존 cron 설치

### 1-3. SSH 로그인용 학습 계정 암호 설정

```bash
sudo passwd agent-admin
hostname -I
```

Mac의 새 터미널에서 접속한다.

```bash
ssh -p 20022 agent-admin@<VM_IP>
```

성공하기 전에는 기존 VM 콘솔을 닫지 않는다.

### 1-4. 제공 앱 실행

VM 터미널 1:

```bash
sudo -iu agent-admin /home/agent-admin/agent-app/bin/run_agent.sh
```

성공하면 Boot Sequence 5단계가 모두 `[OK]`이고 `Agent READY`가 나온다. 앱은 자원 사용량을 단계적으로 바꾸는 학습 프로그램이므로 CPU/MEM 경고가 발생하는 것이 정상이다. 종료는 `Ctrl+C`다.

### 1-5. 수동 모니터링과 통계

VM 터미널 2:

```bash
sudo -u agent-admin /home/agent-admin/agent-app/bin/monitor.sh
sudo -u agent-admin /home/agent-admin/agent-app/bin/report.sh
tail -n 5 /var/log/agent-app/monitor.log
```

### 1-6. cron 자동 증가 확인

```bash
sudo crontab -u agent-admin -l
before=$(sudo wc -l < /var/log/agent-app/monitor.log)
sleep 70
after=$(sudo wc -l < /var/log/agent-app/monitor.log)
printf 'before=%s after=%s\n' "$before" "$after"
```

`after`가 더 크면 매분 자동 실행이 확인된 것이다.

### 1-7. 전체 검증과 제출 증거 수집

```bash
sudo ./14_verify_mission.sh
sudo ./15_collect_evidence.sh
```

`mission-evidence-YYYYMMDD-HHMMSS.txt`가 이 폴더에 생성된다. 계정/그룹, ACL, SSH, UFW, 프로세스, 포트, monitor 로그, cron을 한 파일에 기록하되 키 값은 노출하지 않는다.

## 2. 제공 앱 기준으로 확인된 주의사항

제공된 두 파일은 Linux ELF 실행 파일이며 소스 코드가 아니다.

| 파일 | CPU |
|---|---|
| `agent-app/agent-app-linux-arm64` | Linux ARM64/aarch64 (M3용 VM) |
| `agent-app/agent-app-linux-x86` | Linux x86-64 (Intel용 VM) |

### PDF와 제공 바이너리의 키 경로 차이

Docker에서 제공 ARM64 앱을 단계별로 실제 실행한 결과, 바이너리의 검사는 PDF 문구와 다음처럼 다르다.

| 항목 | PDF 표기 | 제공 바이너리가 실제 요구하는 값 |
|---|---|---|
| `AGENT_KEY_PATH` | `.../api_keys/t_secret.key` | `/home/agent-admin/agent-app/api_keys` **디렉터리** |
| 키 파일명 | `t_secret.key` | `secret.key` |
| 키 내용 | `agent_api_key_test` | `agent_api_key_test` |

실행 가능한 제공물이 더 구체적인 판정 기준이므로 이 세트는 바이너리 기준을 따른다. `04_setup.sh`는 `/home/agent-admin/agent-app/api_keys/secret.key`를 만들고 `AGENT_KEY_PATH`에는 디렉터리를 넣는다.

## 3. 전체 흐름 다이어그램

[설정부터 제출까지의 Process 다이어그램 열기](02_mission-flow.html)

다이어그램은 설치한 `diagram-design` 플러그인의 Process 유형 규칙(역할 lane, 단계, 입력/출력, 단일 focal 단계)을 적용한 HTML이다. 상단에서 75%~200% 배율을 선택할 수 있고 키보드 Tab·방향키도 지원하며, 확대 후 가로 스크롤로 이동할 수 있다.

## 4. 파일 안내

| 파일 | 역할 |
|---|---|
| [01_README.md](01_README.md) | 환경 준비부터 제출까지의 번호순 학습 안내 |
| [02_mission-flow.html](02_mission-flow.html) | 플러그인으로 설계한 확대·축소 가능 Process 다이어그램 |
| [03_portable_lab.sh](03_portable_lab.sh) | M3/Intel Mac 공용 Docker 단일 진입점, 종료 후 컨테이너 제거 |
| [04_setup.sh](04_setup.sh) | Ubuntu 패키지, SSH, UFW, 계정/그룹, ACL, 제공 앱, cron 구성 |
| [05_agent.env.example](05_agent.env.example) | 제공 앱의 환경 변수 원본 |
| [06_sshd-agent-mission.conf](06_sshd-agent-mission.conf) | SSH 20022/Root 차단 drop-in |
| [07_agent-admin.cron](07_agent-admin.cron) | agent-admin의 매분 monitor 실행 규칙 |
| [08_agent-app-monitor.logrotate](08_agent-app-monitor.logrotate) | 10MB 기준, 총 10개 계열 파일 유지 정책 |
| [09_agent-app-archive.cron](09_agent-app-archive.cron) | 보너스 보존 스크립트의 일일 실행 규칙 |
| [10_run_agent.sh](10_run_agent.sh) | 환경 파일을 읽고 제공 바이너리를 일반 계정으로 실행 |
| [11_monitor.sh](11_monitor.sh) | 프로세스/15034 포트 health check, 방화벽 경고, CPU/MEM/DISK 수집·기록 |
| [12_report.sh](12_report.sh) | monitor.log의 CPU/MEM/DISK 평균·최대·최소·샘플 수 계산 |
| [13_archive_logs.sh](13_archive_logs.sh) | 7일 지난 `.log` 압축·이동, 30일 지난 `.gz` 삭제 |
| [14_verify_mission.sh](14_verify_mission.sh) | 필수 요구사항 자동 PASS/FAIL 판정 |
| [15_collect_evidence.sh](15_collect_evidence.sh) | 제출용 수행 내역 텍스트 수집 |
| [16_README_answer.md](16_README_answer.md) | 질문 이미지의 19개 질문과 답, 개념 튜토리얼 |
| [17_README_answer.html](17_README_answer.html) | 답변을 스크롤하며 학습하는 브라우저 문서 |

## 5. 권한 설계

| 대상 | 소유자 | 그룹 | 모드/ACL | 의도 |
|---|---|---|---|---|
| `upload_files` | agent-admin | agent-common | `2770`, common rwx | 세 역할이 협업 |
| `api_keys` | agent-admin | agent-core | `2770`, core rwx | test의 비밀 접근 차단 |
| `/var/log/agent-app` | agent-admin | agent-core | `2770`, core rwx | 운영자/개발자만 로그 접근 |
| `monitor.sh` | agent-dev | agent-core | `750` | dev가 소유, admin이 그룹 실행 |
| `secret.key` | agent-admin | agent-core | `640` | 실행 계정 읽기, 외부 사용자 차단 |

`2`가 붙은 `2770`의 setgid 비트 때문에 새 파일/하위 디렉터리가 부모 그룹을 물려받는다. 기본 ACL은 새 파일에도 협업 정책이 이어지게 한다.

## 6. monitor.sh 동작

1. 제공 앱 프로세스 이름 `agent_app`을 정확히 찾지 못하면 `[ERROR]` 후 `exit 1`.
2. TCP 15034가 LISTEN이 아니면 `[ERROR]` 후 `exit 1`.
3. UFW/firewalld가 비활성이거나 조회되지 않으면 `[WARNING]`만 출력하고 계속.
4. `/proc/stat`, `/proc/meminfo`, `df -P /`에서 CPU/MEM/DISK를 구한다.
5. CPU `>20`, MEM `>10`, DISK `>80`이면 경고만 출력한다.
6. 아래 형식으로 누적한다.

```text
[YYYY-MM-DD HH:MM:SS] PID:1234 CPU:12.3% MEM:8.4% DISK_USED:27%
```

7. `monitor.log`가 10MB 이상이면 자체 회전하여 활성 파일 + `.1`~`.9`, 총 10개를 유지한다. 시스템 `logrotate` 정책도 함께 제공한다.

## 7. report.sh 사용

전체 기간:

```bash
sudo -u agent-admin /home/agent-admin/agent-app/bin/report.sh
```

기간 필터:

```bash
sudo -u agent-admin /home/agent-admin/agent-app/bin/report.sh \
  --from '2026-09-02 09:00:00' \
  --to   '2026-09-02 10:00:00'
```

다른 로그 파일:

```bash
./12_report.sh --log ./sample-monitor.log
```

## 8. 보너스 로그 보존 정책

수동 시험:

```bash
sudo ./13_archive_logs.sh
```

- `/var/log/agent-app/*.log` 중 7일이 지난 파일을 gzip으로 압축
- `/var/log/monitor/agent-app/archive/`로 이동
- 보관소의 `.gz` 중 30일이 지난 파일 삭제
- 대상이 0개여도 오류 없이 개수를 출력

## 9. 수동 증거 체크리스트

자동 증거 파일과 함께 아래 화면을 캡처하면 좋다.

```bash
sudo sshd -T | grep -E '^(port|permitrootlogin) '
sudo ss -tulnp | grep -E ':(20022|15034)\b'
sudo ufw status verbose
id agent-admin && id agent-dev && id agent-test
sudo getfacl /home/agent-admin/agent-app/upload_files
sudo getfacl /home/agent-admin/agent-app/api_keys
stat -c '%U:%G %a %n' /home/agent-admin/agent-app/bin/monitor.sh
sudo tail -n 10 /var/log/agent-app/monitor.log
sudo crontab -u agent-admin -l
```

## 10. 트러블슈팅

### `Key Path Mismatch` 또는 `Missing File: secret.key`

```bash
grep AGENT_KEY_PATH /etc/agent-app/agent.env
sudo ls -l /home/agent-admin/agent-app/api_keys/secret.key
```

`AGENT_KEY_PATH`는 파일이 아니라 `.../api_keys` 디렉터리여야 한다.

### 앱은 켜졌는데 monitor가 프로세스를 못 찾음

```bash
pgrep -a -x agent_app
grep AGENT_EXECUTABLE /etc/agent-app/agent.env
```

앱을 임의의 다른 경로/이름으로 옮겼다면 환경 파일도 맞춘다.

### SSH 변경 후 접속 안 됨

VM 콘솔에서 다음을 확인한다.

```bash
sudo sshd -t
sudo systemctl status ssh --no-pager
sudo ss -ltnp | grep 20022
sudo ufw status
```

### cron 로그가 늘지 않음

```bash
sudo systemctl status cron --no-pager
sudo crontab -u agent-admin -l
sudo tail -n 50 /var/log/agent-app/cron.log
```

앱이 먼저 실행 중이어야 monitor health check가 성공한다.

## 11. 제출 전 최종 확인

- [ ] 5단계 `[OK]`와 `Agent READY`
- [ ] SSH TCP 20022, `PermitRootLogin no`
- [ ] UFW active, 20022/tcp와 15034/tcp만 ALLOW
- [ ] 세 계정, 두 그룹, agent-test의 agent-core 제외
- [ ] upload/common과 api_keys·log/core ACL
- [ ] `monitor.sh`가 `agent-dev:agent-core 750`
- [ ] 프로세스/포트 실패 시 exit 1
- [ ] monitor.log 형식과 누적
- [ ] agent-admin cron 등록 후 1분 뒤 로그 증가
- [ ] 10MB/10개 회전 정책
- [ ] `16_README_answer.md`의 19개 답변 복습
- [ ] `mission-evidence-*.txt` 생성

## 원문

- 과제: [b1-1.pdf](b1-1.pdf)
- 평가 질문 이미지: 원본은 별도 answer 폴더의 `b1-1.webp`
