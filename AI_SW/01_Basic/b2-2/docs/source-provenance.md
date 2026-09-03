# 코드 출처와 제출 패키지 경계

## 기준 원격

- 원격 저장소: <https://github.com/dave17code/b2-2-git-conflict-craft>
- 기준 브랜치: `main`
- 기준 커밋: [`daecf53`](https://github.com/dave17code/b2-2-git-conflict-craft/commit/daecf53)
- 재확인 일자: 2026-09-03

이 제출 패키지는 원격 Git 저장소 자체가 아니다. 실제 Issue, branch, commit, PR, review, conflict와 recovery 이력은 위 원격 저장소에 있다.

## 파일 분류

| 경로 | 분류 | 의미 |
|---|---|---|
| `src/*.py` | 원격 원본 스냅샷 | `daecf53`의 `src/`와 byte-for-byte 동일 |
| `docs/new-file.md`, `docs/new_guide.md`, `docs/git-log.txt` | 원격 증거 스냅샷 | 충돌 결과와 당시 Git 로그를 원격 그대로 보존 |
| `examples/team_utils_demo.py` | 추가 예제 | 원격 네 함수를 한 번에 호출하는 제출용 설명 코드이며 원격 커밋으로 주장하지 않음 |
| `tests/` | 추가 검증 | 원격 함수의 동작, 스냅샷 해시, 문서 링크를 검사하는 제출 패키지 전용 코드 |
| `02_demo.sh` | 추가 재현 | 실제 이력과 같은 충돌 유형을 임시 저장소에서 새로 재현함. 과거 PR 실행 로그 자체가 아님 |
| `README_answer.*`, `diagrams/`, `bonus/` | 추가 설명 | PDF와 평가 질문을 설명하기 위한 학습·발표 자료 |
| `SUBMISSION.md`, `docs/*.md` | 원격 근거 + 보충 설명 | 링크와 hash로 실제 기록을 가리키며, 확인 수준과 한계를 함께 표시 |

## 원격 `src/` SHA-256

| 파일 | SHA-256 |
|---|---|
| `count_utils.py` | `a50398767ed3ad17c30bca45c2713016c6185685fdaadef7a56e5f4e659d45f6` |
| `list_utils.py` | `f9657a2bdeb3512b8afae0ab733766a68329798f8b343bad58b4aa760a3fd38a` |
| `main.py` | `a71940f491b306a8e8ec248fb78da669bab6a2c1451014b60d5ff5614ea2ee5d` |
| `math_utils.py` | `f5bd85639645068c9ba33320c57a0789ff960eff85b3ff868bd8d0926192fc78` |
| `string_utils.py` | `39fc4d3050a923d02b13de614f7f9f77cca38fe26aebb3dc8c0601cf270f19a5` |

추가 원격 증거 파일의 SHA-256은 `new-file.md`=`343215f6…249`, `new_guide.md`=`c0ced224…8be`, `git-log.txt`=`a58784ab…89d`다.

`python3 -m unittest discover -s tests -v`는 위 해시를 검사한다. `bash 05_verify_upstream.sh`는 새 clone의 HEAD와 파일을 직접 비교한다. 원격이 바뀌면 먼저 최신 이력을 다시 감사하고, 의도적으로 스냅샷을 갱신한 뒤 기준 commit과 해시를 함께 바꾼다.

## 표현 원칙

- `실제`: Git/GitHub의 URL, commit hash, PR, review 또는 원격 파일로 확인되는 사실
- `원격 원본 스냅샷`: 특정 commit에서 그대로 복사한 파일
- `추가 예제`: 원격 코드를 이해하기 쉽게 만든 새 코드
- `재현`: 과거 상황과 같은 조건을 별도 임시 저장소에서 다시 실행한 결과
- `문서 기록`: 실행 자체를 독립 검증하지 못하고 팀 문서에만 남은 주장

따라서 추가 예제나 재현 결과를 팀원이 원격 PR에서 직접 만든 결과로 바꾸어 표현하지 않는다.
