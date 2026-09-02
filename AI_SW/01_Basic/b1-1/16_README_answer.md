# b1-1 평가 질문과 답변

이 문서는 `b1-1.webp`의 평가 항목을 질문과 답변으로 구분해 정리한 것이다. 답변은 `b1-1.pdf`, 이 폴더의 Bash 구현, 그리고 제공 Linux 앱을 Docker Ubuntu 22.04에서 실제 실행한 결과를 기준으로 작성했다.

> **제공 앱 우선 기준:** PDF에는 `AGENT_KEY_PATH=.../api_keys/t_secret.key`라고 적혀 있지만, 실제 제공 바이너리는 `AGENT_KEY_PATH=/home/agent-admin/agent-app/api_keys`와 그 안의 `secret.key`를 요구한다. 키 내용은 `agent_api_key_test`다.

## 항목 1 - 필수 결과가 실제로 동작하는가

### Q1. SSH 포트가 20022로 변경되었고, Root 원격 접속이 차단되었는가?

관련 파일: [06_sshd-agent-mission.conf](06_sshd-agent-mission.conf) · [04_setup.sh](04_setup.sh) · [14_verify_mission.sh](14_verify_mission.sh)

**답변**

`06_sshd-agent-mission.conf`에 `Port 20022`, `PermitRootLogin no`를 선언하고 `04_setup.sh`가 `/etc/ssh/sshd_config.d/00-agent-mission.conf`로 설치한다. 설정 파일만 보는 것보다 sshd의 최종 해석과 실제 리슨 상태를 함께 확인해야 한다.

```bash
sudo sshd -T | grep -E '^(port|permitrootlogin) '
sudo ss -ltnp | grep ':20022'
```

기대 결과는 `port 20022`, `permitrootlogin no`, 그리고 TCP 20022의 LISTEN 행이다.

### Q2. 방화벽이 활성화되어 있고, 20022/tcp와 15034/tcp만 허용되는가?

관련 파일: [04_setup.sh](04_setup.sh) · [14_verify_mission.sh](14_verify_mission.sh)

**답변**

`04_setup.sh`는 UFW 기본 인바운드를 deny로, 아웃바운드를 allow로 정하고 TCP 20022(SSH), TCP 15034(APP)를 허용한다.

```bash
sudo ufw status verbose
```

`Status: active`와 두 ALLOW 규칙을 확인한다. 기존 VM에 다른 ALLOW 규칙이 있으면 “두 포트만”이라는 평가 기준에 어긋날 수 있으므로 새 실습 VM을 쓰는 것이 안전하다. `14_verify_mission.sh`는 추가 ALLOW 규칙도 실패로 표시한다.

### Q3. agent-admin/dev/test 계정과 agent-common/core 그룹이 요구사항대로 구성되어 있는가?

관련 파일: [04_setup.sh](04_setup.sh) · [14_verify_mission.sh](14_verify_mission.sh)

**답변**

- `agent-common`: agent-admin, agent-dev, agent-test 모두 포함
- `agent-core`: agent-admin, agent-dev만 포함
- agent-test: agent-core에 포함하지 않음

```bash
id agent-admin
id agent-dev
id agent-test
```

agent-test를 core에서 제외해야 API 키와 운영 로그에 QA 사용자가 접근하지 못한다.

### Q4. 앱이 Boot Sequence 5단계를 모두 [OK]로 통과하고 “Agent READY”를 출력하는가?

관련 파일: [05_agent.env.example](05_agent.env.example) · [10_run_agent.sh](10_run_agent.sh) · [03_portable_lab.sh](03_portable_lab.sh)

**답변**

다음과 같이 일반 계정으로 실행한다.

```bash
sudo -iu agent-admin /home/agent-admin/agent-app/bin/run_agent.sh
```

성공 조건은 아래 다섯 검사와 마지막 메시지다.

1. 실행 사용자가 root가 아닌 `agent-admin`
2. `AGENT_HOME`, `AGENT_PORT`, `AGENT_UPLOAD_DIR`, `AGENT_KEY_PATH`가 올바름
3. `$AGENT_KEY_PATH/secret.key`가 존재하고 내용이 `agent_api_key_test`
4. TCP 15034를 사용할 수 있음
5. `/var/log/agent-app`에 쓰기 가능

그 뒤 `All Boot Checks Passed!`, `Agent READY`, `Agent listening at port 15034`가 나온다.

### Q5. monitor.sh가 프로세스/포트 상태를 점검하고, 비정상 상태에서 exit 1로 종료되는가?

관련 파일: [11_monitor.sh](11_monitor.sh) · [14_verify_mission.sh](14_verify_mission.sh)

**답변**

`monitor.sh`는 설치 시 제공 앱 이름을 `agent_app`으로 고정하고 `pgrep -x`로 정확히 일치하는 프로세스를 찾으며, `ss -ltnH`로 15034 리슨을 확인한다. 둘 중 하나라도 실패하면 `die()`가 `[ERROR]`를 stderr로 출력하고 `exit 1` 한다.

```bash
sudo -u agent-admin /home/agent-admin/agent-app/bin/monitor.sh
echo "$?"
```

앱 실행 중에는 0, 앱 종료 후에는 1이 기대된다. 방화벽 비활성은 health check 실패가 아니라 경고이므로 1로 종료하지 않는다.

### Q6. `/var/log/agent-app/monitor.log`가 지정 포맷으로 누적 기록되는가?

관련 파일: [11_monitor.sh](11_monitor.sh) · [14_verify_mission.sh](14_verify_mission.sh)

**답변**

성공한 실행마다 `>>`로 아래 한 줄을 추가한다.

```text
[2026-09-02 09:31:01] PID:1234 CPU:18.7% MEM:9.2% DISK_USED:27%
```

확인:

```bash
sudo tail -n 10 /var/log/agent-app/monitor.log
```

정규식 검증은 `14_verify_mission.sh`가 자동 수행한다.

### Q7. cron 매분 실행으로 monitor.log가 자동 증가하는가?

관련 파일: [07_agent-admin.cron](07_agent-admin.cron) · [11_monitor.sh](11_monitor.sh) · [15_collect_evidence.sh](15_collect_evidence.sh)

**답변**

agent-admin의 crontab에는 다음 규칙이 등록된다.

```cron
* * * * * /home/agent-admin/agent-app/bin/monitor.sh >> /var/log/agent-app/cron.log 2>&1
```

```bash
sudo crontab -u agent-admin -l
before=$(sudo wc -l < /var/log/agent-app/monitor.log)
sleep 70
after=$(sudo wc -l < /var/log/agent-app/monitor.log)
echo "$before -> $after"
```

앱이 실행 중이고 cron 서비스가 active라면 `after`가 증가한다.

### Q8. monitor.log 용량 관리(10MB/10개)가 설정되어 있고 동작을 설명할 수 있는가?

관련 파일: [11_monitor.sh](11_monitor.sh) · [08_agent-app-monitor.logrotate](08_agent-app-monitor.logrotate)

**답변**

두 겹으로 제공한다.

- `monitor.sh` 자체 회전: 활성 `monitor.log`가 10MiB 이상이면 `.1`로 옮기고 기존 `.1`~`.8`을 `.2`~`.9`로 이동한다. 활성 파일 + 9개 백업 = 총 10개다.
- `/etc/logrotate.d/agent-app-monitor`: `size 10M`, `rotate 9`, `compress`, `copytruncate`, `create 0660 agent-admin agent-core`.

스크립트 자체 회전은 과제 평가를 즉시 만족시키고, logrotate는 운영체제 표준 정책을 보여준다. 둘을 동시에 자주 강제 실행하지는 않는다.

## 항목 2 - 구현 방법을 설명할 수 있는가

### Q9. monitor.sh에서 프로세스 식별(pgrep/ps 등)과 포트 확인(ss/netstat 등)에 사용한 명령과 선택 이유는?

관련 파일: [11_monitor.sh](11_monitor.sh) · [05_agent.env.example](05_agent.env.example)

**답변**

프로세스는 다음 흐름이다.

```bash
PID="$(pgrep -x -- "$AGENT_PROCESS_NAME" | head -n 1 || true)"
```

`pgrep -x`는 프로세스 이름 전체가 `agent_app`과 같은 경우만 찾는다. 긴 셸 명령 문자열 속 경로까지 잡는 `pgrep -f` 오탐과 `ps | grep`의 자기 자신 오탐을 피하기 위해 선택했다.

포트는 다음 흐름이다.

```bash
ss -ltnH | awk '{print $4}' | grep -Eq '(^|:)15034$'
```

`ss`는 현대 Linux의 기본 소켓 도구이고, `-ltnH`는 LISTEN/TCP/숫자/헤더 없음만 남긴다. 프로세스가 살아 있어도 포트를 열지 못할 수 있으므로 프로세스와 포트는 별도로 검사해야 한다.

### Q10. CPU/MEM/DISK 값을 어떤 방식으로 추출·계산했고 로그 포맷을 왜 고정했는가?

관련 파일: [11_monitor.sh](11_monitor.sh) · [12_report.sh](12_report.sh)

**답변**

- CPU: `/proc/stat`을 1초 간격으로 두 번 읽어 `100 × (전체 증가량 - idle 증가량) / 전체 증가량` 계산
- MEM: `/proc/meminfo`의 `MemTotal`, `MemAvailable`로 `100 × (Total - Available) / Total` 계산
- DISK: `df -P /`의 루트 파티션 사용률 `%` 추출

로그 포맷을 고정하면 사람뿐 아니라 `awk`, 수집 에이전트, 대시보드가 같은 규칙으로 파싱할 수 있다. 자유 문장 로그는 “CPU가 어디 있는가?”부터 추측해야 하지만 `CPU:12.3%`는 키와 값이 일정하다.

### Q11. 소유자(agent-dev)와 실행자(agent-admin, cron) 권한 정책을 어떻게 만족시켰는가?

관련 파일: [04_setup.sh](04_setup.sh) · [11_monitor.sh](11_monitor.sh) · [07_agent-admin.cron](07_agent-admin.cron)

**답변**

```text
owner = agent-dev
group = agent-core
mode  = 750 = rwx r-x ---
```

- agent-dev는 소유자로 읽기/쓰기/실행 가능
- agent-admin은 agent-core 그룹원으로 읽기/실행 가능, 수정 불가
- agent-test와 기타 사용자는 접근 불가

```bash
stat -c '%U:%G %a %n' /home/agent-admin/agent-app/bin/monitor.sh
id agent-admin
```

개발자가 코드를 관리하고 운영 계정은 승인된 코드를 실행만 하는 역할 분리다.

### Q12. 용량 기반 로그 관리(10MB/10개)를 어떤 방식으로 구현했는가?

관련 파일: [11_monitor.sh](11_monitor.sh) · [08_agent-app-monitor.logrotate](08_agent-app-monitor.logrotate) · [13_archive_logs.sh](13_archive_logs.sh)

**답변**

이 구현은 Bash 회전과 logrotate 설정을 함께 제공한다. Bash에서는 `stat -c %s`로 바이트 크기를 확인하고 10MiB 이상일 때 높은 번호부터 역순으로 이동한다. 역순이어야 `.1`을 `.2`로 옮기기 전에 기존 `.2`를 잃지 않는다.

```text
monitor.log.8 -> monitor.log.9
...
monitor.log.1 -> monitor.log.2
monitor.log   -> monitor.log.1
새 monitor.log 생성
```

총 파일 수는 활성 1개와 백업 9개다.

## 항목 3 - 설계 이유를 설명할 수 있는가

### Q13. SSH 포트 변경과 Root 접속 차단이 왜 보안에 효과적인지 위험 모델 관점에서 설명할 수 있는가?

관련 파일: [06_sshd-agent-mission.conf](06_sshd-agent-mission.conf) · [04_setup.sh](04_setup.sh)

**답변**

인터넷에 노출된 SSH에는 자동화된 봇이 22번 포트와 `root` 계정을 반복 공격한다.

- 20022로 변경: 무차별 스캔의 소음을 줄이고 로그/자원 낭비를 낮춘다. 하지만 포트는 검색할 수 있으므로 강한 인증을 대신하지 않는다.
- Root 원격 차단: 공격자가 비밀번호 하나를 맞혀 즉시 최고 권한을 얻는 경로를 없앤다. 일반 계정 로그인 후 필요한 작업만 `sudo`로 수행하면 사용자별 감사 흔적도 남는다.

핵심 방어는 공개키 인증, 최소 방화벽 규칙, 보안 업데이트, 접속 제한이고 포트 변경은 보조 방어다.

### Q14. api_keys와 로그 디렉터리를 agent-core로 제한한 이유를 “최소 권한 원칙”으로 설명할 수 있는가?

관련 파일: [04_setup.sh](04_setup.sh) · [14_verify_mission.sh](14_verify_mission.sh)

**답변**

최소 권한은 각 역할에 업무에 필요한 권한만 주는 원칙이다.

- agent-test는 업로드 결과를 시험할 수 있지만 API 비밀을 볼 필요는 없다.
- agent-admin/dev는 앱 실행·개발·장애 분석을 위해 키와 운영 로그가 필요하다.
- 따라서 협업 데이터는 agent-common, 민감 데이터는 agent-core로 분리한다.

계정 하나가 침해돼도 접근 범위를 줄이는 “폭발 반경 축소” 효과가 있다.

### Q15. “경고는 출력하되 종료하지 않는 항목”(방화벽 비활성/임계치 초과)을 분리한 운영상의 이유는?

관련 파일: [11_monitor.sh](11_monitor.sh)

**답변**

프로세스와 포트는 서비스 제공 자체의 필수 조건이다. 둘이 실패하면 “정상” 로그를 남기면 안 되므로 exit 1이 맞다.

반면 CPU/MEM/DISK 임계치 초과는 서비스가 아직 동작하지만 위험이 커진 상태다. 이때 관제 스크립트까지 종료하면 이후 변화 데이터가 끊긴다. 방화벽 상태 조회도 일시적인 sudo/도구 문제일 수 있다. 따라서 경고를 남기고 자원 수집과 로그 기록을 계속해야 원인 분석 자료가 축적된다.

### Q16. 리다이렉션 기호 `>`와 `>>`의 차이와 로그 누적에 `>>`가 필요한 이유는?

관련 파일: [07_agent-admin.cron](07_agent-admin.cron) · [09_agent-app-archive.cron](09_agent-app-archive.cron)

**답변**

- `>`: 파일을 새로 만들거나 기존 내용을 지우고 덮어쓴다.
- `>>`: 파일 끝에 내용을 추가한다.

```bash
echo first  > demo.log   # demo.log = first
echo second > demo.log   # first가 사라짐
echo third >> demo.log   # second 다음에 third 추가
```

모니터링은 시간에 따른 변화가 핵심이다. 매분 `>`를 쓰면 마지막 한 줄만 남아 장애 직전의 추세를 볼 수 없으므로 `>>`를 사용한다.

## 항목 4 - 다른 상황에 적용할 수 있는가

### Q17. 모니터링 대상이 웹 서버(Nginx 등)로 바뀌면 monitor.sh에서 바꿔야 할 핵심 포인트는?

관련 파일: [05_agent.env.example](05_agent.env.example) · [11_monitor.sh](11_monitor.sh)

**답변**

네 가지를 바꾼다.

1. 프로세스: `AGENT_EXECUTABLE` 대신 `nginx: master process` 또는 systemd unit 검사
2. 포트: 15034 대신 HTTP 80/HTTPS 443
3. 로그: `/var/log/nginx/access.log`, `error.log`의 오류율·응답시간을 추가
4. 권한/계정: nginx 실행 계정(`www-data`)과 로그 읽기 그룹에 맞춤

프로세스와 포트만 보면 “응답은 하지만 500 오류만 내는” 상태를 놓친다. 실제 웹 서버에서는 `curl -fsS http://127.0.0.1/health` 같은 애플리케이션 레벨 검사를 추가하는 것이 좋다.

### Q18. “프로세스는 살아있는데 포트가 안 열리는 상황”의 원인 후보와 확인 순서는?

관련 파일: [10_run_agent.sh](10_run_agent.sh) · [11_monitor.sh](11_monitor.sh) · [15_collect_evidence.sh](15_collect_evidence.sh)

**답변**

다음 순서가 효율적이다.

1. `ps -fp <PID>`와 앱 로그: 초기화 중인지, 오류 후 멈췄는지 확인
2. `ss -ltnp`: 다른 포트/주소(`127.0.0.1`, IPv6)에 바인딩했는지 확인
3. 환경 변수/설정: `AGENT_PORT`, 오타, 잘못된 설정 파일 확인
4. 포트 충돌: `ss -ltnp | grep ':15034'`로 다른 프로세스 점유 확인
5. 권한/자원: 파일 권한, 메모리 부족, 파일 디스크립터 한도 확인
6. 방화벽: **리슨 자체가 확인된 뒤** 외부 접속 문제일 때 확인

방화벽은 프로세스가 포트를 LISTEN하지 못하게 만드는 일반적인 원인이 아니다. 먼저 앱 내부와 바인딩을 확인해야 한다.

### Q19. 로그가 급증해 디스크가 가득 찰 위험이 있을 때 운영자의 단기/중기/장기 대응은?

관련 파일: [11_monitor.sh](11_monitor.sh) · [08_agent-app-monitor.logrotate](08_agent-app-monitor.logrotate) · [13_archive_logs.sh](13_archive_logs.sh) · [09_agent-app-archive.cron](09_agent-app-archive.cron)

**답변**

**단기 - 서비스 생존**

- `df -h`, `du -xhd1 /var/log`로 범인 확인
- 앱/로그 발생 속도와 오류 폭주 원인 확인
- 이미 회전된 안전한 오래된 파일부터 압축·이동
- 활성 로그를 무작정 삭제하지 말고 프로세스의 파일 핸들 상태 확인

**중기 - 재발 억제**

- logrotate 크기/개수/압축 정책 조정
- 디스크 70/80/90% 단계 경보
- 오류 루프, 재시도 폭주, 과도한 debug 로그 수정
- 별도 로그 파티션 또는 중앙 로그 저장소 사용

**장기 - 용량 계획과 관측성 설계**

- 하루 평균/최대 로그량과 보존 기간으로 필요한 용량 계산
- 로그 수준·샘플링·보존 등급 정의
- 중앙 수집, 검색, 아카이브, 삭제 정책과 책임자 문서화

“로그를 전부 삭제”는 증거를 없애고 열린 파일 때문에 공간이 즉시 반환되지 않을 수도 있어 최후 수단이다.

---

# b1-1 학습 튜토리얼

## 1. 먼저 머릿속에 그릴 운영 흐름

현실의 작은 카페를 서버라고 생각해 보자.

- SSH는 직원 출입문
- 방화벽은 어떤 문을 열지 정하는 경비 규칙
- 사용자/그룹은 직원증과 부서
- 앱 프로세스는 일하는 바리스타
- 포트는 손님이 주문하는 창구
- 로그는 주문/사고 장부
- monitor.sh는 매분 순찰하는 매니저
- cron은 매니저의 알람
- logrotate는 오래된 장부를 묶어 창고로 보내는 규칙

바리스타가 건물 안에 있다고 해서 주문 창구가 열린 것은 아니다. 그래서 프로세스와 포트를 둘 다 확인한다.

## 2. 프로세스, 포트, 서비스의 차이

### 프로세스

실행 중인 프로그램 한 개다. PID라는 번호를 가진다.

```bash
pgrep -a -x agent_app
ps -fp <PID>
```

### 포트

네트워크 요청을 받는 논리적 창구다. 앱이 실행 중이어도 초기화 실패나 설정 오류로 포트를 열지 못할 수 있다.

```bash
ss -ltnp | grep ':15034'
```

### 서비스

프로세스를 계속 실행하고 재시작하는 운영 단위다. 이 과제는 직접 실행을 요구하지만 현업에서는 systemd unit으로 관리하는 경우가 많다.

## 3. 사용자, 그룹, chmod를 숫자로 이해하기

Linux 권한은 `소유자/그룹/기타` 세 칸이다.

| 숫자 | 기호 | 의미 |
|---|---|---|
| 4 | r | 읽기 |
| 2 | w | 쓰기 |
| 1 | x | 실행/디렉터리 진입 |

`750`은 다음 계산이다.

```text
7 = 4+2+1 = rwx (소유자)
5 = 4+1   = r-x (그룹)
0 = 0     = --- (기타)
```

따라서 agent-dev가 monitor.sh를 수정하고, 같은 agent-core의 agent-admin은 실행만 할 수 있다.

## 4. ACL이 왜 필요한가

기본 chmod는 파일마다 소유 그룹 하나만 표현한다. ACL은 “기본 그룹 외에 이 그룹에도 rwx”처럼 추가 규칙을 붙인다.

```bash
getfacl /home/agent-admin/agent-app/upload_files
```

기본 ACL(`default:`)은 새 파일이 생길 때도 정책을 상속시킨다. 공유 폴더에서 “어제 만든 파일은 되는데 오늘 만든 파일은 접근 불가” 같은 협업 문제를 줄인다.

## 5. SSH와 방화벽은 서로 다른 층이다

- sshd 설정: SSH 프로그램이 어느 포트에서 누구의 로그인을 받을지 결정
- UFW: 운영체제가 외부 패킷을 통과시킬지 결정

sshd가 20022에서 들어도 UFW가 막으면 외부에서 접속하지 못한다. 반대로 UFW가 20022를 열어도 sshd가 듣지 않으면 아무 서비스도 없다.

안전한 변경 순서:

1. VM 콘솔 유지
2. 새 포트 UFW 허용
3. sshd 설정 검사 `sshd -t`
4. sshd 재시작
5. `ss`로 리슨 확인
6. 새 터미널에서 실제 접속
7. 성공 후 이전 세션 종료

## 6. 환경 변수는 실행 계약이다

앱에 경로를 코드로 박아두면 서버마다 소스를 바꿔야 한다. 환경 변수는 같은 앱에 환경별 값을 주는 계약이다.

```bash
set -a
source /etc/agent-app/agent.env
set +a
env | grep '^AGENT_'
```

`run_agent.sh`는 이 계약을 읽고 제공 앱을 실행한다. cron은 로그인 셸보다 환경 변수가 적기 때문에 절대 경로와 환경 파일이 중요하다.

## 7. 제공 앱의 키 경로를 실험으로 이해하기

제공 앱을 잘못 설정하면 단계별 메시지가 원인을 알려준다.

- root 실행 → `Running as 'root' is forbidden`
- 환경 변수 누락 → `Missing Env`
- `AGENT_KEY_PATH`에 파일 경로 지정 → `Key Path Mismatch`
- `secret.key` 없음 → `Missing File: secret.key`
- 잘못된 내용 → `Invalid Content in secret.key`
- 로그 쓰기 불가 → `Permission Denied`

즉 `AGENT_KEY_PATH`는 “키 파일이 들어 있는 디렉터리”이고, 앱이 그 아래 `secret.key`를 조합한다.

## 8. CPU 사용률 계산을 숫자로 보기

`/proc/stat`의 CPU 시간 누적값을 1초 간격으로 읽었다고 하자.

```text
첫 번째 전체=10,000 idle=7,000
두 번째 전체=10,100 idle=7,060
```

1초 동안 전체는 100 증가했고 idle은 60 증가했다. 일한 시간은 40이므로 CPU 사용률은 `40/100 × 100 = 40%`다. 누적값 자체가 아니라 **두 시점의 차이**를 사용한다.

## 9. 메모리는 free보다 available을 보는 이유

Linux는 남는 메모리를 파일 캐시로 적극 사용한다. `free`만 보면 캐시도 사용 중으로 보여 과장될 수 있다. `MemAvailable`은 캐시 회수 가능성까지 고려해 새 프로그램이 사용할 수 있는 양을 추정한다.

```text
사용률 = (MemTotal - MemAvailable) / MemTotal × 100
```

## 10. cron에서 자주 실패하는 이유

cron은 터미널과 다르다.

- PATH가 짧다.
- 현재 디렉터리가 예상과 다르다.
- 셸 초기화 파일을 읽지 않는다.
- 화면이 없으므로 출력이 사라지기 쉽다.

그래서 crontab은 절대 경로를 사용하고 stdout/stderr를 `cron.log`에 남긴다.

```bash
sudo tail -f /var/log/agent-app/cron.log
```

## 11. 회전과 보존은 다른 문제다

- 회전(rotation): 활성 로그가 너무 커지지 않게 10MB 단위로 나눔
- 보존(retention): 며칠까지 보관하고 언제 압축/삭제할지 결정

택배 상자로 비유하면 회전은 한 상자가 무거워지면 새 상자를 여는 일이고, 보존은 7일 지난 상자를 창고로 보내고 30일 지난 상자를 폐기하는 일이다.

## 12. 장애 분석 실전 순서

### 상황 A - monitor가 “프로세스 없음”

1. 앱 터미널이 종료됐는지 확인
2. `pgrep -a -x agent_app`
3. 환경 파일의 `AGENT_EXECUTABLE` 확인
4. 제공 바이너리 실행 권한/아키텍처 확인

### 상황 B - 프로세스 OK, 포트 FAIL

1. 앱 출력에서 Boot 실패/초기화 상태 확인
2. `ss -ltnp`로 실제 포트 확인
3. AGENT_PORT 오타/충돌 확인
4. 자원 부족 확인

### 상황 C - 수동 실행은 되지만 cron 실패

1. `systemctl status cron`
2. agent-admin crontab 확인
3. `cron.log` 확인
4. 디렉터리/파일 권한 확인
5. 앱이 계속 실행 중인지 확인

## 13. 직접 해볼 미니 실험

실습 VM에서만 수행한다.

1. 앱을 끄고 monitor를 실행해 exit code 1 확인
2. `AGENT_PORT=15035`로 임시 변경해 제공 앱과 monitor의 불일치 관찰
3. secret.key 내용을 바꿔 Boot 3단계 실패 확인 후 복구
4. agent-test로 api_keys 진입이 거부되는지 확인
5. monitor를 세 번 실행해 로그가 세 줄 늘어나는지 확인
6. 샘플 로그를 복사해 `12_report.sh --log` 통계 확인

실패를 일부러 만들고 “어떤 신호가 어디에 나타나는가”를 보는 것이 명령어 암기보다 오래 남는다.
