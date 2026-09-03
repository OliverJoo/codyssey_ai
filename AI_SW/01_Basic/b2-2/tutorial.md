# b2-2 학습·질답 자료 보는 순서

이 문서는 자료가 많은 `b2-2` 폴더에서 무엇을 먼저 보고, 어떤 파일을 함께 확인해야 하는지 안내한다. `src/`는 원격 저장소 `main`의 코드 스냅샷이고, 답변·다이어그램·검증 파일은 그 코드와 실제 GitHub 이력을 설명하기 위한 학습 자료다.

## 1. 가장 먼저: 자료의 출처와 범위 확인

1. [코드 출처와 제출 패키지 경계](docs/source-provenance.md)
2. [최신 원격 변경 감사](docs/remote-change-audit.md)

두 파일을 먼저 보면 원격과 동일한 파일, 평가용으로 확장한 파일, 최신 기준 commit `daecf53`을 구분할 수 있다. 학습용 예제나 재현 결과를 실제 원격 작업으로 오해하는 일을 막아 준다.

## 2. 전체 미션 이해

1. [README](README.md)
2. [GitHub Flow 다이어그램](diagrams/01_github-flow.html)
3. [요구사항 추적표](docs/requirements-traceability.md)

README에서 미션 목표와 네 GitHub 계정의 역할을 읽고, 다이어그램에서 Issue → 브랜치 → PR → 리뷰 → 병합 흐름을 확인한다. 요구사항 추적표를 함께 보면 각 평가 항목이 어느 증거와 연결되는지 빠르게 찾을 수 있다.

## 3. 실제 기여와 GitHub 증거 확인

1. [제출 인덱스](SUBMISSION.md)
2. [Git·GitHub 이력 증빙](docs/git-history-evidence.md)
3. [원격 Git 로그 스냅샷](docs/git-log.txt)

SUBMISSION은 계정별 PR·리뷰·피드백 반영 링크를 모은 목차다. 의심되는 항목은 Git 이력 증빙과 원격 로그에서 commit, merge 구조, 승인 여부를 교차 확인한다.

## 4. 충돌 해결 학습

1. [충돌 해결 다이어그램](diagrams/02_conflict-resolution.html)
2. [실제 충돌 해결 기록](docs/conflict-resolution.md)
3. [충돌 재현 스크립트](02_demo.sh)

다이어그램으로 두 충돌의 분기와 해결 원칙을 먼저 파악한 뒤 문서에서 실제 PR·commit을 확인한다. `02_demo.sh`는 원천 저장소를 건드리지 않고 임시 저장소에서 같은 영역 충돌과 rename/modify 계열 충돌을 재현한다.

## 5. Git 복구 명령 학습

1. [복구 명령 의사결정 다이어그램](diagrams/03_git-recovery-decision.html)
2. [트러블슈팅 기록](docs/troubleshooting-log.md)

변경이 원격에 공유됐는지를 먼저 판단하고 `amend`, `reset --soft`, `revert`, `stash` 중 알맞은 명령을 선택한다. 다이어그램은 선택 기준을, 트러블슈팅 기록은 실제 담당 계정·명령·증거 수준을 설명한다.

## 6. 코드를 직접 확인하고 실행

1. [원격과 동일한 소스 코드](src)
2. [네 함수 통합 실행 예제](examples/team_utils_demo.py)
3. [함수 단위 테스트](tests/test_team_utils.py)

`src/`에서 원격 코드를 그대로 확인하고, 추가 예제로 네 함수의 결과를 한 번에 실행한다. 테스트를 함께 보면 정상 입력과 경계값에서 기대하는 동작을 구체적으로 이해할 수 있다.

```bash
python3 examples/team_utils_demo.py
bash 03_test.sh
```

## 7. 질문 이미지와 답변 학습

1. [질문 이미지 1](assets/b2-2-question-1.png)
2. [질문 이미지 2](assets/b2-2-question-2.png)
3. [질문별 상세 답변](README_answer.md)
4. [스크롤형 발표 페이지](README_answer.html)

질문 원문을 먼저 읽고 Markdown 답변에서 근거 링크를 따라간다. 발표나 구두 설명을 연습할 때는 HTML 페이지를 스크롤하면서 정상 흐름 → 충돌 → 복구 → 상황 판단 순으로 설명한다.

## 8. 제출 직전 검증

1. `bash 01_setup.sh` — Python과 Git 환경 확인
2. `bash 03_test.sh` — 원격 코드 동작 테스트
3. `bash 04_verify.sh` — 문서 링크·질문 수·핵심 증거 검사
4. `bash 05_verify_upstream.sh` — 원격 `main`과 보존 스냅샷 직접 비교

원격 저장소가 변경되면 `05_verify_upstream.sh`가 기준 commit 불일치를 알린다. 이때는 문서의 숫자나 hash만 임의로 고치지 말고 원격 이력을 다시 감사해야 한다.

## 목적별 빠른 경로

- **처음 학습:** 출처 확인 → README → GitHub Flow → 충돌 → 복구 → 코드 실행
- **질답 준비:** 질문 이미지 → README_answer.md → 연결된 증빙 → README_answer.html
- **평가자 시연:** GitHub Flow → SUBMISSION → 충돌·복구 다이어그램 → 코드 실행 → `04_verify.sh`
- **원격 정합성 확인:** source-provenance → remote-change-audit → `05_verify_upstream.sh`

다이어그램 HTML은 상단 버튼으로 50%·100%·150%·200% 확대와 화면 맞춤을 사용할 수 있다.
