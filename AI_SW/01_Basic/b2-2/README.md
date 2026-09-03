# b2-2 - 4인 GitHub Flow 협업 실습

이 자료는 실제 저장소 `b2-2-git-conflict-craft`의 코드와 Git 이력을 바탕으로, 엔트리 레벨 개발자가 **Issue → 브랜치 → 커밋 → PR → 리뷰 → 충돌 해결 → 복구 → 제출** 흐름을 이해하도록 정리한 학습·제출 안내서다.

> **출처 경계:** 실제 협업 작업은 [원격 저장소](https://github.com/dave17code/b2-2-git-conflict-craft)에 있다. 이 폴더는 독립 clone이 아니라 제출 패키지다. `src/`와 충돌 결과 파일은 원격 `daecf53`의 원본 스냅샷이고, `examples/`, `tests/`, 실행 스크립트, 답변과 다이어그램은 별도 추가 자료다. 자세한 구분은 [코드 출처 문서](docs/source-provenance.md)를 따른다.

팀은 총 4명이며 실제 GitHub 계정 `dave17code`, `heeyoung35`, `OliverJoo`, `hyunn9799`로 표기한다. 2026-09-03 기준 원격 `main`(`daecf53`)과 GitHub API를 교차 확인했다. 병합 PR 19개는 모두 승인 후 병합되었고 현재 열린 PR은 없다. 세부 Branch Protection 값처럼 현재 권한으로 조회되지 않는 항목은 별도 증빙이 필요한 것으로 표시한다.

## 먼저 볼 자료

1. [GitHub Flow 다이어그램](diagrams/01-github-flow.svg) ([확대형 HTML](diagrams/01_github-flow.html), [편집본](diagrams/01-github-flow.excalidraw))
2. [충돌 해결 다이어그램](diagrams/02-conflict-resolution.svg) ([확대형 HTML](diagrams/02_conflict-resolution.html), [편집본](diagrams/02-conflict-resolution.excalidraw))
3. [Git 복구 의사결정 다이어그램](diagrams/03-git-recovery-decision.svg) ([확대형 HTML](diagrams/03_git-recovery-decision.html), [편집본](diagrams/03-git-recovery-decision.excalidraw))
4. [평가 질문 22개와 답변](README_answer.md)
5. [스크롤형 발표 페이지](README_answer.html)
6. [실제 이력 기반 제출 인덱스](SUBMISSION.md)
7. [최신 원격 변경 전수 감사](docs/remote-change-audit.md)
8. [원격 원본과 추가 자료의 경계](docs/source-provenance.md)
9. [PDF·질문 요구사항 추적표](docs/requirements-traceability.md)

다이어그램은 설치된 gstack `diagram` 워크플로로 `.mmd`·`.excalidraw`·`.svg`·`.png`를 생성했다. 기존 HTML 뷰어는 50%·100%·150%·200% 확대/축소와 화면 맞춤을 제공한다.

## 1. 실제 프로젝트 요약

### 1.1 팀과 역할

| GitHub 계정 | 실제 결과물 | 핵심 병합 PR | 복구 실습 담당 |
|---|---|---|---|
| dave17code | `reverse_string`, 협업 가이드, 최종 문서·캐시·복구 기록 | #2, #11, #15, #30, #31, #32 | `commit --amend` |
| heeyoung35 | `count_words`, README와 `main.py` 통합 | #4, #14 | `reset --soft` |
| OliverJoo | `remove_duplicates`, 비자명 충돌·실제 revert | #7, #16, #17, #19, #22, #29 | `revert` |
| hyunn9799 | `is_even`, 파일 수정·충돌 해결·제출 문서 | #8, #18, #20, #24, #26 | `stash` / `stash pop` |

> 위 PR 번호는 최신 원격 merge commit과 GitHub API로 교차 확인했다. 타인 PR 승인 수는 dave17code 4건, heeyoung35 2건, OliverJoo 7건, hyunn9799 6건이다. PR #32는 OliverJoo의 승인을 받은 뒤 merge commit `daecf53`으로 `main`에 반영됐다.

### 1.2 원격 원본 코드와 추가 예제

| 파일 | 함수 | 동작 | 주요 커밋 |
|---|---|---|---|
| [src/string_utils.py](src/string_utils.py) | `reverse_string(text)` | 문자열 역순 반환, 문자열이 아니면 `TypeError` | `af55b1e`, `5e171a9` |
| [src/count_utils.py](src/count_utils.py) | `count_words(text)` | 앞뒤 공백 제거 후 공백 기준 단어 수 반환 | `8f78474`, `e47ac39` |
| [src/list_utils.py](src/list_utils.py) | `remove_duplicates(items)` | `set`을 이용해 중복 제거, 순서 보장 안 함 | `13c490b`, `db5ae1a` |
| [src/math_utils.py](src/math_utils.py) | `is_even(number)` | 0·음수를 포함한 짝수 판별 | `2d9a7fe`, `38ab44f` |
| [src/main.py](src/main.py) | 원격 실행 진입점 | 원격 그대로 `reverse_string`과 `count_words` 실행 | `4241fdc`, `e7917b1`, `abe92b8` |

`src/`는 원격 `daecf53`와 byte-for-byte 동일하다. 네 팀원의 함수를 한 번에 실행하는 코드는 원격 원본을 고치지 않고 [examples/team_utils_demo.py](examples/team_utils_demo.py)로 분리했다.

```bash
python3 src/main.py
python3 examples/team_utils_demo.py
python3 -c 'from src.list_utils import remove_duplicates; print(remove_duplicates([1, 1, 2, 3]))'
python3 -c 'from src.math_utils import is_even; print(is_even(-2), is_even(3))'
```

## 2. 학습·제출 패키지 구조

```text
b2-2/
├── README.md
├── README_answer.md
├── README_answer.html
├── SUBMISSION.md
├── src/
│   ├── main.py
│   ├── string_utils.py
│   ├── count_utils.py
│   ├── list_utils.py
│   └── math_utils.py
├── examples/
│   └── team_utils_demo.py
├── docs/
│   ├── CONTRIBUTING.md
│   ├── conflict-resolution.md
│   ├── troubleshooting-log.md
│   ├── git-history-evidence.md
│   ├── remote-change-audit.md
│   ├── source-provenance.md
│   ├── requirements-traceability.md
│   ├── git-log.txt
│   ├── new_guide.md
│   └── new-file.md
├── diagrams/
│   ├── 01_github-flow.html
│   ├── 02_conflict-resolution.html
│   └── 03_git-recovery-decision.html
├── 01_setup.sh
├── 02_demo.sh
├── 03_test.sh
├── 04_verify.sh
└── 05_verify_upstream.sh
```

## 3. 환경 설정과 실행

### 3.1 공통 준비

- Git 2.30 이상
- Python 3.10 이상
- GitHub 계정
- 저장소 설정을 확인할 관리자 권한

```bash
git --version
python3 --version
```

사용자 이름과 이메일 설정이 필요하다면 실제 원격 clone을 만든 뒤 해당 clone에만 적용한다. `--global` 설정은 이 실습 자료가 임의로 바꾸지 않는다.

```bash
UPSTREAM_CLONE="/absolute/path/to/b2-2-git-conflict-craft"
git -C "$UPSTREAM_CLONE" config user.name "본인 이름"
git -C "$UPSTREAM_CLONE" config user.email "GitHub 이메일"
```

### 3.2 실행 순서

```bash
bash 01_setup.sh
bash 02_demo.sh
bash 03_test.sh
bash 04_verify.sh
# 네트워크 연결 시 원격 commit과 스냅샷까지 재검증
bash 05_verify_upstream.sh
```

원격 원본과 추가 예제를 빠르게 확인하려면 다음 명령을 사용한다.

```bash
python3 src/main.py
python3 examples/team_utils_demo.py
bash 05_verify_upstream.sh
```

## 4. 실제 GitHub Flow 이해하기

### 4.1 브랜치는 작업 복사본이 아니라 커밋 포인터다

`main`은 팀의 통합 기준이고, 기능 브랜치는 특정 작업의 커밋을 가리키는 이동 가능한 포인터다. 실제 저장소도 계정별 작업 브랜치를 사용했다. 이 문서는 실제 GitHub 계정을 그대로 사용하며, 과거 이력에 남은 `geature` 오타는 새 작업에서 `feature`로 바로잡는다.

```bash
git clone https://github.com/dave17code/b2-2-git-conflict-craft.git
cd b2-2-git-conflict-craft
git switch main
git pull --ff-only origin main
git switch -c feature/dave17code-string-utils
```

### 4.2 Issue와 PR의 역할

Issue는 문제와 완료 조건을 합의하는 곳이고, PR은 구현 결과를 검토하는 곳이다. PR 본문에는 다음을 남긴다.

```markdown
## 연결 이슈
- Closes #이슈번호

## What
- reverse_string 함수를 추가했습니다.

## Why
- 문자열 처리 유틸리티가 필요합니다.

## How
- python3 src/main.py
- 문자열·비문자열 입력을 확인했습니다.
```

별도 원격 clone의 merge commit은 실제 PR 번호를 증명하지만 `Closes #n` 본문은 포함하지 않는다. 따라서 Issue 연동 평가는 GitHub PR 화면을 추가로 확인해야 한다.

### 4.3 좋은 리뷰

`LGTM`만으로는 어떤 위험을 확인했는지 알 수 없다. 실제 `reverse_string` 후속 커밋 `5e171a9`는 타입 검사와 docstring 예시를 추가했고, `count_words` 후속 커밋 `e47ac39`는 앞뒤 공백 처리용 `strip()`을 추가했다. 팀원별 승인 2건 이상과 네 핵심 기능 PR의 피드백 반영은 확인했다. 하지만 구체적 텍스트 피드백이 확인되는 PR은 19개 중 5개뿐이므로 “모든 PR에 실질 코멘트” 요구는 미충족이다. review URL과 반영 hash는 [SUBMISSION.md](SUBMISSION.md)에 연결했다.

좋은 리뷰 예시는 다음처럼 대상·관찰·위험·제안을 포함한다.

```text
string_utils.py에서 문자열 이외 입력의 동작이 정의되지 않았습니다.
TypeError를 명시적으로 발생시키고 docstring에 예시를 추가하면
호출자가 계약을 이해하기 쉬울 것 같습니다.
```

## 5. 충돌·병합 이력 재검증

자세한 재현과 판단은 [충돌 해결 기록](docs/conflict-resolution.md)에서 확인한다.

### 5.1 같은 영역 충돌: `src/main.py`

- dave17code PR #15: `reverse_string` import와 출력 추가
- heeyoung35 PR #14: `count_words` import와 출력 추가
- 해결 merge commit: `abe92b8`
- 판단: 두 기능이 모두 필요하므로 import와 출력 줄을 모두 보존

최종 코드는 두 함수의 결과를 함께 출력한다. Git이 자동으로 결정할 수 없는 동일 영역의 의도를 사람이 결합한 사례다.

### 5.2 이름 변경 대 내용 수정 시나리오: `docs/old-guide.md`

- OliverJoo PR #22: `old-guide.md`를 `new-file.md`로 변경 (`99ef129`)
- hyunn9799 작업: 같은 원본 파일 내용을 수정 (`2579e64`, `1b1ec20`)
- 통합 merge commit: `9315e23`
- 후속 commit: `fee0b98`은 마지막 문장 부호 1줄 수정
- 부모 replay: `1b1ec20`에서 `e660623`을 병합하면 `Automatic merge went well`, 결과는 `R100 old-guide.md → new-file.md`

rename/modify를 의도한 비자명 병합 시나리오는 맞지만, 현재 보존된 부모로 재실행하면 Git이 자동 병합한다. 당시 conflict marker나 unmerged 상태 증거도 없다. 따라서 이 사례를 두 번째 “실제 충돌 해결”로 확정하지 않으며, 과제의 충돌 2회·비자명 충돌 1회 조건은 **미확인/보완 필요**로 판정한다. `02_demo.sh`의 modify/delete 충돌은 개념 이해를 위한 별도 합성 예제다.

## 6. 복구 명령 네 가지

| 상황 | 명령 | 실제 기록상 담당 | 주의점 |
|---|---|---|---|
| 최근 로컬 커밋 보완 | `git commit --amend` | dave17code | push 전 사용 |
| 커밋 취소, 변경은 staged로 유지 | `git reset --soft HEAD~1` | heeyoung35 | 공유 이력에 사용 금지 |
| 공유된 변경을 새 커밋으로 취소 | `git revert <hash>` | OliverJoo | 협업 브랜치에 안전 |
| 미완성 작업 임시 보관 | `git stash` / `git stash pop` | hyunn9799 | 장기 백업 용도 아님 |

원천 프로젝트의 `docs/troubleshooting-log.md`에는 위 분담과 절차가 기록되어 있다. OliverJoo의 revert는 PR #29에서 원본 `df3e50c`와 취소 `7a37beb`이 모두 보존되어 강하게 증명된다. dave17code의 amend와 hyunn9799의 stash/pop은 관련 PR 본문에서 확인된다. heeyoung35의 reset soft는 원천 문서 기록만 확인되며, 명령 특성상 사라진 커밋을 일반 graph만으로 입증할 수 없으므로 당시 `git status`나 reflog 화면을 추가하는 것이 좋다.

## 7. 제출 증빙의 사실 수준

| 항목 | 로컬에서 확인 | 추가 증빙 |
|---|---|---|
| 4인별 코드 기여 | 커밋 작성자와 파일 이력 | 없음 |
| 병합 PR 번호 | merge commit 제목 | PR 페이지 URL 권장 |
| 충돌 해결 결과 | `abe92b8` 한 건은 확인 | 둘째 사례는 자동 병합 replay이므로 별도 실제 충돌 증빙 필요 |
| 리뷰 횟수·핵심 기능 반영 | 인당 승인 2회 이상과 기능 PR 4건 반영 확인 | 모든 PR 실질 코멘트는 5/19만 확인되어 미충족 |
| Issue와 `Closes #n` | GitHub PR 본문으로 확인 | 일부 PR 누락은 보완 필요 |
| Branch Protection | `main protected: true` 확인 | 승인 수·직접 push 차단 등 세부 설정 화면 권장 |
| 복구 명령 실행 | revert는 실제 두 commit, amend·stash는 PR 본문 | reset은 터미널·reflog 증빙 권장 |

실제 해시와 PR별 기여는 [SUBMISSION.md](SUBMISSION.md)에 정리했다.

## 8. 제출 전 체크리스트

- [x] 총 4명을 실제 GitHub 계정으로 일관되게 표기했다.
- [x] 실제 네 유틸 함수와 `main.py`를 설명했다.
- [x] 별도 원격 clone의 merge commit에서 실제 PR 번호를 확인했다.
- [x] 같은 영역 충돌 1건과 rename/modify 자동 병합 replay 결과를 구분했다.
- [ ] 두 번째 실제 충돌 및 비자명 충돌의 conflict 상태 증빙을 보강한다.
- [x] 필수 문서와 확대 가능한 다이어그램을 연결했다.
- [x] 팀원별 리뷰 2회 이상과 핵심 기능 피드백 반영 1회의 URL을 첨부했다.
- [ ] 모든 PR에 실질 코멘트와 reviewer-author 상호작용을 보강한다(현재 명시적 텍스트 근거 5/19).
- [x] 각 PR의 Issue 연결 상태를 확인하고 누락 PR을 구분했다.
- [x] `main`의 protected 상태를 API로 확인했다.
- [ ] 필수 승인 수·직접 push 차단 등 세부 보호 설정 화면을 첨부한다.
- [x] revert 원본·취소 commit과 PR #29를 연결했다.
- [ ] reset soft 실습 당시 `git status` 또는 reflog 증빙을 보강한다.
- [x] PR #32의 승인·병합과 최신 `main` commit `daecf53`을 반영했다.
- [x] `src/`, `docs/new-file.md`, `docs/new_guide.md`, `docs/git-log.txt`를 원격 원본과 동일하게 보존했다.

## 9. 관련 문서

- [평가 질문과 답변](README_answer.md)
- [제출 인덱스](SUBMISSION.md)
- [협업 규칙](docs/CONTRIBUTING.md)
- [충돌 해결 기록](docs/conflict-resolution.md)
- [트러블슈팅 기록](docs/troubleshooting-log.md)
- [Git 이력 증빙](docs/git-history-evidence.md)
- [최신 원격 변경 전수 감사](docs/remote-change-audit.md)
- [원격 원본과 추가 자료의 경계](docs/source-provenance.md)
- [PDF·질문 요구사항 추적표](docs/requirements-traceability.md)
- [원격 Git 로그 스냅샷](docs/git-log.txt)
- [rename 충돌의 최종 파일](docs/new-file.md)
- [GitHub Flow 시각화](diagrams/01_github-flow.html)
- [충돌 해결 시각화](diagrams/02_conflict-resolution.html)
- [복구 의사결정 시각화](diagrams/03_git-recovery-decision.html)
