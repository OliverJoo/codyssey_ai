# [Bug] 두 워커가 반대 순서로 락을 잡아 프로세스가 무응답 상태가 됨

## 1. Description (현상 설명)

- 대상: `agent-leak-app`
- 실행 환경: macOS Apple Silicon, Docker Desktop의 Ubuntu 22.04 ARM64 컨테이너, 일반 사용자 `learner`
- 재현 조건: `MEMORY_LIMIT=512`, `CPU_MAX_OCCUPY=10`, `MULTI_THREAD_ENABLE=true`
- 관측 현상: PID는 존재하지만 두 워커의 마지막 로그가 `WAITING ... BLOCKED`에서 멈추고, 이후 작업 완료 로그가 나오지 않았다.

이 스크립트는 무한 대기를 방지하기 위해 20초 후 실험 프로세스를 종료한다. 따라서 `TIMED_OUT=true`는 재현 실패가 아니라 무응답 상태를 안전하게 관찰하고 실험을 끝냈다는 뜻이다.

## 2. Evidence & Logs (증거 자료)

재현 명령:

```bash
./06_run_mission.sh deadlock-before
./06_run_mission.sh deadlock-after
```

증거 파일:

- `13_evidence_deadlock-before.log`
- `14_evidence_deadlock-after.log`

실제 사전 검증의 핵심 로그:

```text
[Worker-Thread-1] LOCK ACQUIRED: [Shared_Memory_A]. (Holding...)
[Worker-Thread-2] LOCK ACQUIRED: [Socket_Pool_B]. (Holding...)
[Worker-Thread-1] Need resource [Socket_Pool_B] to finish job.
[Worker-Thread-2] Need resource [Shared_Memory_A] to write logs.
[Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
[Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)
```

`04_monitor.sh`에서는 같은 PID가 계속 존재하고 상태·스레드 수는 나오지만 CPU와 RSS가 더 이상 의미 있게 변하지 않는 구간을 찾는다. Linux에서 직접 수행한다면 다음 명령도 같은 PID로 확인한다.

```bash
ps -ef | grep '[a]gent-leak-app'
ps -L -p "$PID" -o pid,tid,psr,stat,pcpu,comm
top -H -p "$PID"
```

## 3. Root Cause Analysis (원인 분석)

의존 관계는 다음과 같다.

```text
Thread-1: Shared_Memory_A 보유 -> Socket_Pool_B 대기
Thread-2: Socket_Pool_B 보유   -> Shared_Memory_A 대기
```

두 자원은 한 스레드만 사용할 수 있고(상호 배제), 각 스레드는 하나를 가진 채 다른 하나를 기다리며(점유 대기), 상대의 락을 강제로 빼앗을 수 없고(비선점), 대기 방향이 원을 이룬다(순환 대기). 교착상태의 네 조건이 모두 충족되어 어느 스레드도 진행할 수 없다.

## 4. Workaround & Verification (조치 및 검증)

| 구분 | MULTI_THREAD_ENABLE | 관측 결과 |
|---|---|---|
| Before | true | 두 락을 반대로 보유한 뒤 BLOCKED, PID 생존, 제한 시간 초과 |
| After | false | Thread-A/B/C가 모두 100% 완료하고 정상 관제 루프로 진입 |

단일 스레드 전환은 임시 회피이며 처리량이 감소할 수 있다. 근본 해결은 모든 코드 경로가 락을 동일한 순서로 획득하게 만들고, 가능하면 한 임계구역으로 합치거나 타임아웃이 있는 `tryLock`을 사용하며, 락 보유 중 외부 I/O를 피하는 것이다.

완료 조건:

- Before 파일에 두 `LOCK ACQUIRED`, 두 `Need resource`, 두 `WAITING ... BLOCKED`가 있어야 한다.
- Before 관제에는 같은 PID가 제한 시간까지 남아 있어야 한다.
- After 파일에는 각 태스크의 `Task Completed. (100%)`와 `All tasks completed.`가 있어야 한다.
