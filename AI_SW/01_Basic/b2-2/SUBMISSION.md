# b2-2 제출 인덱스

이 문서는 실제 공개 저장소의 2026-09-03 원격 상태를 기준으로 작성했으며, 참여자를 실제 GitHub 계정 `dave17code`, `heeyoung35`, `OliverJoo`, `hyunn9799`로 표기한다.

> **표기 범례**
>
> - **[사실]** 원격 Git 객체, GitHub API 또는 PR 페이지에서 직접 확인한 내용
> - **[재구성]** 확인된 객체를 시간순으로 해석한 설명이며, 기록되지 않은 터미널 동작까지 증명하지는 않음
> - **[추가 예시]** 학습을 위해 만든 명령·코드로 실제 팀 작업 이력 자체는 아님

## 1. 팀과 저장소

- 팀원 수: **4명**
- 실제 저장소: [dave17code/b2-2-git-conflict-craft](https://github.com/dave17code/b2-2-git-conflict-craft)
- 기본 브랜치: `main`
- 원격 `main` 기준 커밋: `daecf53`
- 권한 확인: Collaborators API에서 관리자 1명과 write 권한 3명, 총 4명을 확인
- Branch Protection: branch API에서 `main protected: true`와 protection enabled를 확인. 다만 세부 protection endpoint는 현재 권한에서 404여서 필수 승인 수·직접 push 차단 값은 설정 화면 증빙 필요

## 2. 팀원별 실제 기여

### dave17code

- 코드: [reverse_string](src/string_utils.py)
- 병합 PR:
  - [#2 문자열 뒤집기 유틸리티](https://github.com/dave17code/b2-2-git-conflict-craft/pull/2) — `Closes #1`
  - [#11 협업 가이드](https://github.com/dave17code/b2-2-git-conflict-craft/pull/11) — `Closes #9`
  - [#15 main.py 충돌용 변경](https://github.com/dave17code/b2-2-git-conflict-craft/pull/15) — Issue #12 관련 표기, closing keyword 없음
  - [#30 최종 제출 문서 정리](https://github.com/dave17code/b2-2-git-conflict-craft/pull/30) — `Closes #27`
  - [#31 Python cache 제외](https://github.com/dave17code/b2-2-git-conflict-craft/pull/31) — closing keyword 없음
  - [#32 실제 revert hash 문서 보완](https://github.com/dave17code/b2-2-git-conflict-craft/pull/32) — commit `80b43c2`, OliverJoo 승인, merge `daecf53`, closing keyword 없음
- 타인 PR 승인:
  - [#4 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/4#pullrequestreview-5057121421)
  - [#14 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/14#pullrequestreview-5057225019)
  - [#26 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/26#pullrequestreview-5062605549)
  - [#29 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/29#pullrequestreview-5088179249)
- 피드백 반영: [PR #2](https://github.com/dave17code/b2-2-git-conflict-craft/pull/2)의 타입 검사·docstring 피드백을 [`5e171a9`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/5e171a9)에서 반영
- 복구 실습 기록: `git commit --amend`

### heeyoung35

- 코드: [count_words](src/count_utils.py), [main.py](src/main.py)
- 병합 PR:
  - [#4 단어 수 유틸리티](https://github.com/dave17code/b2-2-git-conflict-craft/pull/4) — `Closes #3`
  - [#14 README와 main.py 통합](https://github.com/dave17code/b2-2-git-conflict-craft/pull/14) — `Closes #10`
- 타인 PR 승인:
  - [#2 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/2#pullrequestreview-5057082075)
  - [#11 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/11#pullrequestreview-5057152415)
- 피드백 반영: [PR #4](https://github.com/dave17code/b2-2-git-conflict-craft/pull/4)의 앞뒤 공백 처리 피드백을 [`e47ac39`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/e47ac39)에서 반영
- 복구 실습 기록: `git reset --soft HEAD~1`

### OliverJoo

- 코드: [remove_duplicates](src/list_utils.py)
- 병합 PR:
  - [#7 리스트 중복 제거](https://github.com/dave17code/b2-2-git-conflict-craft/pull/7) — `Closes #5`
  - [#16 충돌용 old-guide 생성](https://github.com/dave17code/b2-2-git-conflict-craft/pull/16) — `Closes #12`
  - [#17 old-guide 이름 변경](https://github.com/dave17code/b2-2-git-conflict-craft/pull/17) — Issue #12 관련 표기, closing keyword 없음
  - [#19 이름 변경 재실습](https://github.com/dave17code/b2-2-git-conflict-craft/pull/19) — closing link 없음
  - [#22 old-guide를 new-file로 변경](https://github.com/dave17code/b2-2-git-conflict-craft/pull/22) — `Closes #21`
  - [#29 실제 git revert 실습](https://github.com/dave17code/b2-2-git-conflict-craft/pull/29) — `Closes #28`
- 타인 PR 승인:
  - [#8 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/8#pullrequestreview-5057139489)
  - [#18 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/18#pullrequestreview-5057265642)
  - [#20 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/20#pullrequestreview-5057286130)
  - [#24 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/24#pullrequestreview-5059691280)
  - [#30 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/30#pullrequestreview-5088331542)
  - [#31 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/31#pullrequestreview-5088417851)
  - [#32 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/32#pullrequestreview-5088746113)
- 피드백 반영: [PR #7](https://github.com/dave17code/b2-2-git-conflict-craft/pull/7)의 반환 순서 설명 피드백을 [`db5ae1a`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/db5ae1a)에서 반영
- 복구 실습 기록: `git revert`

### hyunn9799

- 코드: [is_even](src/math_utils.py)
- 병합 PR:
  - [#8 짝수 판별 유틸리티](https://github.com/dave17code/b2-2-git-conflict-craft/pull/8) — `Closes #6`
  - [#18 old-guide 수정](https://github.com/dave17code/b2-2-git-conflict-craft/pull/18) — Issue #12 관련 표기, closing keyword 없음
  - [#20 내용 수정 재실습](https://github.com/dave17code/b2-2-git-conflict-craft/pull/20) — Issue #12 관련 표기, closing keyword 없음
  - [#24 rename/modify 충돌 해결](https://github.com/dave17code/b2-2-git-conflict-craft/pull/24) — `Closes #23`
  - [#26 트러블슈팅·제출 문서](https://github.com/dave17code/b2-2-git-conflict-craft/pull/26) — `Closes #25`
- 타인 PR 승인:
  - [#7 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/7#pullrequestreview-5057131918)
  - [#15 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/15#pullrequestreview-5057218005)
  - [#16 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/16#pullrequestreview-5057227830)
  - [#17 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/17#pullrequestreview-5057249630)
  - [#19 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/19#pullrequestreview-5057280115)
  - [#22 승인](https://github.com/dave17code/b2-2-git-conflict-craft/pull/22#pullrequestreview-5059632258)
- 피드백 반영: [PR #8](https://github.com/dave17code/b2-2-git-conflict-craft/pull/8)의 0·음수 설명 피드백을 [`38ab44f`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/38ab44f)에서 반영
- 복구 실습 기록: `git stash` / `git stash pop`

## 3. 요구사항 충족 현황

| 평가 항목                             | 상태                    | 근거 또는 보완점                                                                                                                           |
| ------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 단일 저장소에서 4인 협업              | 확인                    | 저장소·작성자·병합 이력                                                                                                                  |
| 팀원별 병합 PR 2개 이상               | 충족                    | 위 실제 PR 링크                                                                                                                            |
| 팀원별 타인 PR**승인** 2개 이상 | 충족                    | 위`APPROVED` review 링크                                                                                                                 |
| 팀원별 실질 리뷰 2개 이상             | **미충족**        | 내용 있는 실질 피드백은#2/#4/#7/#8/#24, 총 5/19건만 확인                                                                                   |
| 팀원별 본인 PR 피드백 반영 1회        | 부분 확인               | PR#2/#4/#7/#8과 후속 커밋은 확인되나 전체 PR의 실질 리뷰 요건은 미충족                                                                     |
| PR What/Why/How                       | 주요 PR에서 확인        | 실제 PR 본문                                                                                                                               |
| 모든 PR의`Closes #n`                | **미충족**        | #15/#17/#18/#19/#20/#31/#32는 closing link 누락                                                                                            |
| 충돌 2회, 비자명 1회                  | **미확인/미충족** | `abe92b8`의 텍스트 충돌은 확인. `9315e23`은 rename을 자동 병합했고 `fee0b98`은 마침표 1자 수정이라 두 번째 실제 충돌을 입증하지 못함 |
| 복구 명령 4종                         | 부분 확인               | revert는 실제 commit·PR, amend/stash는 PR 본문, reset은 문서 기록                                                                         |
| Branch Protection                     | 보호 활성 확인          | `main protected: true`; 세부 규칙 값은 설정 화면 필요                                                                                    |

## 4. 실제 충돌 증빙

- **[사실] 확인된 동일 영역 충돌:** [PR #14](https://github.com/dave17code/b2-2-git-conflict-craft/pull/14), [PR #15](https://github.com/dave17code/b2-2-git-conflict-craft/pull/15), 해결 merge commit [`abe92b8`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/abe92b8)
- **[사실] rename/modify 병합 이력:** [PR #22](https://github.com/dave17code/b2-2-git-conflict-craft/pull/22), [PR #24](https://github.com/dave17code/b2-2-git-conflict-craft/pull/24), merge commit [`9315e23`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/9315e23), 후속 commit [`fee0b98`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/fee0b98)
- **판정:** `9315e23`의 두 부모를 replay하면 Git이 수정 내용을 `new-file.md`로 자동 병합한다. `fee0b98`은 끝의 `..`를 `.!`로 바꾼 1자 수정이다. commit/PR의 설명만으로는 실제 modify/delete 충돌이나 수동 해결을 입증할 수 없다.
- 상세 판단: [docs/conflict-resolution.md](docs/conflict-resolution.md)

## 5. 핵심 문서

- [README.md](README.md)
- [평가 질문과 답변](README_answer.md)
- [협업 규칙](docs/CONTRIBUTING.md)
- [충돌 해결 기록](docs/conflict-resolution.md)
- [트러블슈팅 기록](docs/troubleshooting-log.md)
- [Git 이력 증빙](docs/git-history-evidence.md)
- [최신 원격 변경 전수 감사](docs/remote-change-audit.md)
- [원격 원본과 추가 자료의 경계](docs/source-provenance.md)
- [PDF·평가 질문 요구사항 추적표](docs/requirements-traceability.md)

## 6. Git 그래프 일부

```text
*   daecf53 Merge pull request #32 ... docs/update-revert-hash
*   514d472 Merge pull request #31 ... chore/ignore-python-cache
*   5dc72e6 Merge pull request #30 ... feature/kim-final-docs
*   f476db6 Merge pull request #29 ... feature/joo-revert-practice
| * 7a37beb Revert "docs: add temporary revert practice file"
| * df3e50c docs: add temporary revert practice file
*   7ee6232 Merge pull request #26 ... feature/kwon-troubleshooting-submission
*   5b06f78 Merge pull request #24 ... feature/kwon-update-old-guide
| * fee0b98 fix: resolve modify/delete conflict by moving changes to new-file.md
| * 9315e23 Merge branch 'main' ... into feature/kwon-update-old-guide
*   e660623 Merge pull request #22 ... feature/joo-rename-new-file
*   ab62450 Merge pull request #14 ... feature/kang-readme-main
| * abe92b8 fix: resolve conflict in main.py by combining Kim and Kang outputs
*   90a6ddf Merge pull request #15 ... feature/kim-main-conflict
*   e61f2bf Merge pull request #11 ... feature/kim-contributing
*   2c58a81 Merge pull request #8 ... feature/kwon-math-utils
*   339aa53 Merge pull request #7 ... feature/joo-list-utils
*   44f90df Merge pull request #4 ... geature/kang-count-utils
*   b22f9e3 Merge pull request #2 ... feature/kim-string-utils
*   175ea3c chore: 프로젝트 초기화 및 .gitignore 설정
```

전체 그래프와 파일별 커밋은 [docs/git-history-evidence.md](docs/git-history-evidence.md)에서 확인한다.
