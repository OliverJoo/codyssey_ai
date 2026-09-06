#!/usr/bin/env bash
set -Eeuo pipefail

# macOS에서 Docker 호환 엔진으로 전체 미션을 실행하는 단일 진입점이다.
root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mode=${1:-all}
image=${B1_2_IMAGE:-ubuntu:22.04}
session="b1-2-$$"

usage() {
  cat <<'USAGE'
Usage: ./06_run_mission.sh [all|quick|CASE]

  all    Run all six Before/After experiments (default, about 2 minutes)
  quick  Run one 15-second smoke test
  CASE   Run one case accepted by 05_run_case.sh

Requires a Docker-compatible command: Docker Desktop, OrbStack, or Colima.
Every container is labeled, stopped, and removed automatically.
USAGE
}

# Docker Desktop·OrbStack·Colima 중 하나가 준비됐는지 확인한다.
command -v docker >/dev/null 2>&1 || {
  echo "ERROR: docker command not found. See 01_README.md environment setup." >&2
  exit 1
}
docker info >/dev/null 2>&1 || {
  echo "ERROR: Docker daemon is not running. Start Docker Desktop, OrbStack, or Colima." >&2
  exit 1
}

# Mac CPU에 맞는 Linux 플랫폼과 제공 바이너리를 자동 선택한다.
case "$(uname -m)" in
  arm64|aarch64) platform=linux/arm64 ;;
  x86_64|amd64) platform=linux/amd64 ;;
  *) echo "ERROR: unsupported Mac architecture: $(uname -m)" >&2; exit 1 ;;
esac

# 현재 실행이 만든 라벨의 컨테이너만 찾아 안전하게 정리한다.
cleanup() {
  ids=$(docker ps -aq --filter "label=codyssey.b1-2.session=$session")
  if [[ -n $ids ]]; then
    docker rm -f $ids >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

# 케이스 하나를 비-root 컨테이너에서 실행하고 번호형 로그로 저장한다.
run_one() {
  local case_name=$1
  local evidence_name
  case "$case_name" in
    oom-before) evidence_name=07_evidence_oom-before.log ;;
    oom-after) evidence_name=08_evidence_oom-after.log ;;
    cpu-before) evidence_name=10_evidence_cpu-before.log ;;
    cpu-after) evidence_name=11_evidence_cpu-after.log ;;
    deadlock-before) evidence_name=13_evidence_deadlock-before.log ;;
    deadlock-after) evidence_name=14_evidence_deadlock-after.log ;;
  esac
  local output="$root_dir/$evidence_name"
  local container="codyssey-${session}-${case_name}"
  echo "[$case_name] starting on $platform"
  # 호스트 포트는 열지 않고 CPU 1개·메모리 1GB로 격리한다.
  docker run --rm \
    --name "$container" \
    --label "codyssey.b1-2.session=$session" \
    --platform "$platform" \
    --memory 1g \
    --cpus 1 \
    --volume "$root_dir:/mission:ro" \
    "$image" bash -lc \
      "useradd -m -s /bin/bash learner && runuser -u learner -- bash /mission/05_run_case.sh '$case_name'" \
    | tee "$output"
  echo "[$case_name] evidence saved: $output"
}

# all·quick·개별 케이스 중 실행 목록을 만든다.
case "$mode" in
  -h|--help) usage; exit 0 ;;
  all)
    cases=(oom-before oom-after cpu-before cpu-after deadlock-before deadlock-after)
    ;;
  quick)
    cases=(oom-before)
    ;;
  oom-before|oom-after|cpu-before|cpu-after|deadlock-before|deadlock-after)
    cases=("$mode")
    ;;
  *) echo "ERROR: unknown mode: $mode" >&2; usage; exit 2 ;;
esac

# 선택한 케이스를 순서대로 실행한다.
for case_name in "${cases[@]}"; do
  run_one "$case_name"
done

# 종료 전에 잔여 컨테이너가 없는지 한 번 더 검증한다.
cleanup
remaining=$(docker ps -aq --filter "label=codyssey.b1-2.session=$session")
[[ -z $remaining ]] || { echo "ERROR: test container cleanup failed" >&2; exit 1; }
echo "DONE: ${#cases[@]} experiment(s) completed; test containers removed."
