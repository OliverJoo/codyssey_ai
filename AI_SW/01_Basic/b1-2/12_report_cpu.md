# [Bug] 단일 프로세스 CPU 과점유로 보호 임계치가 위반됨

## 1. Description (현상 설명)

- 대상: `agent-leak-app`
- 실행 환경: macOS Apple Silicon, Docker Desktop의 Ubuntu 22.04 ARM64 컨테이너, 일반 사용자 `learner`
- 재현 조건: `MEMORY_LIMIT=512`, `CPU_MAX_OCCUPY=100`, `MULTI_THREAD_ENABLE=false`
- 관측 현상: 앱이 계산하는 CPU 부하 지표가 5%에서 50.15%까지 증가한 뒤 임계 위반 로그와 함께 종료되었다.

증거 파일의 PID와 같은 프로세스 행을 `ps`로 함께 추적했다. 이 실행에서 OS가 관측한 `%CPU`는 시작 직후 3.0%를 제외하면 주로 0.5~1.0%였다. 따라서 앱 내부 지표 상승을 실제 코어 점유율 상승과 동일하다고 단정하지 않는다.

## 2. Evidence & Logs (증거 자료)

재현 명령:

```bash
./06_run_mission.sh cpu-before
./06_run_mission.sh cpu-after
```

증거 파일:

- `10_evidence_cpu-before.log`
- `11_evidence_cpu-after.log`

실제 사전 검증의 핵심 로그:

```text
2026-09-02 01:27:09,457 [INFO] [CpuWorker] Current Load: 5.00%
2026-09-02 01:27:34,454 [INFO] [CpuWorker] Current Load: 39.92%
2026-09-02 01:27:46,953 [INFO] [CpuWorker] Current Load: 50.15%
2026-09-02 01:27:47,059 [CRITICAL] [CpuWorker] CPU Threshold Violated! (50.15%).
```

`04_monitor.sh` CSV의 `CPU_PERCENT`는 Linux `ps -p PID -o %cpu=`로 얻는다. 프로그램 내부의 `Current Load`는 시나리오가 계산한 부하 지표이고, `ps` 값은 운영체제가 관측한 실제 프로세스 사용률이다. 두 값을 구분해 함께 제시해야 한다.

## 3. Root Cause Analysis (원인 분석)

높은 설정값이 점진적으로 증가하는 CPU 부하 시나리오를 선택하고, 앱의 Watchdog가 내부 지표 약 50%를 보호 기준으로 사용해 프로세스를 종료한다. 다만 이번 바이너리의 `Current Load`는 `ps %CPU`와 일치하지 않으므로 실제 CPU 과점유를 재현했다기보다 보호 로직의 시뮬레이션을 재현한 것으로 해석해야 한다. 실제 서비스라면 프로파일러와 OS 지표로 과점유 여부를 별도 확인한다.

`CPU_MAX_OCCUPY=100`은 프로그램이 높은 부하 시나리오를 수행하도록 만든 재현값이고, `10`은 부하가 정점에 닿을 때 냉각(cooldown)하도록 하는 비교값이다.

## 4. Workaround & Verification (조치 및 검증)

| 구분 | CPU_MAX_OCCUPY | 관측 결과 |
|---|---:|---|
| Before | 100% | 내부 부하가 50.15%에 도달한 뒤 임계 위반 및 종료 |
| After | 10% | 5~10% 범위에서 증가와 cooldown을 반복하며 제한 시간 동안 생존 |

환경변수 하향은 실험 프로그램의 부하를 제한하는 임시 조치다. 근본 해결은 바쁜 대기 제거, 작업 큐의 속도 제한, 배치 크기 축소, 계산 루프의 중단 지점 추가, 프로파일러를 이용한 핫스팟 개선이다.

완료 조건:

- Before 증거에 CPU 증가 구간과 `CPU Threshold Violated`가 있어야 한다.
- After 증거에는 `Peak reached`, `Starting cooldown`, `Cooldown complete`가 있어야 한다.
- 두 파일의 PID와 같은 `04_monitor.sh` 행을 비교해야 한다.
