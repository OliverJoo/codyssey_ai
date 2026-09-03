# 4인 팀 협업 규칙

이 문서는 실제 `b2-2-git-conflict-craft` 저장소에서 사용한 GitHub Flow를 네 GitHub 계정 기준으로 정리하고, 실제 이력에서 발견한 보완점을 포함한다.

> **표기 범례:** **[사실]**은 원격 객체/API로 확인한 내용, **[재구성]**은 증거를 해석한 설명, **[추가 예시]**는 실제 이력에 없는 학습용 권장안이다.

> **실행 위치 경고:** 이 학습자료 폴더는 원격 저장소의 독립 clone이 아닐 수 있다. 아래 Git 명령은 반드시 `dave17code/b2-2-git-conflict-craft`를 별도로 clone한 `UPSTREAM_CLONE`에서만 실행한다. 학습자료 폴더에서 bare `git switch`, `git pull`, `git reset`을 실행하지 않는다.

## 1. 팀 역할

| 팀원 | 주 담당 코드 | 협업 역할 |
|---|---|---|
| dave17code | `src/string_utils.py` | 저장소 초기화, 협업 규칙, 문자열 기능 |
| heeyoung35 | `src/count_utils.py`, `src/main.py` | 프로젝트 설명, 실행 진입점 통합 |
| OliverJoo | `src/list_utils.py` | 리스트 기능, rename 충돌 브랜치 |
| hyunn9799 | `src/math_utils.py` | 수학 기능, modify 충돌·제출 문서 |

## 2. GitHub Flow

- `main`은 항상 실행 가능한 통합 기준으로 유지한다.
- 작업 전 Issue를 만들고 기능·문서별 `feature/*` 브랜치를 만든다.
- Pull Request에서 테스트와 타인 리뷰를 마친 뒤 `main`에 병합한다.
- 병합된 작업 브랜치는 삭제하고 다음 작업은 최신 `main`에서 시작한다.

선택 이유는 다음과 같다.

1. 브랜치 종류가 단순해 4명의 작업 위치를 쉽게 알 수 있다.
2. 짧은 feature 브랜치와 작은 PR은 충돌 범위를 줄인다.
3. Issue·PR·리뷰·merge commit이 한 흐름으로 남아 제출 증빙에 유리하다.

## 3. 브랜치 이름

**[추가 예시]** 이후 작업의 권장 형식은 `feature/<github-account>-<작업명>`이다.

```text
feature/dave17code-string-utils
feature/heeyoung35-count-utils
feature/OliverJoo-rename-guide
feature/hyunn9799-update-guide
```

**[사실]** 실제 브랜치에는 `feature/kim-*`, `feature/kang-*`, `feature/joo-*`, `feature/kwon-*`가 쓰였고 PR #4에는 `geature/kang-count-utils` 오타가 남아 있다. 역사적 브랜치명과 커밋 제목은 실제 값 그대로 인용하고, 새 예시에서만 GitHub 계정과 올바른 `feature` 철자를 쓴다.

작업 시작:

```bash
UPSTREAM_CLONE="/absolute/path/to/b2-2-git-conflict-craft"
git -C "$UPSTREAM_CLONE" switch main
git -C "$UPSTREAM_CLONE" pull --ff-only origin main
git -C "$UPSTREAM_CLONE" switch -c feature/dave17code-string-utils
```

## 4. 커밋 메시지

형식은 `<type>: <구체적인 변경>`이다.

- `feat`: 기능 추가
- `fix`: 오류 또는 충돌 해결
- `docs`: 문서 변경
- `refactor`: 동작을 유지한 개선
- `test`: 테스트 추가·수정
- `chore`: 설정·정리

실제 좋은 예:

```text
feat: add remove_duplicates utility function
refactor: apply strip to handle leading and trailing spaces
docs: clarify order non-preservation in remove_duplicates docstring
fix: resolve conflict in main.py by combining Kim and Kang outputs
```

과거 브랜치명·커밋 제목에 들어간 식별자는 역사적 증빙이므로 그대로 두지만, 새 문서와 설명에서는 `dave17code`~`hyunn9799`를 사용한다. `update`, `temp`, `wip`, `final`처럼 대상과 결과를 알 수 없는 메시지는 금지한다.

## 5. Issue와 PR

PR 본문에는 네 항목을 넣는다.

```markdown
## 연결 이슈
- Closes #이슈번호

## 변경 사항 (What)
- 바뀐 파일과 동작

## 변경 이유 (Why)
- 해결하려는 문제

## 테스트/검증 (How)
- 실행 명령과 확인 결과
```

실제 PR #2, #4, #7, #8, #11, #14, #16, #22, #24, #26, #29, #30에서는 closing keyword가 확인된다. PR #15, #17, #18, #19, #20, #31, #32는 관련 Issue만 적거나 closing link를 누락했다. 이후 PR은 반드시 `Closes #n`을 사용해 모든 PR이 추적되도록 한다.

## 6. 코드 리뷰

- 자기 PR은 자신이 승인하지 않는다.
- 각 팀원은 타인 PR을 최소 2건 승인한다.
- `LGTM`만 남기지 않고 대상·관찰·위험·제안 중 둘 이상을 적는다.
- 작성자는 반영 커밋과 답글을 남긴다.
- 변경 후 리뷰어가 재확인하고 승인한다.

**[사실]** 승인 횟수는 dave17code 4건, heeyoung35 2건, OliverJoo 7건, hyunn9799 6건이며 병합 PR 19개 모두 `APPROVED` 리뷰가 있다. 그러나 승인 여부와 실질 피드백은 다르다. 내용 있는 실질 리뷰는 #2, #4, #7, #8, #24의 **5/19건**만 확인되어 전체 리뷰 품질 요구는 충족하지 못했다. 기능 PR의 확인 가능한 피드백 반영은 다음과 같다.

| 작성자 | PR | 피드백 반영 커밋 |
|---|---|---|
| dave17code | #2 `reverse_string` | `5e171a9` 타입 검사·docstring |
| heeyoung35 | #4 `count_words` | `e47ac39` 앞뒤 공백 처리 |
| OliverJoo | #7 `remove_duplicates` | `db5ae1a` 순서 비보장 명시 |
| hyunn9799 | #8 `is_even` | `38ab44f` 0·음수 설명 |

## 7. 충돌 대응

1. 충돌한 브랜치·파일·관련 PR을 팀에 공유한다.
2. `git status`와 양쪽 커밋을 확인한다.
3. 두 작성자가 무엇을 보존할지 합의한다.
4. 파일을 편집하고 충돌 마커를 모두 제거한다.
5. `git add` 후 실행·테스트한다.
6. 해결 커밋을 만들고 [conflict-resolution.md](conflict-resolution.md)에 기록한다.

**[사실]** `main.py` 충돌에서는 dave17code와 heeyoung35의 출력을 모두 보존했다. 반면 `old-guide.md` rename/modify 이력은 `9315e23`에서 Git이 수정 내용을 `new-file.md`로 자동 병합했다. 후속 `fee0b98`은 마침표 1자를 바꿨으므로 실제 충돌 발생과 수동 해결을 입증하지 않는다. 따라서 비자명 충돌 요구는 현재 증거로 미확인이다.

## 8. 안전 규칙

- 공유된 `main`에서는 합의 없이 `reset`, rebase, force push를 하지 않는다.
- push한 잘못된 변경은 `revert`로 되돌린다.
- 로컬 최근 커밋에만 `amend`와 `reset --soft`를 사용한다.
- 강제 push가 정말 필요하면 팀에 먼저 알리고 `--force-with-lease`를 사용한다.
- Branch API에서 `main protected: true`는 확인됐다. required approval 수·직접 push 차단·force push 제한 같은 세부값은 설정 화면을 캡처해 보강한다.

## 9. 완료 기준

- 실행 결과가 요구사항과 일치한다.
- What/Why/How와 `Closes #n`이 있다.
- 작성자 외 팀원이 실질 리뷰를 남겼다.
- 리뷰 반영 커밋과 답글이 연결된다.
- 충돌 또는 복구가 있었다면 재현 가능한 로그를 남겼다.
- [SUBMISSION.md](../SUBMISSION.md)에 PR·리뷰·해시를 연결했다.

현재 원격 이력은 승인 횟수 조건은 충족하지만 실질 리뷰는 5/19건이고, 실제 충돌은 한 건만 입증된다. 위 완료 기준을 프로젝트 전체가 이미 충족했다는 의미로 읽지 않는다.
