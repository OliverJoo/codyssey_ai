#!/usr/bin/env bash
set -Eeuo pipefail

# 제출 전 번호형 파일·문법·보고서 구조·링크를 한 번에 검사한다.
root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# PDF 미션 수행과 설명에 필요한 전체 파일 목록이다.
required=(
  01_README.md
  02_mission-flow.mmd 02_mission-flow.svg 02_mission-flow.png 02_mission-flow.excalidraw
  03_diagram-viewer.html 04_monitor.sh 05_run_case.sh 06_run_mission.sh
  07_evidence_oom-before.log 08_evidence_oom-after.log 09_report_oom.md
  10_evidence_cpu-before.log 11_evidence_cpu-after.log 12_report_cpu.md
  13_evidence_deadlock-before.log 14_evidence_deadlock-after.log 15_report_deadlock.md
  16_README_answer.md 17_README_answer.html 18_verify_submission.sh
)

# 하나라도 누락되면 마지막에 실패하도록 상태를 누적한다.
fail=0
for file in "${required[@]}"; do
  if [[ ! -s "$root_dir/$file" ]]; then
    echo "MISSING: $file"
    fail=1
  fi
done

# 번호를 붙이기 전의 예전 파일명이 남았는지도 확인한다.
legacy=(
  README.md README_answer.md README_answer.html
  monitor.sh run_case.sh run_mission.sh verify_submission.sh
  report_oom.md report_cpu.md report_deadlock.md
  mission-flow.mmd mission-flow.svg mission-flow.png mission-flow.excalidraw
  diagram-viewer.html
)
for file in "${legacy[@]}"; do
  if [[ -e "$root_dir/$file" ]]; then
    echo "LEGACY NAME: $file (numbered filename required)"
    fail=1
  fi
done

# bash -n으로 네 셸 스크립트의 문법을 검사한다.
for script in 04_monitor.sh 05_run_case.sh 06_run_mission.sh 18_verify_submission.sh; do
  bash -n "$root_dir/$script" || fail=1
done

# 세 리포트가 PDF에서 요구한 네 구역을 모두 갖췄는지 확인한다.
for report in 09_report_oom.md 12_report_cpu.md 15_report_deadlock.md; do
  for heading in "Description" "Evidence & Logs" "Root Cause Analysis" "Workaround & Verification"; do
    grep -q "$heading" "$root_dir/$report" || {
      echo "INVALID: $report lacks '$heading'"
      fail=1
    }
  done
done

# Markdown/HTML 링크와 질문별 관련 파일 링크를 실제 경로와 대조한다.
python3 - "$root_dir" <<'PY' || fail=1
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import re
import sys

root = Path(sys.argv[1]).resolve()
docs = [
    root / "01_README.md",
    root / "09_report_oom.md",
    root / "12_report_cpu.md",
    root / "15_report_deadlock.md",
    root / "16_README_answer.md",
    root / "17_README_answer.html",
    root / "03_diagram-viewer.html",
]
missing = []

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)

def check(doc, raw):
    parsed = urlparse(raw)
    if parsed.scheme or raw.startswith(("#", "mailto:", "javascript:", "data:")):
        return
    rel = unquote(parsed.path)
    if not rel:
        return
    target = (doc.parent / rel).resolve()
    if root not in target.parents and target != root:
        missing.append(f"{doc.name}: path escapes mission folder: {raw}")
    elif not target.exists():
        missing.append(f"{doc.name}: missing link target: {raw}")

for doc in docs:
    text = doc.read_text(encoding="utf-8")
    if doc.suffix == ".md":
        for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            check(doc, raw.split()[0])
    else:
        parser = LinkParser()
        parser.feed(text)
        for raw in parser.links:
            check(doc, raw)

answer_md = (root / "16_README_answer.md").read_text(encoding="utf-8")
question_count = len(re.findall(r"^### 질문 ", answer_md, flags=re.M))
related_count = answer_md.count("**관련 파일:**")
if question_count != related_count:
    missing.append(f"16_README_answer.md: questions={question_count}, related-links={related_count}")

answer_html = (root / "17_README_answer.html").read_text(encoding="utf-8")
card_count = answer_html.count('<article class="qcard">')
card_link_count = answer_html.count('<p class="related">')
if card_count != card_link_count:
    missing.append(f"17_README_answer.html: cards={card_count}, related-links={card_link_count}")

if missing:
    print("LINK CHECK: FAIL")
    for item in missing:
        print(f"  - {item}")
    raise SystemExit(1)
print(f"LINK CHECK: PASS ({question_count} Markdown questions, {card_count} HTML cards)")
PY

# 모든 검사 결과를 최종 PASS 또는 FAIL로 반환한다.
if (( fail )); then
  echo "FAIL: submission is incomplete."
  exit 1
fi
echo "PASS: numbered files, shell syntax, report sections, and local links are consistent."
