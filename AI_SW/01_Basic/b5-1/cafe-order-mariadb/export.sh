#!/bin/bash
# export.sh — DB를 내보낼 머신에서 실행 (어느 아키텍처든 무관)
# 사용법: ./export.sh [출력디렉토리]
#        ./export.sh /Volumes/MyUSB
#        ./export.sh          (인자 없으면 현재 폴더)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${1:-.}"
COMPOSE_FILE="$SCRIPT_DIR/compose.yaml"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# compose.yaml 파싱
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "❌ compose.yaml 파일을 찾을 수 없습니다: $COMPOSE_FILE"
  exit 1
fi

CONTAINER=$(grep 'container_name:' "$COMPOSE_FILE" | head -1 | awk '{print $2}')
DB=$(grep 'MARIADB_DATABASE:' "$COMPOSE_FILE" | head -1 | awk '{print $2}')
DB_USER=$(grep 'MARIADB_USER:' "$COMPOSE_FILE" | head -1 | awk '{print $2}')
DB_PASS=$(grep 'MARIADB_PASSWORD:' "$COMPOSE_FILE" | head -1 | awk '{print $2}')
BACKUP_FILE="${DB}_backup.sql"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 compose.yaml 파싱 결과:"
echo "   CONTAINER : $CONTAINER"
echo "   DATABASE  : $DB"
echo "   USER      : $DB_USER"
echo "   BACKUP    : $BACKUP_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [0/3] Docker 데몬 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "🔍 [0/3] Docker 데몬 확인 중..."

if ! docker info > /dev/null 2>&1; then
  echo "⚠️  Docker가 실행 중이 아닙니다. Docker Desktop 시작 중..."
  open -a Docker

  for i in $(seq 1 30); do
    if docker info > /dev/null 2>&1; then
      echo "✅ Docker 데몬 준비 완료!"
      break
    fi
    if [ "$i" -eq 30 ]; then
      echo "❌ Docker 데몬 시작 실패. Docker Desktop을 수동으로 실행 후 다시 시도하세요."
      exit 1
    fi
    echo "  대기 중... ($i/30)"
    sleep 3
  done
else
  echo "✅ Docker 데몬 실행 중"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [1/3] 컨테이너 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "🐳 [1/3] 컨테이너 확인 중..."

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  echo "⚠️  컨테이너($CONTAINER)가 실행 중이 아닙니다. 시작 중..."
  cd "$SCRIPT_DIR"
  docker compose up -d

  echo "⏳ MariaDB 초기화 대기 중 (15초)..."
  sleep 15

  for i in $(seq 1 10); do
    if docker exec "$CONTAINER" mariadb -u "$DB_USER" -p"$DB_PASS" -e "SELECT 1;" "$DB" > /dev/null 2>&1; then
      echo "✅ 컨테이너 준비 완료!"
      break
    fi
    if [ "$i" -eq 10 ]; then
      echo "❌ 컨테이너 시작 실패. compose.yaml 설정을 확인하세요."
      exit 1
    fi
    echo "  대기 중... ($i/10)"
    sleep 3
  done
else
  echo "✅ 컨테이너 실행 중"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [2/3] 덤프 생성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "📦 [2/3] MariaDB 덤프 생성 중..."

mkdir -p "$OUTPUT_DIR"

docker exec "$CONTAINER" \
  mariadb-dump -u "$DB_USER" -p"$DB_PASS" "$DB" \
  > "$OUTPUT_DIR/$BACKUP_FILE"

echo "✅ 덤프 완료: $OUTPUT_DIR/$BACKUP_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [3/3] 파일 패키징 (USB/외부 폴더일 때만)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "📋 [3/3] 파일 패키징 중..."

if [ "$(realpath "$OUTPUT_DIR")" != "$(realpath "$SCRIPT_DIR")" ]; then
  cp "$SCRIPT_DIR/compose.yaml" "$OUTPUT_DIR/compose.yaml"
  cp "$SCRIPT_DIR/import.sh"   "$OUTPUT_DIR/import.sh"
  chmod +x "$OUTPUT_DIR/import.sh"
  echo "✅ compose.yaml, import.sh 복사 완료"
else
  echo "✅ 현재 폴더 출력 — 복사 생략"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 전달 파일 목록:"
ls -lh "$OUTPUT_DIR/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "➡️  GitHub push 또는 USB 전달 후"
echo "   대상 머신에서: chmod +x import.sh && ./import.sh"
