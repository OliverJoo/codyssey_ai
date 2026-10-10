# 실제 충돌과 rename/modify 병합 이력

이 문서는 실제 저장소의 commit graph, combined diff, PR 본문을 교차 검증한다. `main.py` 텍스트 충돌은 Git 객체로 확인되지만, rename/modify 건은 부모 replay에서 자동 병합되어 실제 충돌로 확인되지 않았다.

> **표기 범례:** **[사실]**은 원격 객체/API로 직접 확인, **[재구성]**은 객체를 근거로 한 해석, **[추가 예시]**는 실제 작업과 분리된 학습용 절차다.

> **실행 위치 경고:** 아래 확인 명령은 원격 저장소의 독립 clone을 가리키는 `UPSTREAM_CLONE`에서만 실행한다. 이 학습자료 폴더에서 bare Git 명령을 실행하면 상위의 다른 저장소에 작동할 수 있다.

## 기록 1 - `src/main.py` 동일 영역 충돌

### 참여자와 근거

- dave17code: PR [#15](https://github.com/dave17code/b2-2-git-conflict-craft/pull/15), commit `e7917b1`
- heeyoung35: PR [#14](https://github.com/dave17code/b2-2-git-conflict-craft/pull/14), commits `932dd4c`, `4241fdc`
- 충돌 해결 merge commit: [`abe92b8`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/abe92b8)

### 상황

dave17code는 `src/main.py`의 import와 출력 영역에 `reverse_string`을 추가했다. heeyoung35는 같은 영역에 `count_words`를 추가했다. heeyoung35 브랜치가 `main`을 병합할 때 Git이 동일한 실행 블록의 최종 의도를 자동으로 선택할 수 없었다.

**[재구성]** 양쪽 변경 의도는 다음과 같았다. 출력 라벨은 실제 역사적 파일의 `Kim Result`, `Kang Result`를 보존한다.

```python
# dave17code 변경
from string_utils import reverse_string
print("Kim Result:", reverse_string("Hello World"))

# heeyoung35 변경
from count_utils import count_words
print("Kang Result:", count_words("Hello Python Git Collaboration"))
```

### 판단과 해결

두 유틸리티는 서로 대체 관계가 아니라 모두 필요한 기능이었다. 따라서 어느 한쪽을 버리지 않고 import 두 개와 출력 두 개를 결합했다. 동시에 잘못된 진입점 조건을 `if __name__ == "__main__":`로 확정했다.

```python
from string_utils import reverse_string
from count_utils import count_words

if __name__ == "__main__":
    print("=== Python Utils Demo ===")
    print("Kim Result:", reverse_string("Hello World"))
    print("Kang Result:", count_words("Hello Python Git Collaboration"))
```

확인 명령:

```bash
UPSTREAM_CLONE="/absolute/path/to/b2-2-git-conflict-craft"
git -C "$UPSTREAM_CLONE" show --cc abe92b8 -- src/main.py
python3 "$UPSTREAM_CLONE/src/main.py"
```

### 결과

- dave17code의 `reverse_string` 출력 보존
- heeyoung35의 `count_words` 출력 보존
- merge commit `abe92b8`에 combined diff 기록
- 이후 PR #14가 `ab62450`으로 `main`에 병합

### 예방

`main.py`처럼 여러 모듈이 모이는 파일은 PR 전에 담당자와 통합 순서를 합의한다. 공용 진입점 변경은 작은 커밋으로 만들고 최신 `main`을 자주 병합해 충돌 범위를 줄인다.

## 기록 2 - `old-guide.md` rename 대 내용 수정: 자동 병합

### 참여자와 근거

- OliverJoo: PR [#22](https://github.com/dave17code/b2-2-git-conflict-craft/pull/22), rename commit `99ef129`
- hyunn9799: PR [#24](https://github.com/dave17code/b2-2-git-conflict-craft/pull/24), modify commits `2579e64`, `1b1ec20`
- 통합 merge commit: [`9315e23`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/9315e23)
- 후속 해결 commit: [`fee0b98`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/fee0b98)

### 확인된 상황

**[사실]** 공통 조상의 `docs/old-guide.md`를 OliverJoo는 `docs/new-file.md`로 이름 변경했고 hyunn9799는 기존 경로의 내용을 수정했다. 그러나 부모 커밋 `1b1ec20`과 `e660623`을 replay하면 Git이 수정된 내용을 새 경로로 자동 병합한다. rename/modify가 동시에 있었다는 사실만으로 실제 충돌이 발생했다고 판단할 수 없다.

Replay 결과는 `Automatic merge went well`이었고 staged 상태는 `R100 docs/old-guide.md -> docs/new-file.md`였다.

실제 시간 순서:

1. `a33831a`: 충돌 실습용 `old-guide.md` 생성
2. `99ef129`: OliverJoo이 `old-guide.md` → `new-file.md` rename
3. `2579e64`, `1b1ec20`: hyunn9799가 `old-guide.md` 내용 수정
4. `9315e23`: hyunn9799 브랜치에 `main`을 병합. 결과 tree에 수정 내용이 `new-file.md`로 자동 반영
5. `fee0b98`: 마지막 문장 끝의 `..`를 `.!`로 바꾼 1자 수정
6. `5b06f78`: PR #24 병합

### Git 객체 판정

`9315e23`의 commit 메시지와 PR #24 설명은 충돌 해결을 주장하지만, 실제 tree와 부모 replay에서는 수동 해결이 필요한 충돌이 재현되지 않는다. `fee0b98`도 내용 이동이 아니라 구두점 1자를 수정한다. 따라서 이 이력은 **rename/modify 자동 병합 사례**로는 사용할 수 있지만, “두 번째 비자명 충돌을 해결했다”는 요구사항 증거로는 사용할 수 없다.

```bash
UPSTREAM_CLONE="/absolute/path/to/b2-2-git-conflict-craft"
git -C "$UPSTREAM_CLONE" show --summary 9315e23
git -C "$UPSTREAM_CLONE" show --cc --name-status 9315e23
git -C "$UPSTREAM_CLONE" diff 9315e23 fee0b98 -- docs/new-file.md
```

### 결과

- **[사실]** 최종 경로: [docs/new-file.md](new-file.md)
- **[사실]** hyunn9799의 수정 내용은 merge tree에 보존됨
- **[사실]** PR #24 review에는 “비자명 충돌 해결”이라는 의견이 있지만, 이는 리뷰어의 서술이며 충돌 발생 자체의 Git 증거는 아님
- **[사실]** `fee0b98`의 실제 diff는 구두점 1자 변경

> 비자명 충돌을 충족하려면 실제 `CONFLICT` 출력, index의 unmerged stages, 충돌 마커, 또는 동일 부모에서 충돌이 재현되는 로그가 추가로 필요하다.

### 예방

- 파일 rename·move 전에 관련 PR과 담당자를 팀 채널에 공지한다.
- 다른 브랜치가 같은 파일을 수정 중인지 확인한다.
- 대규모 이동은 내용 변경과 별도 PR로 분리한다.
- rename 후 링크와 import 경로 검사를 수행한다.

## 증거 판정 체크리스트

- [x] `abe92b8`에서 실제 텍스트 충돌과 결합 결과를 확인했다.
- [x] `9315e23`의 두 부모와 최종 tree를 확인했다.
- [x] `fee0b98`의 실제 diff가 1자 변경임을 확인했다.
- [ ] 두 번째 비자명 충돌 발생을 입증하는 Git/터미널 증거를 확보한다.

**[추가 예시]** rename과 수정이 실제로 충돌하는 별도 실습은 만들 수 있지만, 그 결과를 원격 팀의 수행 이력으로 계산해서는 안 된다.

관련 시각 자료: [충돌 해결 다이어그램](../diagrams/02_conflict-resolution.html)
