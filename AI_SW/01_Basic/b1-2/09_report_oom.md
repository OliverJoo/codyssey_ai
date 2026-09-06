# [Bug] 메모리 증가 후 MemoryGuard가 프로세스를 강제 종료함

## 1. Description (현상 설명)

- 대상: `agent-leak-app`
- 실행 환경: macOS Apple Silicon, Docker Desktop의 Ubuntu 22.04 ARM64 컨테이너, 일반 사용자 `learner`
- 재현 조건: `MEMORY_LIMIT=50`, `CPU_MAX_OCCUPY=10`, `MULTI_THREAD_ENABLE=false`
- 관측 현상: 힙 사용량이 약 3초마다 25MB씩 증가하고 약 5초 뒤 50MB 제한에 도달하면서 프로세스가 종료되었다.

검증 실행 시각은 각 증거 파일의 `STARTED_AT`과 관제 CSV의 ISO 8601 타임스탬프로 확인한다. PID는 실행할 때마다 달라지므로 증거 파일의 `PID` 값을 기준으로 판단한다.

## 2. Evidence & Logs (증거 자료)

재현 명령:

```bash
./06_run_mission.sh oom-before
./06_run_mission.sh oom-after
```

증거 파일:

- `07_evidence_oom-before.log`
- `08_evidence_oom-after.log`

실제 사전 검증의 핵심 로그:

```text
2026-09-02 01:23:09,453 [INFO] [MemoryWorker] Current Heap: 25MB
2026-09-02 01:23:12,475 [INFO] [MemoryWorker] Current Heap: 50MB
2026-09-02 01:23:12,475 [CRITICAL] [MemoryGuard] Memory limit exceeded (50MB >= 50MB)
2026-09-02 01:23:12,477 [CRITICAL] [MemoryGuard] Self-terminating process 31 to prevent system instability.
```

`04_monitor.sh`는 `TIMESTAMP,PID,CPU_PERCENT,RSS_KB,MEM_MB,STATE,THREADS,ELAPSED` 순서로 데이터를 남긴다. 시간에 따라 `RSS_KB`와 `MEM_MB`가 계속 증가하고 마지막에 `EXITED`가 기록되는지 확인한다.

## 3. Root Cause Analysis (원인 분석)

`MemoryWorker`가 사용한 힙 데이터를 해제하지 않아 프로세스의 물리 메모리 사용량(RSS)이 계속 증가한다. 제한이 없으면 호스트의 가용 메모리와 스왑을 소진해 시스템 전체가 느려질 수 있다. 이 프로그램은 운영체제 OOM Killer가 개입하기 전에 내부 `MemoryGuard`가 `MEMORY_LIMIT` 도달을 감지하고 자기 프로세스를 종료한다.

따라서 "운영체제의 OOM Killer가 바로 종료했다"고 단정하면 안 된다. 이번 증거의 직접 원인은 애플리케이션 보호 정책이며, 그 정책이 막으려는 근본 결함은 해제되지 않는 힙 데이터다.

## 4. Workaround & Verification (조치 및 검증)

| 구분 | MEMORY_LIMIT | 관측 결과 |
|---|---:|---|
| Before | 50MB | 약 5초 뒤 50MB에 도달해 MemoryGuard 종료 |
| After | 100MB | 동일 증가율에서 종료 시점이 뒤로 이동하여 생존 시간이 늘어남 |

환경변수 상향은 장애 시점을 늦추는 임시 조치다. 근본 해결은 소스에서 불필요한 객체 참조를 제거하고, 캐시 상한·만료 정책을 두며, 장시간 부하 테스트에서 RSS가 안정화되는지 검증하는 것이다.

완료 조건:

- 두 증거 파일에 서로 다른 `MEMORY_LIMIT`이 기록되어야 한다.
- Before보다 After의 `ELAPSED`가 길어야 한다.
- 두 실행 모두 메모리 수치가 시간에 따라 증가해야 한다.
