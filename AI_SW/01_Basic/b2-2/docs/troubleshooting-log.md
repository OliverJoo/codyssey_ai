# Git 트러블슈팅 실습 기록

원천 저장소의 최신 문서·PR·Git 이력을 네 GitHub 계정 기준으로 정리했다. `commit --amend`와 `stash`는 실제 PR 본문에서 실행·검증 문구를 확인했고, `revert`는 원본·취소 commit과 병합 PR까지 확인했다. `reset --soft`는 원천 문서에 담당·절차가 기록되어 있지만 일반 commit graph만으로 실행 사실을 독립 입증하기 어렵다.

> **표기 범례:** **[사실]**은 원격 객체/API/PR로 확인, **[재구성]**은 문서 기록을 바탕으로 정리한 절차, **[추가 예시]**는 실제 이력과 분리된 연습 명령이다.

> **실행 위치 경고:** 아래 쓰기 명령은 버려도 되는 원격 저장소 clone을 `UPSTREAM_CLONE`으로 지정한 경우에만 연습한다. 이 학습자료 폴더에서 bare `git amend/reset/revert/stash`를 실행하면 상위의 다른 저장소를 변경할 수 있다.

```bash
UPSTREAM_CLONE="/absolute/path/to/disposable-b2-2-git-conflict-craft-clone"
```

## 증빙 수준 요약

| 실습 | 담당 | 확인된 근거 | 추가 권장 증빙 |
|---|---|---|---|
| `commit --amend` | dave17code | PR #11 본문, 원천 트러블슈팅 문서 | amend 전후 해시 또는 reflog |
| `reset --soft HEAD~1` | heeyoung35 | 원천 트러블슈팅 문서 | 실행 직후 `git status`, reflog |
| `git revert` | OliverJoo | 원본 `df3e50c`, 취소 `7a37beb`, PR #29 | 추가 증빙 불필요 |
| `stash` / `stash pop` | hyunn9799 | PR #26 본문, 원천 트러블슈팅 문서 | `git stash list` 전후 화면 |

## 1. dave17code - `git commit --amend`

### 상황

협업 가이드 커밋 메시지에 오타가 있어 최근 로컬 커밋 메시지를 고쳐야 했다. PR [#11](https://github.com/dave17code/b2-2-git-conflict-craft/pull/11)의 검증 항목에 amend 실행과 `git log` 확인이 기록되어 있다.

### [재구성] 연습 절차

```bash
git -C "$UPSTREAM_CLONE" status
git -C "$UPSTREAM_CLONE" log -1 --oneline
git -C "$UPSTREAM_CLONE" commit --amend -m "docs: add contributing guide and team rules"
git -C "$UPSTREAM_CLONE" log -1 --oneline
```

### 결과와 주의점

- 파일 내용은 유지되고 최근 commit 메시지와 hash가 바뀐다.
- push하기 전 개인 브랜치의 최신 commit에 사용하는 것이 안전하다.
- 이미 공유했다면 동료와 hash가 달라지므로 무단 amend와 force push를 하지 않는다.

## 2. heeyoung35 - `git reset --soft HEAD~1`

### 상황

미완성 변경을 실수로 commit했지만 작업 내용은 잃지 않고 보완해야 했다. 원천 문서는 heeyoung35가 `reset --soft`를 담당했다고 기록한다.

### [재구성] 연습 절차

```bash
git -C "$UPSTREAM_CLONE" status
git -C "$UPSTREAM_CLONE" log -2 --oneline
git -C "$UPSTREAM_CLONE" reset --soft HEAD~1
git -C "$UPSTREAM_CLONE" status
# 파일 보완 후
git -C "$UPSTREAM_CLONE" add <수정한-파일>
git -C "$UPSTREAM_CLONE" commit -m "feat: complete utility implementation"
```

### 결과와 주의점

- 브랜치 포인터만 한 commit 전으로 이동한다.
- 취소한 commit의 변경은 staging area에 남는다.
- 원격에 공유한 commit에는 사용하지 않는다.
- 최종 graph에는 reset으로 사라진 이전 commit이 보이지 않으므로 reflog나 실행 화면이 증빙에 필요하다.

## 3. OliverJoo - `git revert`

### 상황

원격에 공유된 임시 문서 commit `df3e50c`를 기존 역사에서 지우지 않고 취소했다. 취소 commit `7a37beb`은 제목이 `Revert "docs: add temporary revert practice file"`이며 두 commit은 PR [#29](https://github.com/dave17code/b2-2-git-conflict-craft/pull/29)로 `main`에 병합됐다.

### [사실] 안전한 이력 확인

```bash
git -C "$UPSTREAM_CLONE" show --stat df3e50c
git -C "$UPSTREAM_CLONE" show --stat 7a37beb
git -C "$UPSTREAM_CLONE" log --oneline --ancestry-path df3e50c^..7a37beb
```

최신 `main`에는 취소 commit까지 이미 포함되어 있으므로 같은 `revert`를 다시 실행하지 않는다. 새 revert 연습이 필요하면 실제 이력 확인과 분리된 disposable branch에서 별도 예제로 수행한다.

### 결과와 주의점

- 원래 commit을 삭제하지 않고 반대 변경의 새 commit을 만든다.
- 공유 브랜치에서도 동료가 일반 pull로 같은 역사에 도달할 수 있다.
- 원본 `df3e50c`와 취소 `7a37beb`이 모두 graph에 남아 동작과 이력 보존을 함께 증명한다.
- PR #32의 `80b43c2`가 복구 문서의 hash placeholder를 실제 원본 `df3e50c`와 취소 `7a37beb`로 교체했고, OliverJoo의 승인 뒤 merge `daecf53`으로 원격 `main`에 반영됐다.

## 4. hyunn9799 - `git stash` / `git stash pop`

### 상황

완료되지 않은 변경이 있는 상태에서 다른 작업으로 전환해야 했다. PR [#26](https://github.com/dave17code/b2-2-git-conflict-craft/pull/26)의 본문에는 stash로 임시 보관한 뒤 다른 작업 후 `stash pop`으로 복원했다고 기록되어 있다.

### [재구성] 연습 절차

```bash
git -C "$UPSTREAM_CLONE" status
git -C "$UPSTREAM_CLONE" stash push -m "WIP hyunn9799 documentation"
git -C "$UPSTREAM_CLONE" stash list
git -C "$UPSTREAM_CLONE" switch main
# 필요한 다른 작업 확인 후 원래 브랜치 복귀
git -C "$UPSTREAM_CLONE" switch feature/kwon-troubleshooting-submission
git -C "$UPSTREAM_CLONE" stash pop
git -C "$UPSTREAM_CLONE" status
```

### 결과와 주의점

- 미완성 변경을 commit하지 않고 작업 트리를 깨끗하게 만들었다.
- `pop`은 적용 성공 시 stash 항목을 제거한다. 먼저 확인하려면 `git stash apply`를 사용한다.
- stash는 로컬에만 있으므로 장기 백업이나 팀 공유 수단으로 쓰지 않는다.
- `pop` 중 충돌이 나면 일반 충돌 절차로 해결한다.

## 명령 선택표

| 질문 | 답 | 명령 |
|---|---|---|
| 아직 commit하지 않은 변경을 잠시 치울까? | 예 | `stash` |
| 최근 로컬 commit만 보완할까? | 예 | `commit --amend` |
| 최근 로컬 commit을 취소하되 변경을 staged로 남길까? | 예 | `reset --soft HEAD~1` |
| 이미 공유된 변경을 안전하게 취소할까? | 예 | `revert` |

관련 시각 자료: [Git 복구 의사결정 다이어그램](../diagrams/03_git-recovery-decision.html)
