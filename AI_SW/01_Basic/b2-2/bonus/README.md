# 선택 보너스

핵심 제출물과 혼동하지 않도록 보너스를 이 폴더에 분리했다.

## CODEOWNERS

`bonus/.github/CODEOWNERS`의 `@OWNER/...`를 실제 GitHub 사용자 또는 팀으로 바꾼 뒤 저장소 루트의 `.github/CODEOWNERS`로 복사한다. Branch Protection의 필수 리뷰어 설정과 함께 사용한다.

## 대화형 rebase 기록 양식

공유되지 않은 개인 feature 브랜치에서만 수행한다. 이 제출 패키지는 Git 저장소가 아니므로 아래 명령은 반드시 별도로 clone한 실제 원격 저장소에서 실행한다.

```bash
UPSTREAM_CLONE="/absolute/path/to/b2-2-git-conflict-craft"
git -C "$UPSTREAM_CLONE" log --oneline -3 > before-rebase.txt
git -C "$UPSTREAM_CLONE" rebase -i HEAD~3
git -C "$UPSTREAM_CLONE" log --oneline -3 > after-rebase.txt
```

| 항목 | 작성 내용 |
| --- | --- |
| 브랜치 | `<feature-branch>` |
| 정리 전 | `<before-rebase.txt 링크>` |
| 사용 동작 | `squash` / `reword` |
| 정리 후 | `<after-rebase.txt 링크>` |
| 정리 이유 | `<리뷰어가 이해하기 쉬워진 점>` |

이미 공유한 브랜치에서는 팀 합의 없이 rebase나 강제 push를 하지 않는다.
