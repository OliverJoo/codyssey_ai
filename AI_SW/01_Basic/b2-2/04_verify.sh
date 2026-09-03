#!/usr/bin/env bash
set -euo pipefail

# 제출 전 코드, 스크립트, 필수 문구를 한 번에 검사한다.
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"

bash 01_setup.sh
bash 03_test.sh
bash -n 01_setup.sh 02_demo.sh 03_test.sh 04_verify.sh 05_verify_upstream.sh

# README와 답변 문서의 파일명·링크 정합성을 확인한다.
python3 tests/verify_links.py

# 원격 원본 스냅샷과 실제 협업 기록이 모두 있는지 확인한다.
grep -q 'dave17code' README.md
grep -q 'heeyoung35' README.md
grep -q 'OliverJoo' README.md
grep -q 'hyunn9799' README.md
grep -q 'reverse_string' src/string_utils.py
grep -q 'count_words' src/count_utils.py
grep -q 'remove_duplicates' src/list_utils.py
grep -q 'is_even' src/math_utils.py
grep -q '원격 원본 스냅샷' docs/source-provenance.md
grep -q '추가 예제' examples/team_utils_demo.py
grep -q 'GitHub Flow' docs/CONTRIBUTING.md
grep -q 'Closes #' .github/pull_request_template.md
grep -q '변경 사항 (What)' .github/pull_request_template.md
grep -q '변경 이유 (Why)' .github/pull_request_template.md
grep -q '테스트/검증 (How)' .github/pull_request_template.md
grep -q '## 기록 1' docs/conflict-resolution.md
grep -q '## 기록 2' docs/conflict-resolution.md
grep -q 'git commit --amend' docs/troubleshooting-log.md
grep -q 'git reset --soft HEAD~1' docs/troubleshooting-log.md
grep -q 'git revert' docs/troubleshooting-log.md
grep -q 'git stash' docs/troubleshooting-log.md
grep -q 'daecf53' docs/git-history-evidence.md
grep -q 'df3e50c' docs/troubleshooting-log.md
grep -q '7a37beb' docs/troubleshooting-log.md
grep -q 'PR #32' docs/remote-change-audit.md
grep -q '__pycache__/' .gitignore

# 최신 원격의 승인·병합 상태와 실제 계정 표기를 확인한다.
grep -q '병합 PR 19개' docs/git-history-evidence.md
grep -q 'OliverJoo' docs/remote-change-audit.md
grep -q '열린 PR: 없음' docs/remote-change-audit.md
! grep -Eq '팀원[1-4]|team-member-[1-4]|익명화' README.md README_answer.md README_answer.html SUBMISSION.md docs/*.md diagrams/*.html
! grep -q '15개 PR' README.md README_answer.md README_answer.html

echo "검증 완료: 코드 테스트와 핵심 제출 문서 조건을 모두 통과했습니다."
