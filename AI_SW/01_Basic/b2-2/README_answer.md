# b2-2 평가 질문과 근거 기반 답변

이 문서는 질문 이미지 두 장의 22개 항목에 답한다. 답변은 실제 공개 저장소의 코드, commit graph, GitHub Issue·PR·review API를 교차 확인해 작성했으며, 참여자는 실제 GitHub 계정 `dave17code`, `heeyoung35`, `OliverJoo`, `hyunn9799`로 표기한다. 원격 이력으로 확인한 사실, 문서 기록만 있는 주장, 추가 학습용 설명과 가상 시나리오를 구분한다.

> **명령 실행 위치:** 아래 Git 명령에서 `UPSTREAM_CLONE`은 `https://github.com/dave17code/b2-2-git-conflict-craft`를 clone한 로컬 경로다. Git 이력 확인이나 연습 전에 `cd "$UPSTREAM_CLONE"`으로 이동한다. `src/`는 원격 `main`과 같은 원본이고, 네 함수를 한 번에 실행하는 추가 예시는 `examples/team_utils_demo.py`에 분리되어 있다.

## 답변 자료 순서

1. [질문 이미지 1](assets/b2-2-question-1.png)
2. [질문 이미지 2](assets/b2-2-question-2.png)
3. [GitHub Flow](diagrams/01_github-flow.html)
4. [충돌 해결](diagrams/02_conflict-resolution.html)
5. [Git 복구 선택](diagrams/03_git-recovery-decision.html)
6. [제출 인덱스](SUBMISSION.md)
7. [Git 이력 증빙](docs/git-history-evidence.md)
8. [최신 원격 변경 전수 감사](docs/remote-change-audit.md)

---

## 항목 1 - 필수 결과물과 수행 증거

### Q1. 저장소가 팀 단위로 1개이며, 팀원이 협업 가능한 권한으로 참여했는가?

**답변:** 충족한다. 실제 공개 저장소는 [dave17code/b2-2-git-conflict-craft](https://github.com/dave17code/b2-2-git-conflict-craft) 하나이며, Collaborators API에서 총 4명(admin 1명, push 권한 3명)이 확인됐다. 참여자는 GitHub 계정 dave17code·heeyoung35·OliverJoo·hyunn9799로 표기한다. 로컬 commit 작성자와 GitHub PR 작성자도 네 명의 기여를 보여 준다.

**관련 자료:** [팀원별 실제 기여](SUBMISSION.md#2-팀원별-실제-기여), [Git 이력 증빙](docs/git-history-evidence.md)

### Q2. `main`에 Branch Protection이 설정되어 있고, 직접 push 없이 PR로만 병합되었는가?

**답변:** GitHub branch API에서 `main`의 `protected: true`가 확인됐다. 초기 commit `175ea3c` 이후 `main`의 first-parent 통합 이력은 모두 2-parent PR merge이며, 확인한 병합 PR 19개 모두 최소 1개 승인이 있다. 따라서 보호·PR 병합·승인 사용은 확인된다. 다만 현재 계정으로 세부 protection endpoint를 조회하지 못해 “필수 승인 정확히 1명”, “직접 push 차단” 같은 세부 규칙 값은 설정 화면 캡처가 추가로 필요하다.

**관련 자료:** [요구사항 충족 현황](SUBMISSION.md#3-요구사항-충족-현황), [협업 규칙](docs/CONTRIBUTING.md#8-안전-규칙)

### Q3. 각 PR이 Issue와 연동되어 추적 가능한가?

**답변:** 주요 PR 다수는 연결됐지만 **모든 PR이 closing keyword로 연결되지는 않았다.** 기존 연결 외에 PR #29→Issue #28, PR #30→Issue #27이 추가됐다. 반면 #15, #17, #18, #19, #20, #31, #32는 closing link가 없다. 추적성은 부분 충족이며, 이후에는 모든 PR에 `Closes #n`을 강제해야 한다.

**관련 자료:** [실제 PR 목록](SUBMISSION.md#2-팀원별-실제-기여), [PR 규칙](docs/CONTRIBUTING.md#5-issue와-pr)

### Q4. 팀원별 PR 2개 이상이 병합되었는가?

**답변:** 충족한다. dave17code는 #2·#11·#15·#30·#31·#32, heeyoung35는 #4·#14, OliverJoo는 #7·#16·#17·#19·#22·#29, hyunn9799는 #8·#18·#20·#24·#26이 병합됐다. 원격 merge commit 제목과 GitHub `merged_at`을 교차 확인했다.

**관련 자료:** [팀원별 PR 링크](SUBMISSION.md#2-팀원별-실제-기여), [Git 이력 증빙](docs/git-history-evidence.md)

### Q5. 팀원별 리뷰 2개 이상과 본인 PR의 피드백 반영 1회가 있는가?

**답변:** 충족한다. 타인 PR 승인 수는 dave17code 4건(#4·#14·#26·#29), heeyoung35 2건(#2·#11), OliverJoo 7건(#8·#18·#20·#24·#30·#31·#32), hyunn9799 6건(#7·#15·#16·#17·#19·#22)이다. 또한 핵심 기능 PR #2/#4/#7/#8의 피드백이 각각 `5e171a9`(타입 검사), `e47ac39`(앞뒤 공백), `db5ae1a`(순서 비보장 명시), `38ab44f`(0·음수 설명)에 반영됐다.

**관련 자료:** [review와 반영 commit 링크](SUBMISSION.md#2-팀원별-실제-기여), [리뷰 규칙](docs/CONTRIBUTING.md#6-코드-리뷰)

### Q6. 충돌 기록이 2회 이상이고 비자명 충돌이 포함되는가?

**답변:** **비자명 충돌 충족 여부는 미확인이다.** `src/main.py` 동일 영역 충돌은 merge commit `abe92b8`의 combined diff와 두 출력을 결합한 결과로 확인된다. 두 번째 기록은 OliverJoo의 `old-guide.md → new-file.md` rename과 hyunn9799의 기존 파일 내용 수정을 `9315e23`과 `fee0b98`로 통합했다고 설명한다. 그러나 같은 부모와 변경을 사용한 독립 replay에서는 Git이 자동 병합했으므로, 이 이력만으로 과제에서 요구한 실제 rename/modify 충돌 발생을 입증할 수 없다. 따라서 “충돌 기록 2회 중 비자명 충돌 1회”는 추가 터미널 로그나 재현 가능한 충돌 절차가 필요하다.

**관련 자료:** [이력 기반 충돌 기록](docs/conflict-resolution.md), [충돌 시각화](diagrams/02_conflict-resolution.html), [증빙 강도](docs/remote-change-audit.md)

### Q7. amend/reset/revert/stash 4종과 팀원별 참여 기록이 있는가?

**답변:** 네 명의 담당 기록은 있다. PR #11 본문은 dave17code amend, PR #26 본문은 hyunn9799 stash/pop을 명시한다. OliverJoo revert는 원본 `df3e50c`, 취소 `7a37beb`, 병합 PR #29로 실제 이력까지 확인됐다. heeyoung35 reset soft만 원천 문서 기록 수준이며, 최종 graph에서 사라지는 명령이므로 당시 `git status`나 reflog가 있어야 더 강한 증빙이 된다. 따라서 4종 기록은 충족하지만 실행 증빙 강도는 일부 보완 필요다.

**관련 자료:** [증빙 수준과 절차](docs/troubleshooting-log.md), [복구 시각화](diagrams/03_git-recovery-decision.html)

### Q8. 필수 문서 세 개가 존재하고 구조를 갖추었는가?

**답변:** 문서 구조는 충족한다. [CONTRIBUTING](docs/CONTRIBUTING.md)은 브랜치·커밋·PR·리뷰·충돌 규칙을, [conflict-resolution](docs/conflict-resolution.md)은 두 충돌 주장에 대한 참여자·상황·판단·결과를, [troubleshooting-log](docs/troubleshooting-log.md)은 네 복구 명령의 상황·절차·결과·주의점을 제공한다. 문서가 존재한다는 사실과 각 기록의 실행 증빙 강도는 별도로 평가한다.

---

## 항목 2 - 코드와 문서 설계 설명

### Q9. 브랜치를 “작업 단위”로 나누는 기준은 무엇인가?

**답변:** 한 브랜치는 한 Issue와 한 가지 검토 가능한 목적을 가진다. 실제 핵심 기능도 `reverse_string`, `count_words`, `remove_duplicates`, `is_even`을 서로 다른 브랜치와 PR로 나눴다. 한 문장으로 목적을 설명할 수 있고 독립 검증·독립 revert가 가능하면 적당한 크기다. `main.py` 같은 공용 파일은 별도 통합 작업으로 분리한다.

**관련 자료:** [원격 원본 코드 표](README.md#12-원격-원본-코드와-추가-예제), [브랜치 규칙](docs/CONTRIBUTING.md#3-브랜치-이름)

### Q10. What/Why/How와 Issue 연동을 일관되게 남긴 방법은 무엇인가?

**답변:** PR 본문을 연결 Issue, What, Why, How 네 칸으로 고정했다. 실제 PR #2·#4·#7·#8 등은 기능, 이유, 로컬 검증을 구분한다. 다만 일부 충돌 PR은 `Closes #n` 대신 “관련 작업 #12”만 써 자동 종료·완전한 추적이 깨졌다. 형식 존재만 검사하지 말고 closing keyword까지 checklist로 검사해야 한다.

**관련 자료:** [PR 작성 규칙](docs/CONTRIBUTING.md#5-issue와-pr), [미충족 항목](SUBMISSION.md#3-요구사항-충족-현황)

### Q11. 리뷰가 LGTM에 그치지 않게 한 최소 품질 기준은 무엇인가?

**답변:** 최소 기준은 대상 파일·관찰·위험·개선안을 구체적으로 쓰고, 작성자가 반영 commit 또는 답글을 연결하는 것이다. 실제 반영 결과로 `reverse_string`의 타입 검사, `count_words`의 `strip()`, `remove_duplicates`의 순서 비보장 설명, `is_even`의 0·음수 설명이 있다. 다만 전체 19개 병합 PR을 확인했을 때 실질 텍스트 피드백이 확인되는 PR은 #2·#4·#7·#8·#24, 총 **5/19**뿐이다. 인당 승인 횟수와 별개로 “각 PR에 실질 코멘트 1개 이상” 요구는 미충족이다.

**관련 자료:** [리뷰 규칙과 실제 반영표](docs/CONTRIBUTING.md#6-코드-리뷰), [제출 인덱스](SUBMISSION.md)

### Q12. 충돌 발생 시 어떤 흐름으로 대응했는가?

**답변:** 권장 대응은 충돌 브랜치와 파일 공유 → `git status`와 양쪽 의도 확인 → 보존할 동작 합의 → 마커 제거와 `git add` → 실행 검증 → 해결 commit·문서 기록 순서다. `main.py`에서는 두 출력을 결합한 결과가 이력으로 확인된다. rename/modify 사례는 새 파일명과 수정 내용을 함께 보존한 통합 결과는 확인되지만, 독립 replay가 자동 병합되어 실제 충돌 발생 여부는 별도 증빙이 필요하다.

**관련 자료:** [이력 기반 충돌 기록](docs/conflict-resolution.md), [대응 규칙](docs/CONTRIBUTING.md#7-충돌-대응)

### Q13. 트러블슈팅 로그를 재현 가능하게 한 고정 항목은 무엇인가?

**답변:** 원격 원본 로그에는 참여자·상황·명령·결과·선택 이유·주의점이 있으나 모든 사례가 동일한 필드와 실행 증빙을 갖추지는 않았다. 다음은 **추가 권장 형식**이다: 참여자, 시작 상황, 실행 전 상태, 명령, 실행 후 결과, 선택 이유, 공유 여부, 주의점, 증빙 링크를 고정한다. 특히 reset처럼 최종 graph에서 이전 commit이 사라지는 명령은 전후 hash와 reflog를 캡처해야 한다. 이 형식은 재현성을 높이기 위한 보완안이지, 원격에서 이미 모두 기록됐다는 뜻은 아니다.

**관련 자료:** [네 복구 실습 기록](docs/troubleshooting-log.md)

---

## 항목 3 - 이론과 선택 이유

### Q14. `main`을 항상 배포 가능한 상태로 유지하는 이유는 무엇인가?

**답변:** `main`이 실행 가능한 기준선이면 기능 배포, 긴급 수정, 회귀 비교를 즉시 시작할 수 있다. 깨진 코드가 들어가면 네 팀원의 다음 브랜치가 모두 불안정한 기반에서 출발한다. 그래서 실제 프로젝트처럼 feature 브랜치에서 작업하고 승인된 PR merge로 통합한다.

**관련 자료:** [GitHub Flow](README.md#4-실제-github-flow-이해하기), [흐름 다이어그램](diagrams/01_github-flow.html)

### Q15. 직접 push 대신 PR과 승인을 사용하는 이유는 무엇인가?

**답변:** 품질 측면에서는 다른 사람이 오류와 경계 사례를 찾고, 책임 측면에서는 제안·검토·승인 주체가 분리되며, 추적성 측면에서는 Issue·diff·대화·검증·merge가 한곳에 남는다. 실제 저장소의 초기 commit 이후 main 통합은 모두 PR merge이고 확인한 병합 PR 19개 모두 승인이 있다. 세부 직접 push 차단 규칙은 설정 화면으로 보강한다.

**관련 자료:** [Branch Protection 확인 범위](SUBMISSION.md#1-팀과-저장소), [리뷰 규칙](docs/CONTRIBUTING.md#6-코드-리뷰)

### Q16. Issue-PR 연동은 왜 필요한가?

**답변:** 추적성 면에서 요구사항과 변경을 연결하고, 커뮤니케이션 면에서 완료 조건을 공유하며, 자동화 면에서 merge 시 Issue를 닫고 프로젝트 보드를 갱신할 수 있다. 이번 저장소는 19개 병합 PR 중 12개에서 `Closes #n`을 확인했지만 #15/#17/#18/#19/#20/#31/#32에는 closing link가 없었다. 이는 “관련 번호 언급”과 “closing link”가 다르다는 실제 학습 사례다.

**관련 자료:** [실제 연결 현황](README_answer.md#q3-각-pr이-issue와-연동되어-추적-가능한가), [PR 규칙](docs/CONTRIBUTING.md#5-issue와-pr)

### Q17. push된 commit은 reset보다 revert가 안전한 이유는 무엇인가?

**답변:** reset은 branch pointer를 과거로 옮겨 기존 commit을 원격에서 없애려면 force push가 필요하다. 동료의 local history와 갈라져 작업 손실 위험이 생긴다. revert는 반대 변경의 새 commit을 추가하므로 기존 hash와 역사를 보존하고 모두가 일반 pull로 같은 상태에 도달한다. reset은 아직 공유하지 않은 개인 브랜치에 제한한다.

**관련 자료:** [명령 선택표](docs/troubleshooting-log.md#명령-선택표), [복구 시각화](diagrams/03_git-recovery-decision.html)

### Q18. 충돌 마커와 비자명 충돌의 판단 기준은 무엇인가?

**답변:** `<<<<<<< HEAD` 아래는 현재 브랜치, `=======`는 경계, `>>>>>>> branch` 위는 합칠 브랜치의 내용이다. 비자명 충돌에서는 최신 줄이나 한쪽 전체를 기계적으로 고르지 않는다. 양쪽 Issue의 목적, 사용자에게 필요한 최종 동작, API 계약, 테스트, 파일의 최종 정체성을 기준으로 선택·결합·리팩터링한다. 원격 rename/modify 기록은 새 이름과 수정 내용을 모두 보존한 결과를 보여 주지만, 독립 replay가 자동 병합되었으므로 실제 비자명 충돌의 발생 증거와 해결 원칙 설명은 구분해야 한다.

**관련 자료:** [충돌 기록](docs/conflict-resolution.md), [충돌 해결도](diagrams/02_conflict-resolution.html)

---

## 항목 4 - 상황 판단과 심층 이해

Q19~Q21은 원격 저장소에서 실제로 수행된 사건을 보고하는 항목이 아니라, 확인된 팀 규칙과 Git 원리를 적용한 **가상 시나리오 답변**이다.

### Q19. 긴급 hotfix는 어떤 순서로 처리하는가?

**답변(가상 시나리오):** 최신 `main`에서 작은 fix branch 생성 → 원인과 범위가 명확한 수정 → 빠른 테스트 → Issue와 연결한 PR → 작성자 외 긴급 리뷰·승인 → `main` merge → 배포·모니터링 → 필요하면 revert 순서다. 긴급하다는 이유로 직접 push나 검증 생략을 허용하면 더 큰 장애가 날 수 있다. 아래는 수행 이력이 아니라 연습 절차다.

```bash
cd "$UPSTREAM_CLONE"
git switch main
git pull --ff-only origin main
git switch -c fix/heeyoung35-count-empty-input
# 수정과 검증
git push -u origin fix/heeyoung35-count-empty-input
```

**관련 자료:** [GitHub Flow](diagrams/01_github-flow.html), [PR 규칙](docs/CONTRIBUTING.md#5-issue와-pr)

### Q20. 의미 없는 commit 메시지를 이미 push했다면 어떻게 개선하는가?

**답변(가상 시나리오):** 먼저 공유 범위를 확인한다. 개인 feature 브랜치이고 다른 사람이 기반으로 작업하지 않았다면 팀에 공지하고 interactive rebase의 `reword`/`squash` 후 `--force-with-lease`를 제한적으로 쓸 수 있다. 이미 리뷰 중이거나 merge됐다면 history를 바꾸지 않고 PR 설명과 후속 commit에서 의도를 보완한다. `main`은 메시지 정리만을 위해 재작성하지 않는다.

**관련 자료:** [커밋 규칙](docs/CONTRIBUTING.md#4-커밋-메시지), [안전 규칙](docs/CONTRIBUTING.md#8-안전-규칙)

### Q21. 같은 파일·영역에서 충돌이 반복되면 어떻게 예방하는가?

**답변(가상 예방 시나리오):** 이력상 여러 기능이 모인 `main.py`와 rename·수정이 겹친 `old-guide.md`는 충돌 위험이 큰 지점이다. 일반적인 원인은 오래 사는 브랜치, 큰 작업, 소유권 불명확, 구조 변경 사전 공유 부족이다. Issue를 더 작게 나누고 최신 main을 자주 동기화하며, 공용 진입점 담당을 정하고, rename과 내용 변경을 별도 PR로 분리한다. 이는 재발을 가정한 예방안이며 실제 반복 장애 기록은 아니다.

**관련 자료:** [이력 기반 충돌 기록과 예방책](docs/conflict-resolution.md), [팀 역할](docs/CONTRIBUTING.md#1-팀-역할)

### Q22. rebase의 장점·위험과 안전 수칙은 무엇인가?

**답변(보너스 개념):** 원격 저장소에는 rebase 전후 비교 문서나 관련 PR이 없어 **보너스 수행 증빙은 확인되지 않는다.** 개념적으로 interactive rebase는 작은 WIP commit을 squash하고 메시지를 정리해 review history를 읽기 쉽게 한다. 하지만 부모 commit을 바꿔 새 hash를 만들므로 공유 브랜치에서 실행하면 동료 history와 갈라진다. 개인 branch의 공유 전 또는 명시적 팀 합의 후에만 사용하고, backup branch 생성·테스트·`--force-with-lease`를 지킨다. `main`에서는 하지 않는다.

**관련 자료:** [안전 규칙](docs/CONTRIBUTING.md#8-안전-규칙), [복구 의사결정](diagrams/03_git-recovery-decision.html)

---

## 심층 이해 튜토리얼

### 1. 네 함수에서 배우는 작은 PR 설계

실제 결과물은 작지만 협업 학습에 적합하다. 원격과 동일한 [main.py](src/main.py)는 `reverse_string`과 `count_words` 두 함수만 실행한다. 네 팀원의 모듈을 한 번에 살펴보는 코드는 원격 원본을 바꾸지 않고 [추가 학습 예시](examples/team_utils_demo.py)로 분리했다.

```python
# dave17code: 슬라이싱과 입력 계약
reverse_string("hello")  # "olleh"

# heeyoung35: 공백 정규화 후 단어 세기
count_words("  Hello   Git  ")  # 2

# OliverJoo: set 기반 중복 제거—순서는 보장되지 않음
remove_duplicates([1, 2, 2, 3])  # 원소 집합은 {1, 2, 3}

# hyunn9799: 나머지 연산으로 짝수 판별
is_even(-2)  # True
```

각 함수는 목적이 하나이고 독립 검증이 가능하다. 이런 단위는 review가 빠르고 문제가 생겼을 때 PR 하나를 revert하기 쉽다.

```bash
python3 src/main.py                 # 원격 main.py 그대로: 두 함수
python3 examples/team_utils_demo.py # 추가 학습 예시: 네 함수
```

**관련 코드:** [원격 실행 진입점](src/main.py), [4함수 추가 예시](examples/team_utils_demo.py), [string](src/string_utils.py), [count](src/count_utils.py), [list](src/list_utils.py), [math](src/math_utils.py)

### 2. Git의 세 공간과 복구 명령

현실 비유로 작업 디렉터리는 책상 위 원고, staging area는 제출 봉투, commit은 접수 도장이다.

- 파일 편집: 책상 위 원고만 변경
- `git add`: 선택한 원고를 봉투에 넣음
- `git commit`: 봉투 내용을 역사에 접수
- `reset --soft`: 접수만 취소하고 봉투는 유지
- `amend`: 가장 최근 접수 내용을 교체
- `stash`: 책상 위 원고를 임시 보관함으로 이동
- `revert`: 이전 접수를 지우지 않고 취소 문서를 새로 접수

```bash
cd "$UPSTREAM_CLONE"
git status
git diff
git diff --staged
git log --oneline -5
```

### 3. 텍스트 충돌과 논리 충돌

텍스트 충돌은 Git이 마커로 알려 준다. 논리 충돌은 자동 merge가 성공해도 두 변경의 가정이 어긋나는 경우다. 예를 들어 한 PR이 함수 인수 의미를 바꾸고 다른 PR이 예전 의미로 호출 코드를 추가하면 줄은 달라 자동 병합될 수 있지만 실행은 틀릴 수 있다.

따라서 충돌 마커를 제거한 뒤에도 실행과 요구사항 확인이 필요하다.

```bash
cd "$UPSTREAM_CLONE"
git diff --check
python3 src/main.py
git status
```

실제 `abe92b8` combined diff는 최종 동작을 사람이 결정해야 했음을 보여 준다.

### 4. merge commit을 읽는 방법

일반 commit은 부모가 하나지만 merge commit은 보통 부모가 둘이다. `abe92b8`의 첫 부모는 heeyoung35 작업선, 둘째 부모는 당시 `main`의 PR #15 결과다. `git show --cc`는 양쪽에서 달라진 줄과 최종 결합 결과를 한 번에 보여 준다.

```bash
cd "$UPSTREAM_CLONE"
git show --summary abe92b8
git show --cc abe92b8 -- src/main.py
git log --graph --oneline --all
```

이 방법은 “충돌을 해결했다”는 말보다 강한 증거다. 어떤 부모의 어느 내용을 보존했는지 확인할 수 있기 때문이다.

### 5. 리뷰 횟수와 리뷰 품질은 다르다

승인 2회 조건은 API로 셀 수 있지만, 품질은 코멘트와 후속 diff를 함께 봐야 한다. 다음 연결이 있어야 한다.

```text
구체적 피드백
  → 작성자 답변
  → 수정 commit
  → 재검증
  → 승인
```

이번 프로젝트의 네 기능 PR에는 실제 후속 commit이 있어 반영 결과를 확인할 수 있다. PR #24에도 구체적인 review 본문이 있다. 그러나 실질 텍스트 피드백이 확인되는 PR은 전체 19개 중 5개뿐이며, 나머지 다수는 빈 본문 승인 또는 단순 승인 문구다. 따라서 인당 review 횟수는 충족해도 “각 PR의 실질 review”는 미충족이다. 평가에서는 review URL과 반영 hash를 함께 제시한다.

### 6. 증빙 강도를 구분하는 법

모든 주장은 같은 수준으로 확인되지 않는다.

1. **코드로 확인:** 함수와 최종 동작
2. **Git으로 확인:** 작성자, hash, merge 구조, 최종 diff
3. **GitHub로 확인:** PR 본문, Issue link, review, collaborator, protected 여부
4. **설정 화면이 필요한 것:** 세부 required approvals, 직접 push 차단 규칙
5. **당시 화면이 필요한 것:** reset/stash 직후 상태, 충돌 터미널 출력

보고서에서 “완료”와 “추가 증빙 필요”를 나누면 과장 없이도 수행 내용을 더 설득력 있게 보여 줄 수 있다.

### 7. 최신 원격 상태를 읽는 법

원격 저장소는 계속 변하므로 확인 시점과 `main` commit을 함께 기록해야 한다. 2026-09-03 확인 결과 PR #32의 `80b43c2`는 OliverJoo의 승인을 거쳐 merge commit `daecf53`으로 반영됐다. 현재 열린 PR은 없으며, 이후 변경이 생기면 같은 방식으로 API와 실제 graph를 다시 교차 확인한다.

또한 원격 `docs/git-log.txt`는 PR #29까지를 담은 스냅샷이다. 파일이 저장된 뒤 병합된 PR #30·#31·#32는 실제 `git log`와 GitHub PR 페이지에서 추가 확인한다. 증빙 파일도 생성 시점을 함께 기록해야 낡은 스냅샷을 최신 상태로 오해하지 않는다.

**관련 자료:** [최신 원격 변경 전수 감사](docs/remote-change-audit.md), [Git 이력 증빙](docs/git-history-evidence.md)

### 8. 평가자에게 보여 주는 5분 흐름

1. [GitHub Flow](diagrams/01_github-flow.html)에서 정상 협업 흐름을 설명한다.
2. `python3 src/main.py`로 원격과 동일한 두 함수 실행 결과를 확인하고, 필요하면 `python3 examples/team_utils_demo.py`로 네 모듈을 학습용으로 함께 실행한다.
3. [팀원별 기여](SUBMISSION.md#2-팀원별-실제-기여)에서 4명의 PR·review를 확인한다.
4. [충돌 기록](docs/conflict-resolution.md)에서 `abe92b8`과 `fee0b98` 판단을 설명한다.
5. [복구 로그](docs/troubleshooting-log.md)에서 공유 여부에 따른 명령 선택을 설명한다.
6. [최신 원격 변경](docs/remote-change-audit.md)에서 PR #29~#32의 반영 상태를 확인한다.
7. [충족 현황](SUBMISSION.md#3-요구사항-충족-현황)에서 Issue closing 누락과 세부 보호 설정 증빙 보완점도 정직하게 제시한다.

```bash
cd "$UPSTREAM_CLONE"
python3 src/main.py
git log --oneline --graph --decorate --all
git show --cc abe92b8 -- src/main.py
```

---

## 심화 부록: Git 협업을 “이력 검증 시스템”으로 이해하기

이 부록은 앞에서 다룬 GitHub Flow, Issue–PR 연결, 충돌 해결, reset/revert/rebase 사용법을 반복하지 않는다. 작은 유틸리티 저장소에서 확인한 스냅샷·리뷰·병합 증거를 실제 팀의 재현성과 자동화 문제로 확장한다.

### 1. 커밋 해시는 무결성을 보여 주지만 작성자 신원까지 증명하지는 않는다

Git 객체 ID는 커밋 내용, 부모, 작성자 정보 등을 바탕으로 계산되므로 커밋 `daecf53...`를 고정하면 “그때 본 객체와 같은가”를 확인하기 좋다. 프로젝트의 SHA-256 스냅샷 테스트도 로컬 파일이 기준 바이트와 같은지 탐지한다. 그러나 해시가 같다는 사실만으로 그 기준값을 누가 만들었는지, 믿을 만한 배포인지까지 증명되지는 않는다.

현실적으로 공격자가 코드와 `EXPECTED` 해시를 함께 바꾸면 테스트는 다시 통과한다. 중요한 기준선은 보호된 CI 변수, 서명된 tag/release, 별도 감사 시스템처럼 변경 권한이 분리된 곳에 두어야 한다.

```bash
git tag -s training-baseline-2026-09 daecf53
git tag -v training-baseline-2026-09
```

즉 `hash = 무결성`, `signature + 신뢰한 공개키 = 출처 확인`으로 역할을 구분한다. 교육 제출물이라면 commit 고정만으로 충분할 수 있지만, 배포 승인에는 신뢰 사슬이 더 필요하다.

### 2. 서로 다른 커밋이 같은 변경인지 볼 때는 `patch-id`가 유용하다

rebase나 cherry-pick은 같은 코드 변경을 새 부모 위에 다시 만들기 때문에 commit hash가 달라진다. 이때 hash만 비교하면 동일 작업을 다른 작업으로 오판할 수 있다. `git patch-id --stable`은 메타데이터보다 diff의 실질 내용을 기준으로 비교하는 도구다.

예를 들어 `reverse_string` 타입 검사를 feature 브랜치에서 cherry-pick해 hotfix 브랜치에도 적용하면 두 commit ID는 달라도 패치가 같을 수 있다.

```bash
git show <commit-A> | git patch-id --stable
git show <commit-B> | git patch-id --stable
```

두 patch-id가 같으면 “실질 변경이 동등할 가능성이 높다”는 근거가 된다. 다만 파일 이동, 문맥 변화, 바이너리 변경 등에서는 한계가 있으므로 최종 트리와 테스트도 함께 본다. 협업 통계에서 단순 commit 수 대신 “독립 변경 단위”를 세려 할 때도 이 차이가 중요하다.

### 3. 회귀 원인은 `git bisect`로 선형 탐색 대신 이진 탐색할 수 있다

PR 수가 많아진 뒤 `count_words`의 빈 문자열 테스트가 깨졌다고 하자. 최근 commit부터 하나씩 되돌려 확인하면 n번 가까이 실행할 수 있지만, `git bisect`는 좋은 기준과 나쁜 기준 사이를 절반씩 좁혀 O(log n)번에 최초 불량 commit을 찾는다.

```bash
git bisect start
git bisect bad HEAD
git bisect good <정상으로 확인한-commit>
git bisect run python3 -m unittest tests.test_team_utils
git bisect reset
```

자동 bisect에 쓰는 테스트는 결과가 결정적이어야 한다. 네트워크 상태나 현재 시간에 따라 흔들리는 테스트라면 엉뚱한 commit을 지목한다. 또한 여러 원인이 동시에 있는 경우 “최초 bad”가 곧 전체 근본 원인이라는 뜻은 아니므로 해당 diff를 다시 검토한다.

### 4. 반복 충돌에는 `rerere`, 동시 작업에는 `worktree`가 도움 된다

긴 rebase에서 같은 충돌을 여러 번 풀거나, 병합을 시험했다 취소한 뒤 다시 풀 때 사람은 같은 결정을 반복하기 쉽다. `rerere`는 conflict 상태와 해결 결과를 기록해 같은 형태의 충돌에 이전 해결을 재사용한다.

```bash
git config rerere.enabled true
# 평소처럼 충돌 해결 후 git add / commit
git rerere status
```

자동 재사용 결과도 반드시 diff와 테스트로 검토해야 한다. 문맥은 같아 보여도 업무 의도가 달라졌을 수 있기 때문이다.

한편 긴급 수정 때문에 현재 feature 작업을 stash로 숨기는 대신 별도 worktree를 만들면 두 작업 디렉터리를 동시에 유지할 수 있다.

```bash
git worktree add ../b2-2-hotfix -b hotfix/count-words origin/main
git worktree list
```

호텔 방 두 개에 서로 다른 작업 도구를 펼쳐 두는 것과 같다. 다만 같은 브랜치를 두 worktree에서 동시에 checkout할 수 없고, 생성한 경로와 브랜치의 정리 책임을 팀 규칙에 포함해야 한다.

### 5. 사람의 규칙은 “브랜치 보호의 기계적 계약”으로 옮겨야 한다

문서에 What/Why/How와 리뷰 규칙이 있어도 누락은 발생한다. 실무에서는 PR template을 안내로 쓰되, required status checks, required review, 최신 base 반영, conversation resolution을 branch rule로 강제한다. 특정 영역은 `CODEOWNERS`로 담당 검토자를 자동 요청할 수 있다.

```text
# .github/CODEOWNERS 예시
/src/        @team-python
/docs/       @team-docs
/.github/    @repo-maintainers
```

예를 들어 문서 담당 승인만 받고 `src/` 변경을 병합하는 문제를 줄일 수 있다. 단, CODEOWNERS가 자동 요청하는 것과 “그 소유자의 승인 없이는 병합 불가”는 별도 보호 규칙이다. CI도 단순 `grep` 존재 검사만 두기보다 실제 단위 테스트, 링크 검사, 원본 스냅샷 검사를 서로 다른 check로 보여 주면 실패 원인과 재실행 권한이 명확해진다.

### 6. Git의 rename은 파일 신원이 아니라 유사도에 대한 사후 판단이다

Git은 파일에 영구 ID를 붙여 “이 파일이 이름만 바뀌었다”고 저장하지 않는다. 한 경로의 삭제와 다른 경로의 추가를 비교할 때 내용 유사도가 충분하면 rename으로 표시한다. 그래서 같은 commit도 옵션과 임계값에 따라 `R100`, `R60`, 또는 delete/add로 보일 수 있다.

```bash
git diff --find-renames=50% <parent> <commit>
git diff --find-renames=90% <parent> <commit>
```

이 사실은 rename/modify 충돌 증빙에 중요하다. 최종 `git show --summary`의 `R100`만으로 “당시 사용자가 실제 충돌 마커를 해결했다”까지 증명할 수 없다. 재현 절차에서는 공통 merge base, 양쪽 tree, 실제 merge 명령의 stdout/stderr와 exit code를 함께 보존해야 한다.

### 실무 접근법

#### 접근법 1. 병합 전 disposable worktree에서 통합을 예행연습한다

PR head를 임시 worktree에 두고 대상 base를 merge 또는 rebase한 뒤 전체 테스트를 실행한다. 원래 작업 디렉터리를 건드리지 않아 충돌 재현과 증거 캡처가 쉽다. 성공 기준은 “충돌 마커가 없다”가 아니라 양쪽 요구사항 테스트가 모두 통과하는 것이다.

#### 접근법 2. 증거를 주장과 분리된 원시 자료로 보존한다

PR 번호, review state, commit hash를 문장으로만 옮기지 말고 조회 시각과 함께 API JSON 또는 명령 출력으로 저장하고, 그 파일의 해시를 manifest에 기록한다. 문서는 이 원시 자료에서 계산되도록 하면 “19개”처럼 바뀌는 숫자를 수동으로 여러 파일에 복사하다 생기는 불일치를 줄일 수 있다. 개인정보·토큰은 원시 자료에 포함하지 않는다.

#### 접근법 3. CI를 요구사항 추적표와 1:1로 연결한다

각 요구사항에 `자동 검사`, `API로 확인`, `사람이 캡처` 중 검증 방식을 지정한다. 함수 동작과 링크는 자동화하고, 실제 리뷰의 질이나 화면 설정은 사람 검토 대상으로 남긴다. 자동화할 수 없는 항목을 억지로 `grep` 통과로 치환하지 않는 것이 핵심이다. PR 화면에는 실패한 요구사항 이름과 복구 방법이 바로 보이게 한다.
