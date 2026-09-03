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

**1. 핵심 개념 및 단일 진실 공급원(SSOT) 기준:**
- **개념**: 팀 협업의 신뢰성을 보장하기 위해 모든 팀원이 하나의 공식 중앙 원격 저장소(Single Source of Truth)를 공유해야 하며, 역할 기반 권한 분담(Role-based Access Control)을 통해 무단 변경을 방지하면서도 원활한 기여(PR 및 리뷰)가 가능해야 한다.

**2. 실제 프로젝트 수행 현황 및 증빙:**
- **단일 원격 저장소**: [dave17code/b2-2-git-conflict-craft](https://github.com/dave17code/b2-2-git-conflict-craft) 1개 저장소를 공식 베이스로 구축하여 팀 전체가 공유했다.
- **팀원 4인 권한 구성 (GitHub Collaborators API 검증)**:
  - `dave17code` (Admin): 저장소 생성 및 브랜치 보호 정책 등 거버넌스 설정 총괄.
  - `heeyoung35`, `OliverJoo`, `hyunn9799` (Push/Write Collaborator): 피처 브랜치 생성, 푸시, PR 생성 및 상호 코드 리뷰 권한 보유.
- **기여 일치성 검증**: 로컬 Git 커밋 author 이메일과 원격 GitHub PR/Review 활동 내역이 4명 모두 일치하여 실명 기반 협업 책임을 명확히 했다.

**3. 권한 설계 원칙 및 안전 수칙:**
- `Admin` 권한을 저장소 관리자 1인으로 최소화하여 보안 사고를 예방했다.
- 일반 팀원에게 `Write` 권한을 부여하되 `main` 브랜치 직접 푸시는 원천 차단하고, 반드시 피처 브랜치를 통한 Pull Request와 동료 승인을 거치도록 강제했다.

**관련 자료:** [팀원별 실제 기여](SUBMISSION.md#2-팀원별-실제-기여), [Git 이력 증빙](docs/git-history-evidence.md)

### Q2. `main`에 Branch Protection이 설정되어 있고, 직접 push 없이 PR로만 병합되었는가?

**1. 브랜치 보호(Branch Protection)의 정의 및 목적:**
- **정의**: 프로덕션 배포 기준선인 `main` 브랜치에 대해 개발자의 부주의한 직접 푸시(`git push origin main`), 히스토리 삭제/덮어쓰기(`--force`), 브랜치 임의 삭제를 시스템적으로 차단하는 GitHub 거버넌스 규칙이다.
- **목적**: 모든 코드가 반드시 코드 리뷰와 품질 검증을 거쳐서만 통합되도록 강제하여 `main`의 상시 배포 가능 상태(Deployable State)를 수호한다.

**2. 실제 프로젝트 수행 현황 및 무결성 검증:**
- **Branch Protection 활성화**: GitHub Branch API 확인 결과 `main` 브랜치의 `protected: true` 설정이 검증되었다.
- **직접 push 0건 및 100% PR 병합**:
  - 초기 커밋(`175ea3c`) 이후 `main`에 반영된 모든 통합(총 19건)은 예외 없이 2-parent Merge Commit 형태로 기록되었다 (First-parent 무결성 유지).
  - 병합된 19개 PR 모두 최소 1인 이상의 동료 승인(`APPROVED` 리뷰)을 획득한 후에만 병합 버튼이 활성화되어 통합되었다.

**3. 실무 지침 및 세부 설정 권장사항:**
- `Require a pull request before merging` (최소 1명 이상 승인 필수 설정).
- `Dismiss stale pull request approvals when new commits are pushed` (새 커밋 푸시 시 이전 승인 자동 취소 및 재검토 유도).
- `Do not allow bypassing the above settings` (관리자도 예외 없이 규칙을 준수하도록 강제).

**관련 자료:** [요구사항 충족 현황](SUBMISSION.md#3-요구사항-충족-현황), [협업 규칙](docs/CONTRIBUTING.md#8-안전-규칙), [흐름 다이어그램](diagrams/01_github-flow.html)

### Q3. 각 PR이 Issue와 연동되어 추적 가능한가?

**1. 추적성(Traceability) 연동의 개념 및 필요성:**
- **개념**: 요구사항(Issue)과 이를 해결한 구현체(PR)를 명시적으로 링크하여 "왜 이 코드가 변경되었는가"에 대한 비즈니스 맥락(Context)을 영구 보존하고, PR 병합 시 해당 Issue를 자동으로 종결시키는 엔지니어링 실천법이다.

**2. 실제 프로젝트 연동 현황 및 분석:**
- **키워드 자동 연동 (12개 PR)**:
  - PR #2, #4, #7, #8, #11, #14, #16, #22, #24, #26, #29, #30 등 총 12개 PR은 본문에 `Closes #n` / `Fixes #n`을 정확히 기재하여, 병합과 동시에 Issue 자동 닫힘과 양방향 추적성을 완벽하게 달성했다.
- **수동/단순 언급 연동 (7개 PR)**:
  - PR #15, #17, #18, #19, #20, #31, #32의 경우 PR 본문에 "관련 작업 #12", "충돌 실습 연계" 등 텍스트 언급은 남겼으나 GitHub 예약어(`Closes`)가 누락되어 자동 종료가 연동되지 않았다.

**3. 실무 개선 가이드 및 표준화 규칙:**
- '단순 이슈 번호 언급(#12)'은 단순 하이퍼링크만 생성할 뿐 이슈의 라이프사이클을 전이시키지 못한다.
- PR 템플릿(`.github/pull_request_template.md`)에 `Closes #<Issue 번호>` 입력을 필수 항목으로 지정하고, PR 머지 전 리뷰어가 연동 키워드 포함 여부를 검증 체크리스트로 관리해야 한다.

**관련 자료:** [실제 PR 목록](SUBMISSION.md#2-팀원별-실제-기여), [PR 규칙](docs/CONTRIBUTING.md#5-issue와-pr)

### Q4. 팀원별 PR 2개 이상이 병합되었는가?

**1. 평가 기준 및 목적:**
- 모든 팀원이 단순히 코드를 작성하는 데 그치지 않고, 독립된 작업 브랜치 운영 → PR 생성 → 피어 리뷰 통과 → `main` 병합까지 이어지는 협업 사이클을 인당 최소 2회 이상 완수하여 실질적인 기여도를 증명해야 한다.

**2. 팀원 4인 전원 기준 초과 달성 현황 (총 19건 병합):**
- **`dave17code` (총 6건 병합)**:
  - PR #2: `feat: add reverse_string` (핵심 기능)
  - PR #11: `refactor(troubleshoot): amend commit message` (amend 실습)
  - PR #15: `feat: update main.py for string reverse` (main.py 충돌 생성)
  - PR #30: `docs: update troubleshooting log`
  - PR #31: `docs: update conflict resolution`
  - PR #32: `docs: add contributing and submission guidelines`
- **`heeyoung35` (총 2건 병합)**:
  - PR #4: `feat: add count_words utility` (핵심 기능)
  - PR #14: `feat: update main.py for count_words` (main.py 충돌 생성 및 결합)
- **`OliverJoo` (총 6건 병합)**:
  - PR #7: `feat: add remove_duplicates` (핵심 기능)
  - PR #16: `feat: add duplicate remover demo`
  - PR #17: `conflict: add conflicting guide section`
  - PR #19: `conflict: modify intro in guide`
  - PR #22: `refactor: rename old-guide.md to new-file.md` (비자명 rename 충돌)
  - PR #29: `revert: undo accidental file push` (revert 복구 실습)
- **`hyunn9799` (총 5건 병합)**:
  - PR #8: `feat: add is_even function` (핵심 기능)
  - PR #18: `feat: add even check demo`
  - PR #20: `conflict: modify guide summary`
  - PR #24: `docs: update content in old-guide.md` (비자명 modify 충돌)
  - PR #26: `refactor(troubleshoot): demonstrate git stash workflow` (stash 실습)

**3. 검증 방법**:
- GitHub REST API `merged_at` 필드 및 원격 first-parent 머지 커밋 로그(`git log --merges --first-parent`)를 교차 대조하여 전원 2회 이상 병합 기준을 100% 충족함을 확인했다.

**관련 자료:** [팀원별 PR 링크](SUBMISSION.md#2-팀원별-실제-기여), [Git 이력 증빙](docs/git-history-evidence.md)

### Q5. 팀원별 리뷰 2개 이상과 본인 PR의 피드백 반영 1회가 있는가?

**1. 상호 코드 리뷰 및 피드백 반영의 정의:**
- 단순 승인(Approve)을 넘어 동료의 코드에서 잠재적 결함, 경계 조건(Edge case), 가독성 문제를 능동적으로 발굴하여 개선을 요구하고, PR 작성자가 이를 수용해 추가 커밋으로 코드를 개선하는 유기적 협업 과정이다.

**2. 실제 프로젝트 수행 현황 및 통계:**
- **팀원별 타인 PR 승인 리뷰 (4인 전원 2건 이상 충족)**:
  - `dave17code` (4건): PR #4, #14, #26, #29 승인
  - `heeyoung35` (2건): PR #2, #11 승인
  - `OliverJoo` (7건): PR #8, #18, #20, #24, #30, #31, #32 승인
  - `hyunn9799` (6건): PR #7, #15, #16, #17, #19, #22 승인
- **팀원 4인 전원 피드백 반영 커밋 완수 (100% 충족)**:
  - `dave17code` (PR #2): heeyoung35의 "문자열 타입 유효성 검증 필요" 리뷰 반영 → 커밋 `5e171a9`로 `isinstance(text, str)` 방어 로직 추가.
  - `heeyoung35` (PR #4): dave17code의 "다중 공백 및 앞뒤 공백 정규화" 리뷰 반영 → 커밋 `e47ac39`로 `strip()` 및 정규화 적용.
  - `OliverJoo` (PR #7): hyunn9799의 "set 변환 시 순서 비보장 특성 명시" 리뷰 반영 → 커밋 `db5ae1a`로 docstring 설명 보강.
  - `hyunn9799` (PR #8): OliverJoo의 "0 및 음수에 대한 짝수 판별 기준 설명" 리뷰 반영 → 커밋 `38ab44f`로 경계 조건 문서화.

**3. 실무 인사이트 및 개선점:**
- 초기 모듈 구현 PR들에서는 매우 수준 높은 코드 레벨 피드백과 수정 커밋이 완벽하게 이루어졌다. 후속 실습 PR들에서도 단순 승인 대신 최소 1개의 구체적 관찰 코멘트를 남기는 문화가 정착되도록 가이드라인을 보강했다.

**관련 자료:** [review와 반영 commit 링크](SUBMISSION.md#2-팀원별-실제-기여), [리뷰 규칙](docs/CONTRIBUTING.md#6-코드-리뷰)

### Q6. 충돌 기록이 2회 이상이고 비자명 충돌이 포함되는가?

**답변:** **충족한다.** 저장소에는 2회 이상의 충돌 실습 및 해결 이력이 명확히 기록되어 있으며, 비자명 충돌(Rename vs Modify) 시나리오가 포함되어 있다.

1. **동일 영역 텍스트 충돌 (`src/main.py`)**:
   - dave17code(PR #15)와 heeyoung35(PR #14)가 진입점 및 실행 블록을 동시에 수정하여 발생한 충돌이다.
   - 어느 한쪽을 덮어쓰지 않고 두 유틸리티(`reverse_string`, `count_words`)의 기능과 출력을 모두 결합하여 merge commit `abe92b8`의 combined diff로 온전히 해결·보존했다.
2. **비자명 충돌 (`docs/old-guide.md` Rename vs Modify)**:
   - OliverJoo가 파일명을 `docs/new-file.md`로 변경(PR #22)하고, hyunn9799가 기존 파일 내용을 수정한(PR #24) 비자명 충돌 시나리오다.
   - 파일명 변경과 수정된 본문 내용을 모두 유실 없이 보존하여 merge commit `9315e23` 및 후속 커밋 `fee0b98`로 최종 통합했다.
3. **충돌 실습 및 해결 체인**:
   - 이외에도 충돌 생성·재현 및 협업 절차를 검증하기 위해 PR #16, #17, #18, #19, #20, #22, #24 등 다수의 연계 PR과 [이력 기반 충돌 기록](docs/conflict-resolution.md) 문서를 체계적으로 남겼다. (Git의 삼방향 병합 rename 탐지 휴리스틱 동작 분석 및 팀 협업 예방 가이드 포함)

**관련 자료:** [이력 기반 충돌 기록](docs/conflict-resolution.md), [충돌 시각화](diagrams/02_conflict-resolution.html), [팀원별 실제 기여](SUBMISSION.md#2-팀원별-실제-기여)

### Q7. amend/reset/revert/stash 4종과 팀원별 참여 기록이 있는가?

**1. 4대 Git 복구 명령의 정의 및 용도:**
- **`amend`**: 최근 로컬 커밋의 메시지 오타나 누락된 변경사항을 직전 커밋에 덮어써서 커밋을 깔끔하게 유지할 때 사용.
- **`reset (--soft)`**: 커밋된 작업을 취소하되 작업 트리를 날리지 않고 Staging Area로 안전하게 되돌려 재작업할 때 사용.
- **`revert`**: 이미 원격에 푸시/공유된 커밋을 삭제하지 않고 정반대의 취소 역커밋을 생성하여 안전하게 롤백할 때 사용.
- **`stash`**: 작업 중인 미완성 변경사항을 임시 저장 스택에 보관하고 브랜치를 자유롭게 전환할 때 사용.

**2. 실제 프로젝트 수행 현황 및 팀원별 분담 증빙:**
- **`amend` (dave17code)**:
  - 상황: 직전 로컬 커밋 메시지 오타 수정.
  - 실행: `git commit --amend -m "..."` 실행 후 커밋 해시 변화 검증 (PR #11 본문에 전후 해시 기록).
- **`reset --soft` (heeyoung35)**:
  - 상황: 미완성 커밋을 취소하되 작성된 코드를 Staging Area에 온전히 보존.
  - 실행: `git reset --soft HEAD~1` 실행으로 `HEAD` 포인터만 이전으로 이동시키고 인덱스 유지.
- **`revert` (OliverJoo)**:
  - 상황: 이미 원격 `main`에 병합된 임시 파일 커밋(`df3e50c`)을 안전하게 취소.
  - 실행: `git revert df3e50c`로 역커밋 `7a37beb`를 생성하여 충돌 없이 PR #29로 무결 통합.
- **`stash / pop` (hyunn9799)**:
  - 상황: 기능 구현 도중 타 브랜치의 긴급 확인 요청 발생.
  - 실행: `git stash`로 작업 트리 임시 보관 → 브랜치 전환 및 확인 → `git stash pop`으로 복구 (PR #26 본문에 절차 기록).

**3. 안전 기준 및 재현성 강화 지침:**
- `revert`나 `amend`는 Git 커밋 히스토리에 명확한 증빙이 남지만, `reset`은 이전 커밋이 그래프에서 분리되므로 `reflog` 기록 및 전후 상태 스크린샷을 남겨 재현성을 완벽히 확보해야 한다.

**관련 자료:** [증빙 수준과 절차](docs/troubleshooting-log.md), [복구 시각화](diagrams/03_git-recovery-decision.html), [팀원별 실제 기여](SUBMISSION.md#2-팀원별-실제-기여)

### Q8. 필수 문서 세 개가 존재하고 구조를 갖추었는가?

**1. 협업 문서화의 목적 및 엔지니어링 의의:**
- 팀 프로젝트의 규칙이 구두나 파편화된 메신저에 머무르지 않고, 저장소 코드와 함께 버전 관리되는 체계적인 가이드라인 및 사후 분석 보고서(Post-mortem)로 정립되어야 한다.

**2. 3대 필수 문서의 구조 및 세부 내용:**
1. **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) (협업 프로세스 표준 가이드)**:
   - 팀 역할 정의, GitHub Flow 3대 원칙, 브랜치 네이밍 컨벤션, 커밋 메시지 규칙, PR 4대 템플릿(What/Why/How), 코드 리뷰 최소 품질 기준, 충돌 대응 6단계 워크플로우, force push 금지 등 8대 핵심 섹션을 완비.
2. **[docs/conflict-resolution.md](docs/conflict-resolution.md) (이력 기반 충돌 해결 보고서)**:
   - 기록 1(`main.py` 라인 충돌) 및 기록 2(`old-guide.md` rename vs modify 비자명 충돌)에 대해 [참여자, 발생 상황, 양측 의도, 판단 근거, 통합 해결책, 재발 예방 대책]을 표준 스키마로 기록.
3. **[docs/troubleshooting-log.md](docs/troubleshooting-log.md) (트러블슈팅 및 복구 실습 로그)**:
   - 4대 복구 명령(`amend`, `reset --soft`, `revert`, `stash`)에 대해 [담당자, 문제 배경, 실행 전 상태, 실행 명령어, 선택 이유, 실행 후 결과, 협업 주의점]의 7대 고정 항목을 정의하고 의사결정 매트릭스를 제공.

**3. 문서 무결성 평가:**
- 3개 문서 모두 마크다운 표준 링크, 코드 블록, 표를 포함하여 체계적인 구조를 갖추었으며, 실제 발생한 커밋 및 PR과 1:1로 매핑되어 실효성 높은 협업 자산으로 기능한다.

**관련 자료:** [CONTRIBUTING.md](docs/CONTRIBUTING.md), [conflict-resolution.md](docs/conflict-resolution.md), [troubleshooting-log.md](docs/troubleshooting-log.md)

---

## 항목 2 - 코드와 문서 설계 설명

### Q9. 브랜치를 “작업 단위”로 나누는 기준은 무엇인가?

**1. 작업 단위(Unit of Work)의 정의 및 원칙:**
- **단일 책임 원칙 (Single Responsibility)**: 하나의 브랜치는 오직 하나의 명확한 목표(단일 Issue)만을 해결해야 하며, 무관한 작업이 섞이지 않아야 한다.
- **검토 용이성 (Reviewable Scope)**: 동료 리뷰어가 10~15분 내에 diff 전체의 설계와 맥락을 파악할 수 있는 적절한 크기(보통 1~2개 파일, 200~300줄 이하)여야 한다.
- **독립적 배포 및 회귀 가능성 (Atomic & Revertible)**: 해당 기능에 결함이 발생했을 때 다른 정상 기능에 부작용을 주지 않고 단일 `git revert <merge-commit>`으로 안전하게 롤백될 수 있어야 한다.

**2. 실제 프로젝트 적용 사례:**
- **기능별 모듈 격리 개발**:
  - `dave17code`: `feature/dave17code-reverse-string` (문자열 뒤집기 모듈에만 집중)
  - `heeyoung35`: `feature/heeyoung35-count-words` (단어 수 세기 모듈에만 집중)
  - `OliverJoo`: `feature/oliverjoo-remove-duplicates` (중복 제거 모듈에만 집중)
  - `hyunn9799`: `feature/hyunn9799-is-even` (짝수 판별 모듈에만 집중)
- **공용 진입점 분리**:
  - 공용 실행 파일인 `src/main.py` 수정 작업은 개별 기능 구현 PR과 혼합하지 않고, 별도의 통합 PR(PR #14, #15)로 분리하여 불필요한 광범위 충돌을 방지했다.

**3. 분기 및 관리 수칙:**
- 브랜치 수명이 길어질수록 main과의 베이스 차이로 인해 충돌 확률이 급증하므로, 1~2일 내에 리뷰 및 머지가 완료될 수 있도록 태스크를 최소 단위로 쪼개어 브랜치를 생성한다.

**관련 자료:** [원격 원본 코드 표](README.md#12-원격-원본-코드와-추가-예제), [브랜치 규칙](docs/CONTRIBUTING.md#3-브랜치-이름)

### Q10. What/Why/How와 Issue 연동을 일관되게 남긴 방법은 무엇인가?

**1. PR 본문 표준화(Template)의 목적:**
- 리뷰어가 코드(Diff)만 보고 작성자의 의도를 추측하는 인지적 비용을 줄이고, 변경의 배경과 검증 증빙을 표준화된 양식으로 제공하여 리뷰 품질과 히스토리 자산 가치를 극대화한다.

**2. PR 4대 필수 섹션 구조 (Schema):**
1. **연동 Issue (`Closes #<Issue 번호>`)**:
   - PR 병합 시 GitHub가 연결된 이슈를 자동으로 닫을 수 있도록 표준 예약어 지정.
2. **What (무엇을 변경했는가)**:
   - 변경된 핵심 파일, 추가된 함수 및 모듈의 명확한 요약.
3. **Why (왜 변경했는가)**:
   - 해당 작업이 필요했던 비즈니스/기술적 배경 및 해결하려는 문제점 기술.
4. **How (어떻게 구현하고 검증했는가)**:
   - 사용한 알고리즘, 경계값 예외 처리 방식, 로컬 실행 명령어(`pytest`, 실행 스크립트) 및 테스트 통과 증빙 기술.

**3. 실제 프로젝트 적용 및 실무 교훈:**
- 실제 PR #2, #4, #7, #8 등 핵심 기능 PR에서 4개 영역을 철저히 구분하여 작성했다.
- 일부 충돌 실습 PR에서 `Closes #n` 대신 "관련 작업 #12"와 같은 자유 텍스트를 사용하여 자동 닫힘이 누락된 사례를 확인했으며, 이를 계기로 GitHub PR 템플릿(`.github/pull_request_template.md`)과 리뷰 체크리스트에 키워드 검증을 필수화하는 실무 표준을 정립했다.

**관련 자료:** [PR 작성 규칙](docs/CONTRIBUTING.md#5-issue와-pr), [SUBMISSION.md PR 목록](SUBMISSION.md#2-팀원별-실제-기여)

### Q11. 리뷰가 LGTM에 그치지 않게 한 최소 품질 기준은 무엇인가?

**1. 실행 가능한 피드백(Actionable Feedback)의 정의:**
- 단순한 형식적 찬사("Looks Good To Me")는 잠재적 결함을 예방하지 못한다. 진정한 코드 리뷰는 코드의 논리 무결성, 엣지 케이스 예외 처리, 네이밍 및 가독성을 능동적으로 점검하고 구체적인 대안을 제시하는 엔지니어링 토론이어야 한다.

**2. 팀이 수립한 4단계 리뷰 최소 품질 기준:**
1. **구체적 위치 명시 (Location)**: 파일명과 라인 번호를 정확히 타겟팅.
2. **관찰된 리스크 (Risk & Defect)**: 현재 코드가 야기할 수 있는 예외(Exception)나 비효율 지적.
3. **원인 및 근거 (Rationale)**: 언어 동작 특성이나 사용자 시나리오에 기반한 기술적 근거 제시.
4. **대안 코드 스니펫 (Alternative)**: 리뷰어가 제안하는 구체적인 코드 작성.

**3. 실제 프로젝트 적용 성과 (4대 핵심 PR 반영):**
- `PR #2` (heeyoung35 → dave17code): 문자열 외 입력 시 `TypeError` 발생 가능성 지적 → `isinstance(text, str)` 방어 로직 커밋(`5e171a9`) 반영.
- `PR #4` (dave17code → heeyoung35): 연속 공백이나 앞뒤 공백 시 잘못된 단어 수 카운트 지적 → `strip()` 및 정규화 커밋(`e47ac39`) 반영.
- `PR #7` (hyunn9799 → OliverJoo): Python `set()` 사용 시 입력 순서가 섞이는 특성 안내 누락 지적 → docstring 경고 커밋(`db5ae1a`) 반영.
- `PR #8` (OliverJoo → hyunn9799): 0 및 음수 정수의 짝수 판별 경계 조건 모호성 지적 → 주석 및 명세 보강 커밋(`38ab44f`) 반영.

**4. 통계 및 고도화 방향:**
- 19개 전체 병합 PR 중 코드 레벨 텍스트 리뷰가 집중된 PR은 5건(#2, #4, #7, #8, #24)이며, 나머지 충돌/복구 실습 PR은 빠른 진행을 위해 승인(Approve) 위주로 처리되었다. 향후 실무에서는 모든 PR에 최소 1개 이상의 관찰 질문을 남기도록 룰을 고도화했다.

**관련 자료:** [리뷰 규칙과 실제 반영표](docs/CONTRIBUTING.md#6-코드-리뷰), [제출 인덱스](SUBMISSION.md)

### Q12. 충돌 발생 시 어떤 흐름으로 대응했는가?

**답변:** 충돌 발생 시 독단적으로 한쪽 코드를 덮어쓰지 않고, **[감지 및 공유 → 의도 분석 → 보존 합의 → 편집 및 마커 제거 → 로컬 실행 검증 → 스테이징/커밋 → 문서화]**의 7단계 체계적 프로세스로 대응했다.

1. **상황 감지 및 팀 공유**:
   - `git merge` 또는 `git pull` 시 `CONFLICT`가 발생하면, 즉시 팀 채널과 PR에 충돌 브랜치, 대상 파일, 상대 작업자(작성자)를 공유하여 중복 수정을 방지했다.
2. **원인 및 양측 의도 파악 (`git status` & Diff)**:
   - `git status`로 충돌 상태(`both modified` 등 unmerged paths)를 파악하고, 파일 내 충돌 마커(`<<<<<<< HEAD`, `=======`, `>>>>>>>`)와 연결된 각 Issue/PR의 목적을 대조했다.
3. **보존 동작 합의 및 해결 (의사결정)**:
   - 기계적으로 최신 라인을 선택하지 않고, 양쪽 변경이 모두 프로젝트에 필요한지 검토했다.
   - **동일 영역 충돌 (`src/main.py`)**: dave17code의 `reverse_string`과 heeyoung35의 `count_words`는 상호 배타적이지 않은 필수 모듈이므로, 둘 다 버리지 않고 `import`와 실행 출력문을 모두 살려 `if __name__ == "__main__":` 블록 아래로 통합 결합했다.
   - **비자명 충돌 (`docs/old-guide.md`)**: OliverJoo의 파일명 변경(`new-file.md`)과 hyunn9799의 가이드 문서 내용 수정을 모두 수용하여, 변경된 새 파일 경로에 수정 본문을 온전히 반영함으로써 정보 유실을 방지했다.
4. **충돌 마커 제거 및 코드 정리**:
   - 편집기에서 `<<<<<<<`, `=======`, `>>>>>>>` 등 Git 마커를 완전히 제거하고 코드 스타일과 들여쓰기를 정돈했다.
5. **로컬 실행 및 무결성 검증 (Execution Test)**:
   - 파일 수정 직후 바로 커밋하지 않고, `python3 src/main.py` 실행 및 유닛 테스트를 직접 수행하여 문법 에러나 논리적 충돌(Logical Conflict)이 없는지 동작을 검증했다.
6. **스테이징 및 해결 커밋 (`git add` & Commit)**:
   - 검증 통과 후 `git add <file>`로 충돌 해결 상태를 확정하고, 충돌 해결 사유와 통합 내역을 명시한 Merge Commit(`abe92b8`, `9315e23`)을 작성했다.
7. **충돌 해결 기록 문서화**:
   - [conflict-resolution.md](docs/conflict-resolution.md)에 참여자, 충돌 상황, 판단 근거, 최종 결과, 예방 조치를 기록하여 팀원 간 지식을 공유하고 재발을 방지했다.

**관련 자료:** [이력 기반 충돌 기록](docs/conflict-resolution.md), [대응 규칙](docs/CONTRIBUTING.md#7-충돌-대응), [충돌 해결 다이어그램](diagrams/02_conflict-resolution.html)

### Q13. 트러블슈팅 로그를 재현 가능하게 한 고정 항목은 무엇인가?

**답변:** 트러블슈팅 로그([docs/troubleshooting-log.md](docs/troubleshooting-log.md))는 다른 팀원이나 평가자가 동일한 장애·복구 상황을 그대로 재현하고 검증할 수 있도록 다음 **7가지 핵심 고정 항목(Schema)**을 정의하여 일관되게 기록했다.

1. **담당자 (Actor)**:
   - 복구 작업을 수행한 팀원 GitHub 계정을 명시하여 책임 소재와 협업 역할을 분리했다.
2. **발생 상황 및 문제 배경 (Context & Trigger)**:
   - 어떤 작업 중에 어떤 문제가 발생했는지 구체적인 상황을 기술했다. (예: 직전 커밋 메시지 오타 발생, 미완성 커밋 분리 필요, 원격 공유 브랜치의 잘못된 커밋 롤백, 작업 중 긴급 컨텍스트 전환 등)
3. **실행 전 상태 (Pre-condition)**:
   - 작업 직전의 브랜치명, `git status`, 최근 커밋 해시(`git log -1`) 등 초기 조건을 확인했다.
4. **실행 명령어 및 절차 (Command & Procedure)**:
   - 사용한 Git 명령어와 필수 옵션(`commit --amend`, `reset --soft HEAD~1`, `revert <hash>`, `stash` / `stash pop`) 및 실행 순서를 정확히 기록했다.
5. **명령 선택 이유 (Rationale & Decision)**:
   - 대안 명령(예: 공유 커밋에 `reset` 대신 `revert`를 선택한 이유, 작업 내용을 날리지 않기 위해 `reset --hard` 대신 `reset --soft`를 선택한 이유 등)과 비교하여 Git 동작 원리에 기반한 판단 근거를 서술했다.
6. **실행 후 결과 및 검증 (Post-condition & Verification)**:
   - 명령 수행 후 `git status`의 변화, 스테이징 영역 상태, 새 커밋 해시 생성 여부, `git log` 히스토리 등을 확인하여 문제가 완전히 해결되었음을 입증했다.
7. **팀 협업 주의점 및 안전 수칙 (Safety Rules & Caveats)**:
   - 로컬 전용 명령과 원격 공유 브랜치 금지 수칙, force-push 위험성, 히스토리 소실 방지 주의점을 명시했다.

**실제 적용 사례 (4대 복구 명령)**:
- **`amend` (dave17code)**: 최근 로컬 커밋 메시지 오타 수정 및 전후 해시 변화 검증 (PR #11 본문).
- **`reset --soft` (heeyoung35)**: 미완성 커밋을 취소하되 작업 내용은 Staging Area에 온전히 보존하여 후속 작업으로 연결.
- **`revert` (OliverJoo)**: 이미 `main`에 push된 임시 파일 커밋(`df3e50c`)을 삭제하지 않고 역커밋(`7a37beb`)을 생성하여 협업자 충돌 없이 히스토리 보존 (PR #29, PR #32).
- **`stash / pop` (hyunn9799)**: 미완성 작업 트리를 임시 보관 스택에 저장하고 브랜치 전환 후 안전하게 복원 (PR #26 본문).

특히 `reset`이나 `amend`처럼 커밋 그래프에서 이전 해시가 덮어써지는 명령은 `reflog` 및 실행 전후 화면을 증빙으로 보존하는 안전 기준까지 함께 정립했다.

**관련 자료:** [네 복구 실습 기록](docs/troubleshooting-log.md), [복구 결정 다이어그램](diagrams/03_git-recovery-decision.html), [팀원별 실제 기여](SUBMISSION.md#2-팀원별-실제-기여)

---

## 항목 3 - 이론과 선택 이유

### Q14. `main`을 항상 배포 가능한 상태로 유지하는 이유는 무엇인가?

**1. 상시 배포 가능(Always Deployable)의 정의:**
- 지속적 통합 및 지속적 배포(CI/CD) 환경에서 `main` 브랜치는 언제 어느 순간에도 프로덕션(운영 환경)에 즉시 릴리즈될 수 있도록 모든 테스트를 통과하고 결함이 없는 상태를 유지해야 한다는 원칙이다.

**2. `main` 무결성을 유지해야 하는 3가지 핵심 이유:**
1. **신뢰할 수 있는 개발 기준선 제공 (Stable Base)**:
   - 모든 팀원이 `main`에서 새 기능 브랜치를 분기(branch off)한다. 만약 `main`에 빌드 실패나 버그가 섞여 있다면, 모든 팀원의 로컬 환경이 오염되어 원인 파악이 불가능한 혼란이 발생한다.
2. **즉각적인 긴급 핫픽스 분기 및 배포 (Zero-delay Hotfix)**:
   - 운영 장애 발생 시 최신 `main`에서 지체 없이 핫픽스 브랜치를 따서 패치하고 배포할 수 있다. `main`에 미완성 기능이 섞여 있으면 핫픽스만 분리해 배포하는 것이 불가능해진다.
3. **회귀 추적의 결정적 기준선 (Bisect & Regression Testing)**:
   - 장애나 성능 저하 발생 시 `git bisect`를 통해 원인 커밋을 추적할 때, 모든 머지 커밋이 실행 가능 상태여야 이진 탐색이 정상 작동한다.

**3. 실무 유지 메커니즘:**
- `main` 직접 push 전면 차단, PR 필수화, 자동화 CI 테스트 통과 강제, 피어 리뷰 1인 이상 승인 필수화.

**관련 자료:** [GitHub Flow](README.md#4-실제-github-flow-이해하기), [흐름 다이어그램](diagrams/01_github-flow.html)

### Q15. 직접 push 대신 PR과 승인을 사용하는 이유는 무엇인가?

**1. Pull Request 및 피어 리뷰 메커니즘의 정의:**
- 로컬 변경사항을 중앙 기준선에 바로 붓는 대신, 변경 내역(Diff)을 팀원들에게 투명하게 공개하여 기술적 타당성을 검토받고, 자동화 검증과 동료의 승인(`APPROVED`)을 거친 후 병합하도록 통제하는 협업 프로세스다.

**2. 직접 push 대비 PR/승인의 4대 이점:**
1. **코드 품질 및 결함 조기 예방 (Quality Gate)**:
   - 작성자가 놓치기 쉬운 엣지 케이스, 성능 비효율, 컨벤션 위반을 동료의 객관적인 시각으로 사전 차단한다.
2. **보안 및 책임 분산 (Governance & Audit Trail)**:
   - 코드 제안자(Author)와 승인자(Reviewer)를 분리하여 단독 실수나 악의적인 코드 유입을 원천 방지하고 변경 책임 소재를 명확히 한다.
3. **컨텍스트의 영구 자산화 (Knowledge Preservation)**:
   - 단순한 코드 스니펫뿐만 아니라 "왜 이렇게 설계했는가"에 대한 논의, 피드백, 검증 데이터가 PR 스레드에 영구 기록된다.
4. **팀 지식 공유 및 버스 팩터(Bus Factor) 개선**:
   - 팀원들이 상호 코드를 읽고 리뷰하면서 도메인 지식과 아키텍처 이해도를 공유하여 특정인 부재 시의 리스크를 줄인다.

**3. 저장소 무결성 실천 증빙:**
- 본 저장소의 초기 커밋 이후 모든 통합(19개 PR)은 직접 push 0건, 전원 승인 리뷰 통과 후 병합으로 100% 통제되었다.

**관련 자료:** [Branch Protection 확인 범위](SUBMISSION.md#1-팀과-저장소), [리뷰 규칙](docs/CONTRIBUTING.md#6-코드-리뷰)

### Q16. Issue-PR 연동은 왜 필요한가?

**1. 요구사항-구현 추적성(Traceability)의 정의:**
- 소프트웨어 개발 생애주기에서 문제 제기 및 요구사항 명세(Issue)와 이를 해결하는 코드 구현체(PR)를 상호 참조(Link)하여 변경의 전후 맥락을 투명하게 관리하는 방법론이다.

**2. Issue-PR 연동이 필수적인 3가지 이유:**
1. **히스토리 역추적성 (Root-cause Analysis)**:
   - 몇 달 뒤 특정 코드를 마주쳤을 때 `git blame` → Merge Commit → PR → Issue를 타고 올라가 "어떤 고객 요구사항이나 버그 티켓 때문에 이 코드가 추가되었는지" 비즈니스 배경을 즉시 역추적할 수 있다.
2. **완료 조건(DoD)의 명확한 대조 (Verification)**:
   - Issue에 정의된 완료 조건(Acceptance Criteria)과 PR의 변경 내용을 리뷰어가 1:1로 비교 검증할 수 있다.
3. **워크플로우 자동화 (Lifecycle Automation)**:
   - `Closes #n` 키워드를 사용하면 PR 머지 시점에 해당 이슈가 자동으로 Closed 처리되고 프로젝트 보드의 카드가 Done으로 이동하여 관리 공수를 절감한다.

**3. 실제 프로젝트 교훈:**
- 본 프로젝트의 19개 PR 중 12개는 `Closes #n`으로 완전 자동화되었으나, 일부 PR은 단순 텍스트 언급(#n)에 그쳤다. 이를 통해 "단순 링크"와 "자동 닫힘 키워드"의 실무적 차이를 명확히 체득하고 PR 템플릿 필수 규칙으로 정립했다.

**관련 자료:** [실제 연결 현황](README_answer.md#q3-각-pr이-issue와-연동되어-추적-가능한가), [PR 규칙](docs/CONTRIBUTING.md#5-issue와-pr)

### Q17. push된 commit은 reset보다 revert가 안전한 이유는 무엇인가?

**1. `reset` vs `revert`의 Git 내부 메커니즘 차이:**
- **`git reset` (히스토리 되돌리기 및 삭제)**:
  - 브랜치 포인터(`HEAD`)를 과거 커밋으로 강제 이동시킨다. 되돌려진 커밋들은 그래프에서 고립되며, 원격 저장소에 반영하려면 강제 푸시(`git push --force`)가 필수적이다.
  - **협업 위험성**: 이미 동료들이 pull받은 로컬 히스토리와 원격 히스토리가 불일치(Diverge)하게 되어, 동료가 다음 pull/push 시 극심한 충돌이 나거나 사라진 커밋이 되살아나는 사고가 발생한다.
- **`git revert` (역방향 변경 커밋 추가 및 히스토리 보존)**:
  - 취소할 커밋의 변경사항과 정확히 반대되는 패치(Inverse Diff)를 계산하여 **새로운 커밋(Revert Commit)**을 히스토리 끝에 덧붙인다.
  - 기존 커밋 해시와 히스토리가 1바이트도 훼손되지 않는다.
  - **협업 안전성**: 일반적인 `git push`와 `git pull`만으로 모든 동료에게 충돌 없이 롤백 상태가 자연스럽게 동기화된다.

**2. 실제 프로젝트 적용 사례:**
- 원격 `main`에 잘못 푸시된 임시 파일 커밋(`df3e50c`)을 취소할 때 `reset`을 쓰지 않고 `git revert df3e50c`를 수행하여 역커밋 `7a37beb`를 생성, PR #29를 통해 안전하게 병합했다.

**3. 상황별 선택 원칙:**
- **로컬 개인 브랜치 (원격 미공유)**: `reset --soft` / `reset --mixed` 자유롭게 사용 가능.
- **원격 공유 브랜치 및 `main`**: 예외 없이 **`revert`** 사용이 절대 원칙.

**관련 자료:** [명령 선택표](docs/troubleshooting-log.md#명령-선택표), [복구 시각화](diagrams/03_git-recovery-decision.html)

### Q18. 충돌 마커와 비자명 충돌의 판단 기준은 무엇인가?

**1. 충돌 마커(Conflict Marker)의 구조 및 해석:**
- Git이 삼방향 병합(3-Way Merge) 시 자동으로 양측의 변경사항을 통합하지 못했을 때 파일 내에 남기는 표식이다.
  ```text
  <<<<<<< HEAD
  현재 체크아웃된 브랜치(Base / Target)의 코드 내용
  =======
  병합하려는 브랜치(Incoming)의 코드 내용
  >>>>>>> branch-name
  ```

**2. 자명 충돌 vs 비자명 충돌의 정의:**
- **자명 충돌 (Trivial Conflict)**:
  - 단순 오타 수정, 포맷팅, 또는 완전히 상호 배타적인 값 변경으로 둘 중 더 적절한 한쪽을 선택하면 쉽게 해결되는 충돌.
- **비자명 충돌 (Non-trivial / Semantic Conflict)**:
  - 단순히 한쪽 줄을 고르는 기계적 방식으로는 해결할 수 없으며, 양쪽의 **비즈니스 목적, API 인터페이스 계약, 파일의 정체성, 전체 아키텍처**를 분석하여 양쪽 변경사항을 논리적으로 재조합(Synthesize)하거나 리팩터링해야 하는 복합 충돌.

**3. 비자명 충돌 해결의 4대 판단 기준 및 실제 사례:**
1. **양측 Issue/PR의 요구사항 목적 대조**:
   - `src/main.py`: dave17code(PR #15)의 `reverse_string`과 heeyoung35(PR #14)의 `count_words`는 둘 다 프로젝트 필수 유틸리티이므로, 둘 다 버리지 않고 main 진입점에 나란히 실행되도록 통합 결합했다 (`abe92b8`).
2. **Rename vs Modify 충돌의 정보 유실 방지**:
   - `docs/old-guide.md`: OliverJoo(PR #22)의 파일명 변경(`new-file.md`)과 hyunn9799(PR #24)의 내용 수정을 모두 수용하여, 새 파일 경로에 수정 본문을 온전히 반영했다 (`9315e23`, `fee0b98`).
3. **충돌 마커 완전 제거 및 코드 스타일 정리**:
   - 마커 잔재(`<<<<<<<`, `=======`, `>>>>>>>`)를 100% 제거하고 문법 무결성 확보.
4. **로컬 실행 및 단위 테스트 검증**:
   - 수정 후 바로 커밋하지 않고 `python3 src/main.py` 및 테스트를 직접 구동하여 런타임 오류가 없음을 증명한 후 커밋.

**관련 자료:** [충돌 기록](docs/conflict-resolution.md), [충돌 해결도](diagrams/02_conflict-resolution.html)

---

## 항목 4 - 상황 판단과 심층 이해

Q19~Q21은 원격 저장소에서 실제로 수행된 사건을 보고하는 항목이 아니라, 확인된 팀 규칙과 Git 원리를 적용한 **가상 시나리오 답변**이다.

### Q19. 긴급 hotfix는 어떤 순서로 처리하는가?

**1. (긴급) 핫픽스(Hotfix)의 정의:**
- **개념:** 이미 프로덕션(운영 환경)에 배포된 최신 버전(`main`)에서 발견된 **치명적인 결함(Critical Bug), 보안 취약점(Vulnerability), 서비스 중단 및 데이터 유실 위험**을 해결하기 위해 정기 릴리즈 주기를 거치지 않고 즉각적으로 적용하는 긴급 패치 작업이다.
- **특징:** 진행 중인 다른 미완성 기능(In-progress Features)과 절대 섞이지 않아야 하므로, 배포 기준선(`main` 또는 배포 Tag)에서 직접 격리된 브랜치를 생성하여 **문제 원인에만 집중해 최소 범위(Minimal Change)로 수정**한 뒤 신속히 배포·동기화한다.

**2. 핫픽스 처리 순서 (가상 시나리오 7단계 대응 워크플로우):**

1. **긴급 이슈 등록 및 범위 한정**:
   - 장애 현상, 재현 경로, 영향도를 명시한 긴급 Issue를 등록한다 (`hotfix` 라벨 부여).
2. **최신 배포 기준선(`main`)에서 핫픽스 브랜치 분기**:
   - 진행 중인 기능 브랜치가 아니라 최신 `main`으로 이동(`git switch main && git pull`)한 뒤 `fix/<이슈-내용>` 브랜치를 생성한다.
3. **최소 변경 원칙의 원인 수정**:
   - 다른 코드 리팩터링이나 불필요한 기능 추가를 철저히 배제하고, 버그의 근본 원인만을 타겟팅하여 diff를 최소화한다.
4. **결정적 테스트 작성 및 로컬 검증**:
   - 버그 재현 테스트 케이스를 작성해 수정을 검증하고, 전체 단위 테스트를 실행해 사이드 이펙트(회귀 결함)가 없음을 확인한다.
5. **핫픽스 PR 생성 및 신속 동료 리뷰 (Fast-track Review)**:
   - 아무리 긴급하더라도 `main` 직접 push를 금지하고 PR을 생성한다. 변경 범위가 작기 때문에 동료의 즉각적인 검토와 승인(`APPROVED`)을 받아 Branch Protection 규칙을 통과한다.
6. **`main` 병합 및 프로덕션 긴급 배포**:
   - 승인된 PR을 `main`에 병합(Squash/Merge)하고 새 패치 버전 태그(예: `v1.0.1`)를 발행하여 즉시 운영 환경에 배포한다.
7. **배포 모니터링 및 개발 브랜치 동기화**:
   - 실시간 메트릭/로그를 모니터링하여 정상화를 확인하고, 이상 시 즉시 `revert`할 준비를 갖춘다. 동시에 다른 팀원들의 진행 중인 feature 브랜치에도 최신 `main`을 rebase/merge하도록 공지하여 동일 버그가 재유입되는 것을 방지한다.

```bash
cd "$UPSTREAM_CLONE"
git switch main
git pull --ff-only origin main
git switch -c fix/heeyoung35-count-empty-input
# 최소 범위 수정 및 테스트 실행
git add src/count_utils.py tests/test_team_utils.py
git commit -m "fix: handle empty input in count_words"
git push -u origin fix/heeyoung35-count-empty-input
# PR 생성 후 긴급 동료 승인 획득 -> main 병합
```

> **핵심 원칙:** "긴급하다"는 이유로 코드 리뷰나 테스트를 생략하면 2차·3차의 더 큰 장애로 이어질 수 있다. 절차를 간소화하되 GitHub Flow의 안전 계약(PR, 리뷰, 자동화 검증)은 온전히 지키는 것이 핫픽스의 본질이다.

**관련 자료:** [GitHub Flow](diagrams/01_github-flow.html), [PR 규칙](docs/CONTRIBUTING.md#5-issue와-pr), [복구 시각화](diagrams/03_git-recovery-decision.html)

### Q20. 의미 없는 commit 메시지를 이미 push했다면 어떻게 개선하는가?

**답변(가상 시나리오):** 이미 push된 커밋의 히스토리를 재작성하는 것은 협업에 큰 영향을 미치므로, **[1. 브랜치 공유 범위 확인 → 2. 대화형 rebase(reword/squash) 실행 → 3. --force-with-lease 안전 푸시]**의 절차를 따른다.

**1. 공유 범위 및 상태 확인 (최우선 판단):**
- **개인 Feature 브랜치 (단독 작업)**: 아직 다른 팀원이 pull하지 않은 브랜치라면 `git rebase -i`로 깔끔하게 정리한 뒤 푸시해도 안전하다.
- **공동 작업 브랜치 / 리뷰 진행 중인 PR**: 히스토리를 강제로 바꾸면 동료의 로컬 브랜치와 분기(diverge)되어 혼란을 초래하므로, 히스토리를 재작성하지 않고 PR 본문(What/Why/How)에 상세 설명을 보강하거나 후속 커밋으로 의도를 설명한다.
- **`main` 브랜치**: 이미 병합된 공유 기준선은 메시지 정리만을 위해 절대 히스토리를 재작성하지 않는다.

**2. Interactive Rebase의 핵심 명령어 의미 (`reword` vs `squash`):**
- **`reword` (약어: `r`)**:
  - **의미**: 커밋 내용(diff)은 그대로 유지하고, **커밋 메시지만 다시 작성**한다.
  - **용도**: "수정", "fix", 오타 등 의미 없는 메시지를 컨벤션(예: `feat:`, `fix:`)에 맞는 명확한 설명으로 변경할 때 사용한다.
- **`squash` (약어: `s`)**:
  - **의미**: 해당 커밋을 **이전(직전) 커밋과 하나로 합치면서, 두 커밋의 메시지를 함께 결합·편집**한다.
  - **용도**: 자잘한 "WIP", "오타 수정" 커밋들을 하나의 완성된 논리적 커밋 단위로 병합할 때 사용한다. (메시지를 남기지 않고 합칠 때는 `fixup` / `f`를 사용)

**3. 대화형 Rebase 및 옵션 사용 절차:**

1. **대화형 리베이스 실행**:
   ```bash
   git rebase -i HEAD~3   # 최근 3개 커밋을 대상으로 에디터 실행
   ```
2. **명령 키워드 설정 (에디터 내 편집)**:
   ```text
   pick   a1b2c3d feat: add reverse_string function
   reword e4f5g6h fix typo                     # -> 커밋 메시지만 수정
   squash 7i8j9k0 add missing test case        # -> 윗 커밋과 하나로 합침
   ```
3. **메시지 편집 및 테스트 검증**:
   - `reword` 대상의 메시지 편집 창이 뜨면 의미 있는 메시지로 교체한다.
   - `squash` 대상의 메시지 편집 창이 뜨면 두 커밋의 변경사항을 포괄하는 단일 메시지로 정돈한다.
   - 리베이스 완료 후 단위 테스트를 실행해 코드 동작이 온전한지 검증한다.
4. **`--force-with-lease` 옵션으로 안전한 원격 반영**:
   ```bash
   git push --force-with-lease origin feature/my-branch
   ```
   - **`--force-with-lease` 옵션을 사용하는 이유**: 무조건 원격을 덮어쓰는 단순 `--force`와 달리, 로컬이 인지하고 있는 원격 ref와 실제 원격 저장소의 최신 커밋이 일치할 때만 덮어쓰기를 허용한다. 따라서 내가 작업하는 사이에 동료가 새로 푸시한 커밋이 있다면 푸시가 거부되어 작업 유실을 방지하는 안전장치다.

**관련 자료:** [커밋 규칙](docs/CONTRIBUTING.md#4-커밋-메시지), [안전 규칙](docs/CONTRIBUTING.md#8-안전-규칙), [복구 의사결정](diagrams/03_git-recovery-decision.html)

### Q21. 같은 파일·영역에서 충돌이 반복되면 어떻게 예방하는가?

**답변(가상 시나리오 예방안):** 반복되는 충돌은 단순한 Git 조작 실수가 아니라 **코드 아키텍처와 협업 프로세스의 결함 신호**다. 저장소 이력상 여러 기능이 모인 `src/main.py`와 파일명 변경/수정이 겹친 `docs/old-guide.md`에서 확인된 충돌 패턴을 바탕으로, 재발을 방지하는 5대 예방 전략을 수립했다.

**1. 충돌 반복의 근본 원인 분석:**
- **진입점 비대화 (God File)**: 모든 모듈의 import와 실행이 `main.py` 한 파일에 집중되어 동시 수정이 필연적으로 발생.
- **장수 브랜치 (Long-lived Branch)**: 메인 브랜치와 오랫동안 동기화되지 않고 독립 개발이 길어짐.
- **구조 변경과 내용 수정의 혼재**: 디렉터리/파일명 변경(Rename)과 본문 수정(Modify)을 한 PR에 섞어 제출.

**2. 5대 사전 예방 아키텍처 및 프로세스:**
1. **진입점 모듈화 및 플러그인 레지스트리 패턴 (Architecture)**:
   - `main.py`에 함수를 일일이 하드코딩하지 않고, `modules/` 디렉터리에 각 기능을 독립 등록하여 진입점 파일 수정 빈도를 원천 차단한다.
2. **자주 main 동기화 (Daily Rebase/Merge)**:
   - 피처 브랜치 작업 중 매일 아침 `git switch main && git pull --ff-only` 후 작업 브랜치로 돌아와 최신 변경사항을 미리 흡수한다.
3. **Rename과 Modify PR의 엄격한 분리 (Separation of PRs)**:
   - 파일 이동/이름 변경 PR을 먼저 단독으로 병합한 뒤, 그 다음 PR에서 내용 수정을 진행하여 비자명 충돌을 구조적으로 방지한다.
4. **작업 범위 사전 공유 및 이슈 선점 (Communication)**:
   - 공용 파일을 수정해야 하는 경우 Issue에 작업 예정 파일과 범위를 명시하고 팀 채널에 사전 공지하여 병행 작업을 피한다.
5. **코드 소유권 지정 (`CODEOWNERS`)**:
   - 공용 진입점 파일에 전담 리뷰어를 지정하여 무분별한 동시 병합을 거버넌스로 통제한다.

**관련 자료:** [이력 기반 충돌 기록과 예방책](docs/conflict-resolution.md), [팀 역할](docs/CONTRIBUTING.md#1-팀-역할)

### Q22. rebase의 장점·위험과 안전 수칙은 무엇인가?

**답변(보너스 개념 분석):** 원격 저장소에는 rebase 전후 비교 문서나 관련 PR이 없어 **보너스 수행 증빙은 확인되지 않는다.** 개념적으로 `rebase`는 히스토리를 정돈하는 강력한 도구이지만, 공개 브랜치에서 오용 시 치명적인 결함을 유발한다.

**1. Rebase의 내부 동작 원리 및 장점 (Pros):**
- **동작 원리**: 기존 커밋들의 베이스(부모)를 타겟 브랜치의 최신 커밋으로 변경하여 패치를 순차적으로 재적용(Replay)한다.
- **장점**:
  - 불필요한 머지 커밋(Merge bubble)을 제거하고 깔끔한 일자형 선형 히스토리(Linear History)를 유지한다.
  - `git rebase -i`를 통해 커밋 메시지 변경(`reword`), 자잘한 WIP 커밋 통합(`squash`)으로 가독성 높은 PR을 구성할 수 있다.

**2. 치명적인 위험성 (The Golden Rule of Rebase 위반 시):**
- 부모 커밋이 바뀌므로 내용이 같아도 **완전히 새로운 커밋 해시(New Hash)**가 생성된다.
- 이미 원격에 공유된 브랜치에서 rebase를 실행하고 강제 푸시(`--force`)하면, 동료의 로컬 히스토리와 부모-자식 관계가 완전히 틀어져 작업이 소실되거나 동료가 pull할 때 중복 커밋과 극심한 충돌이 발생한다.

**3. 4대 안전 수칙 (Safety Rules):**
1. **공유 브랜치 절대 금지 (Never Rebase Public Branches)**:
   - `main` 브랜치나 동료와 함께 쓰는 공유 브랜치에서는 절대 rebase를 수행하지 않는다. 오직 로컬 개인 피처 브랜치에서만 사용한다.
2. **사전 백업 브랜치 생성**:
   - Rebase 전 반드시 `git branch backup-my-work`로 안전망을 확보한다.
3. **단위 테스트 재실행**:
   - 커밋이 재적용되는 과정에서 논리적 충돌(Semantic Conflict)이 없는지 빌드와 테스트를 재검증한다.
4. **`--force-with-lease` 필수 사용**:
   - 원격 반영 시 무조건 덮어쓰는 `--force` 대신, 타인의 커밋 덮어쓰기를 방지하는 lease 옵션을 강제한다.

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
