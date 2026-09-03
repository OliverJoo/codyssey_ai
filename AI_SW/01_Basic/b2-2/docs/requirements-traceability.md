# PDF·평가 질문 요구사항 추적표

기준 자료는 10쪽 과제 PDF `미션 - AI_SW 기초 (AI_SW Basic).pdf`와 [질문 이미지 1](../assets/b2-2-question-1.png), [질문 이미지 2](../assets/b2-2-question-2.png)다. 2026-09-03 원격 `main` `daecf53`, Git graph, GitHub PR·review API, 실제 부모 commit replay를 교차 확인했다.

판정 기준은 `충족`, `부분`, `미충족`, `미확인`, `추가 설명`으로 나눈다. 문서에 절차가 적혀 있다는 사실과 Git 이력으로 실제 실행이 증명되는 것은 같은 수준으로 취급하지 않는다.

## PDF 필수 요구사항

| 요구사항 | 판정 | 근거와 한계 |
|---|---|---|
| 3~5명, 단일 저장소, 협업 권한 | 충족 | 4 collaborators: admin 1, write 3 |
| `main` Branch Protection, PR only, 승인 1명 이상 | 부분 | `protected: true`와 PR merge 이력은 확인. required approvals·직접 push 차단 세부 설정 화면은 미확인 |
| GitHub Flow·브랜치 규칙·선택 이유 | 충족 | 원격 `docs/CONTRIBUTING.md`, branch·merge 이력 |
| 모든 작업 Issue 생성 및 PR의 `Closes/Fixes` 연동 | 미충족 | 19개 병합 PR 중 12개만 closing keyword, 7개 누락 |
| 커밋 메시지 규칙 | 충족 | 협업 문서와 실제 commit subject |
| 팀원별 병합 PR 2개 이상 | 충족 | 네 명 모두 2개 이상 |
| 팀원별 타인 PR review 2개 이상 | 충족 | dave17code 4, heeyoung35 2, OliverJoo 7, hyunn9799 6 |
| 팀원별 본인 PR 피드백 반영 1회 | 충족 | 기능 PR #2·#4·#7·#8의 후속 commit |
| 모든 PR의 실질 코멘트와 상호작용 | 미충족 | 구체적 텍스트 피드백이 확인되는 PR은 5/19. 나머지 다수는 빈 approve 또는 단순 승인 문구 |
| 충돌 해결 2회 이상, 비자명 충돌 1회 | 미확인 | `main.py` 충돌 `abe92b8` 한 건은 확인. rename/modify 사례 부모 replay는 자동 병합되어 두 번째 실제 conflict로 입증되지 않음 |
| amend·reset·revert·stash 4종 및 팀원별 참여 | 부분 | revert는 commit+PR, amend·stash는 PR 본문·문서, reset은 문서 기록만 확인 |
| 필수 협업 문서 3종 | 충족 | `CONTRIBUTING`, `conflict-resolution`, `troubleshooting-log` 존재. 현재 패키지 문서는 원격 기반 확장본 |
| 팀원별 유틸 함수와 사용 예 | 충족 | 원격 `src/` 네 모듈과 commit. `src/main.py`는 2개 함수 실행, 네 함수 통합은 별도 추가 예제 |
| Git graph 증빙 | 충족 | 원격 그대로 보존한 [git-log.txt](git-log.txt)와 최신 first-parent 검증 스크립트 |

## 질문 22개 연결

| 질문 | 성격 | 현재 판정·답변 위치 |
|---:|---|---|
| Q1 | 수행 증거 | 단일 repo·4인 권한 충족 |
| Q2 | 수행 증거 | Branch Protection 세부값 미확인으로 부분 |
| Q3 | 수행 증거 | closing link 12/19로 미충족 |
| Q4 | 수행 증거 | 인당 PR 2개 이상 충족 |
| Q5 | 수행 증거 | 인당 review 수와 기능 피드백 반영 충족 |
| Q6 | 수행 증거 | 실제 conflict 1건만 확인, 두 번째·비자명 조건 미확인 |
| Q7 | 수행 증거 | 4종 기록은 있으나 독립 검증 강도가 달라 부분 |
| Q8 | 산출물 | 필수 문서 3종 존재 |
| Q9~Q12 | 이력 기반 분석 | 실제 저장소 사례를 토대로 설명 |
| Q13 | 추가 학습 | 재현 가능한 로그의 권장 필드. 원격 모든 기록이 이 형식을 지켰다는 주장이 아님 |
| Q14~Q18 | 개념 + 실제 예 | Git/GitHub 일반 원리와 확인된 이력 연결 |
| Q19~Q21 | 가상 시나리오 | hotfix·메시지 개선·반복 충돌 예방 방안 |
| Q22 | 보너스 개념 | 실제 interactive rebase 수행 증빙 없음. 개념과 안전 규칙만 설명 |

각 질문의 완성 답변은 [README_answer.md](../README_answer.md)에 있다.

## 제출 전에 실제로 보완해야 하는 항목

1. Branch Protection 설정 화면에서 required approval 수와 직접 push 차단을 캡처한다.
2. closing keyword가 빠진 7개 PR은 이미 merge되어 자동 연결을 소급할 수 없으므로 미충족 사실을 설명한다.
3. 모든 PR의 실질 review 요구는 현재 5/19만 확인되므로 완료로 표시하지 않는다.
4. 두 번째 실제 conflict와 비자명 conflict는 새 Issue·branch·PR에서 실제 unmerged 상태와 해결 과정을 남겨야 한다.
5. reset은 실행 직후 `git status`와 reflog 같은 당시 증거를 추가한다.
6. rebase 보너스는 수행 전·후 graph가 없으므로 “미수행/증빙 없음”으로 표시한다.
