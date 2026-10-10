# 최신 원격 변경 감사

이 문서는 2026-09-03에 원격 저장소를 별도의 `/tmp` 복제본으로 읽어 조사한 결과다. 사용자의 원천 작업 폴더는 수정하지 않았다. 참여자는 실제 GitHub 계정 `dave17code`, `heeyoung35`, `OliverJoo`, `hyunn9799`로 표기했다.

> **표기 범례:** **[사실]**은 원격 객체/API/PR로 직접 확인, **[재구성]**은 증거의 해석, **[추가 예시]**는 실제 이력과 분리한 학습용 내용이다.

## 1. 기준 상태

- 원격 저장소: <https://github.com/dave17code/b2-2-git-conflict-craft>
- `main` 기준 커밋: `daecf53`
- `main` 상태: `protected: true`
- 협업 권한: 관리자 1명, write 3명으로 총 4명
- 병합 PR: 총 19개, 모두 최소 1개의 `APPROVED` 리뷰 확인
- 내용 있는 실질 리뷰: #2/#4/#7/#8/#24, 총 5/19건
- 열린 PR: 없음

## 2. 이전 기준 `7ee6232` 이후 변경

| PR | 상태 | GitHub 작성자 | 변경 | 핵심 증빙 |
|---|---|---|---|---|
| [#29](https://github.com/dave17code/b2-2-git-conflict-craft/pull/29) | 병합 | OliverJoo | 공유된 임시 문서를 실제 `git revert`로 취소 | 원본 `df3e50c`, 취소 `7a37beb`, merge `f476db6` |
| [#30](https://github.com/dave17code/b2-2-git-conflict-craft/pull/30) | 병합 | dave17code | README, root SUBMISSION, 충돌·복구·Git 로그 문서 정리 및 중복 `docs/SUBMISSION.md` 삭제 | `33a80c9`, `3084263`, merge `5dc72e6` |
| [#31](https://github.com/dave17code/b2-2-git-conflict-craft/pull/31) | 병합 | dave17code | Python 캐시를 `.gitignore`에서 제외 | `af66f1f`, merge `514d472` |
| [#32](https://github.com/dave17code/b2-2-git-conflict-craft/pull/32) | 병합 | dave17code | 복구 문서의 revert placeholder를 실제 hash로 교체 | `80b43c2`, OliverJoo 승인, merge `daecf53` |

PR #29는 `Closes #28`, PR #30은 `Closes #27`로 Issue를 닫았다. PR #31과 PR #32에는 closing keyword가 없으므로 “모든 PR이 Issue와 연결됨”은 충족하지 않는다.

## 3. 원격 문서 전수 확인

| 원격 파일 | 확인한 내용 | 평가 자료 반영 |
|---|---|---|
| `README.md` | 4인 역할, GitHub Flow, 함수 4개, 충돌 2종 주장, 복구 4종 | Git 객체로 확인된 충돌 1건과 미확인 rename/modify 건을 구분 |
| `SUBMISSION.md` | 팀원별 Issue·PR, 충돌 hash, 핵심 문서 인덱스 | 실제 merged PR·review 전체 목록으로 확장 |
| `docs/CONTRIBUTING.md` | 브랜치·커밋·PR·리뷰·충돌 규칙 | 평가용 예시와 최신 횟수를 보강 |
| `docs/conflict-resolution.md` | `main.py` 충돌과 rename/modify 병합 이력 | 실제 충돌 1건과 자동 병합 1건을 구분 |
| `docs/troubleshooting-log.md` | amend/reset/revert/stash의 상황·명령·주의점 | revert는 Git 이력으로 확인, reset은 문서 수준으로 구분 |
| `docs/git-log.txt` | PR #29까지의 그래프 스냅샷 | 스냅샷 생성 시점 이후 PR #30·#31·#32는 별도 최신 기준으로 설명 |
| `docs/new-file.md` | rename/modify 해결 뒤 보존된 최종 내용 | 충돌 결과물로 연결 |
| `docs/new_guide.md` | 줄바꿈 없는 11바이트 `# Old Guide` 한 줄 | 내용 있는 최종 결과로 오인하지 않도록 명시 |
| `.gitignore` | PR #31에서 `__pycache__/`, `*.pyc` 추가 | 제출 사본에도 동일 규칙 반영 |

원격 `src/main.py`는 `reverse_string`과 `count_words`만 실행한다. 이 학습 패키지의 `src/` 5개는 원격 `main`의 blob과 byte-for-byte 일치하도록 복원했다. 네 함수를 한 번에 실행하는 **[추가 예시]**는 `examples/team_utils_demo.py`에 분리했다.

## 4. 평가 시 사실 수준

- **강한 증빙:** 네 함수 commit, 19개 병합 PR, 각 병합 PR의 승인, `abe92b8` 텍스트 충돌, revert 원본·취소 commit, 보호된 `main`
- **미충족:** 내용 있는 실질 리뷰는 5/19건
- **미확인:** `9315e23`은 부모 replay에서 자동 병합되고 `fee0b98`은 1자 수정이므로 두 번째 비자명 충돌의 증거가 아님
- **PR·문서 증빙:** dave17code amend, hyunn9799 stash/pop
- **문서 기록만 확인:** heeyoung35 reset soft. reset 전 commit은 일반 Git graph에서 사라지므로 reflog나 실행 화면이 있으면 더 강하다.
- **최신 반영:** PR #32가 실제 revert hash를 보완했고 승인 후 `main`에 병합됐다.
- **추가 화면 권장:** required approval 수, 직접 push 차단, force push 제한 등 Branch Protection 세부값

## 5. 원천 보존 원칙

감사와 갱신은 별도 복제본과 평가 자료 폴더에서만 수행한다. 원천 작업 폴더에는 `fetch`, checkout, commit, 파일 복사를 하지 않는다.
