# 실제 Git·GitHub 이력 증빙

이 문서는 원천 저장소를 **읽기 전용**으로 조사해 `main`의 Git 이력과 공개 GitHub 기록을 실제 계정 기준으로 정리한 결과다. 원천 파일은 수정하지 않았다.

> **표기 범례:** **[사실]**은 원격 객체/API/PR에서 확인, **[재구성]**은 확인된 객체의 해석, **[추가 예시]**는 실제 이력에 없는 학습용 내용이다.

## 1. 검증 기준

- 원격 저장소: <https://github.com/dave17code/b2-2-git-conflict-craft>
- 확인한 원격 `main` 기준 커밋: `daecf53`
- 확인 시점: 2026-09-03, 원격 저장소의 별도 clone(`UPSTREAM_CLONE`)에서 확인
- Collaborator: 관리자 1명과 push 권한 3명, 총 4명
- 표시 이름: 실제 GitHub 계정 `dave17code`, `heeyoung35`, `OliverJoo`, `hyunn9799`
- 상태: 병합 PR 19개, 모두 승인 확인, 열린 PR 없음

## 2. 팀원별 실제 병합 PR과 리뷰

| 팀원 | 실제 기능·역할 | 확인된 병합 PR | 타인 PR 승인 |
|---|---|---|---|
| dave17code | `reverse_string`, 협업 규칙·최종 문서·캐시·복구 기록 | [#2](https://github.com/dave17code/b2-2-git-conflict-craft/pull/2), [#11](https://github.com/dave17code/b2-2-git-conflict-craft/pull/11), [#15](https://github.com/dave17code/b2-2-git-conflict-craft/pull/15), [#30](https://github.com/dave17code/b2-2-git-conflict-craft/pull/30), [#31](https://github.com/dave17code/b2-2-git-conflict-craft/pull/31), [#32](https://github.com/dave17code/b2-2-git-conflict-craft/pull/32) | #4, #14, #26, #29 |
| heeyoung35 | `count_words`, README·runner | [#4](https://github.com/dave17code/b2-2-git-conflict-craft/pull/4), [#14](https://github.com/dave17code/b2-2-git-conflict-craft/pull/14) | #2, #11 |
| OliverJoo | `remove_duplicates`, rename 충돌·revert | [#7](https://github.com/dave17code/b2-2-git-conflict-craft/pull/7), [#16](https://github.com/dave17code/b2-2-git-conflict-craft/pull/16), [#17](https://github.com/dave17code/b2-2-git-conflict-craft/pull/17), [#19](https://github.com/dave17code/b2-2-git-conflict-craft/pull/19), [#22](https://github.com/dave17code/b2-2-git-conflict-craft/pull/22), [#29](https://github.com/dave17code/b2-2-git-conflict-craft/pull/29) | #8, #18, #20, #24, #30, #31, #32 |
| hyunn9799 | `is_even`, modify 충돌·최종 문서 | [#8](https://github.com/dave17code/b2-2-git-conflict-craft/pull/8), [#18](https://github.com/dave17code/b2-2-git-conflict-craft/pull/18), [#20](https://github.com/dave17code/b2-2-git-conflict-craft/pull/20), [#24](https://github.com/dave17code/b2-2-git-conflict-craft/pull/24), [#26](https://github.com/dave17code/b2-2-git-conflict-craft/pull/26) | #7, #15, #16, #17, #19, #22 |

네 계정 모두 병합 PR 2개 이상과 타인 PR **승인** 2회 이상을 충족한다. 확인한 19개 병합 PR은 모두 최소 1개의 `APPROVED` 리뷰가 있다. 다만 내용 있는 실질 피드백은 #2/#4/#7/#8/#24의 **5/19건**뿐이므로, 승인 횟수를 실질 리뷰 요구 충족으로 해석하면 안 된다. 초기 커밋 뒤 `main`의 first-parent 경로는 모두 2-parent PR merge commit이다.

[PR #32](https://github.com/dave17code/b2-2-git-conflict-craft/pull/32)는 dave17code의 `docs/update-revert-hash` 작업이다. commit `80b43c2`에서 revert placeholder를 실제 hash로 바꾸고 OliverJoo의 승인을 받아 merge commit `daecf53`으로 반영됐다.

## 3. 확인된 실질 피드백

| 작성자 | 기능 PR | 리뷰 내용 요약 | 반영 커밋 |
|---|---:|---|---|
| dave17code | #2 | 타입 검사와 docstring 예시 보강 | `5e171a9` |
| heeyoung35 | #4 | 앞뒤 공백 처리를 명시적으로 보강 | `e47ac39` |
| OliverJoo | #7 | `set` 변환의 순서 비보장 명시 | `db5ae1a` |
| hyunn9799 | #8 | 0과 음수 짝수 설명 보강 | `38ab44f` |
| OliverJoo | #24 | rename/modify 결과에 대한 구체적 검토 의견 | 별도 반영 commit으로 단정 불가 |

나머지 14개 PR의 `APPROVED`는 확인되지만, 내용 있는 피드백까지 확인되지는 않았다. 따라서 프로젝트 전체의 실질 리뷰 요구는 미충족이다.

## 4. 실제 충돌 이력

### 동일 영역 충돌

- heeyoung35는 `src/main.py`에 `count_words` 실행을 추가했다.
- dave17code는 같은 실행 영역에 `reverse_string` 출력을 추가했다.
- 해결 merge commit `abe92b8`은 두 import와 두 출력을 함께 보존했다.
- 이후 PR #14와 #15가 `main`에 병합되었다.

### rename/modify 자동 병합 이력

- OliverJoo의 `99ef129`는 `old-guide.md`를 `new-file.md`로 변경했다.
- hyunn9799의 `2579e64`, `1b1ec20`은 기존 경로의 내용을 수정했다.
- merge `9315e23`은 부모 replay에서 수정 내용을 새 파일로 자동 병합한다.
- `fee0b98`의 실제 diff는 문장 끝 `..`를 `.!`로 바꾼 1자 수정이다.
- 최종적으로 PR #22와 #24가 병합되었다.

commit 메시지와 review는 “modify/delete 충돌 해결”을 주장하지만 Git 객체만으로 실제 충돌이나 수동 해결은 확인되지 않는다. 이 건을 비자명 충돌 요구의 충족 증거로 계산하지 않는다.

## 5. 요구사항별 증거 수준

- **확인됨:** 공개 저장소, 4명 collaborator, 보호된 `main`, 19개 병합 PR, 전 병합 PR 최소 1회 승인, 네 기능, `abe92b8`의 실제 텍스트 충돌
- **미충족:** 실질 리뷰는 5/19건만 확인됨
- **미확인:** rename/modify 이력은 자동 병합되어 두 번째 비자명 충돌을 입증하지 못함
- **문서와 PR 본문으로 확인됨:** dave17code의 amend, hyunn9799의 stash/pop
- **commit과 PR로 확인됨:** OliverJoo의 revert. 원본 `df3e50c`, 취소 `7a37beb`, 병합 PR #29가 연결된다.
- **문서상 수행:** heeyoung35의 reset soft. 현재 commit graph만으로 실행 전후 상태를 독립 검증할 수는 없다.
- **부분 충족:** 핵심 PR 다수는 `Closes`로 Issue와 연결했지만 #15/#17/#18/#19/#20/#31/#32는 closing link가 없다.
- **세부 확인 제한:** `main`은 API에서 protected로 확인되지만 required approval 수와 직접 push 차단 세부값은 protection endpoint에서 조회되지 않았다.

## 6. 최신 원격 추가 이력

| PR | merge commit | 내용 | 승인자 |
|---|---|---|---|
| #29 | `f476db6` | OliverJoo의 실제 revert 실습 | dave17code |
| #30 | `5dc72e6` | 최종 README·SUBMISSION·충돌·복구·Git 로그 문서 | OliverJoo |
| #31 | `514d472` | `.gitignore`에 Python cache 제외 | OliverJoo |
| #32 | `daecf53` | 실제 revert hash 문서 보완 (`80b43c2`) | OliverJoo |

세 파일의 자세한 변화와 원격 문서별 반영 결과는 [remote-change-audit.md](remote-change-audit.md)에 있다.

따라서 답변 문서는 “규칙을 정했다”, “공개 기록으로 확인했다”, “추가 화면 증빙이 필요하다”를 구분한다.
