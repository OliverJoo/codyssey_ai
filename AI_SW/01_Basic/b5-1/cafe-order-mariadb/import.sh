#!/bin/bash
# import.sh — DB를 받을 머신에서 실행 (어느 아키텍처든 무관)
# 사용법: ./import.sh
# compose.yaml, *_backup.sql 파일이 같은 폴더에 있어야 함

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

# 백업 파일 존재 확인
if [ ! -f "$SCRIPT_DIR/$BACKUP_FILE" ]; then
  echo "❌ 백업 파일을 찾을 수 없습니다: $SCRIPT_DIR/$BACKUP_FILE"
  exit 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [1/3] Docker Compose 시작
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "🐳 [1/3] Docker Compose 시작..."

cd "$SCRIPT_DIR"
docker compose up -d

echo "⏳ MariaDB 초기화 대기 중 (15초)..."
sleep 15

echo "🔍 DB 연결 확인 중..."
for i in $(seq 1 10); do
  if docker exec "$CONTAINER" mariadb -u "$DB_USER" -p"$DB_PASS" -e "SELECT 1;" "$DB" > /dev/null 2>&1; then
    echo "✅ DB 준비 완료!"
    break
  fi
  if [ "$i" -eq 10 ]; then
    echo "❌ DB 연결 실패. compose.yaml 설정을 확인하세요."
    exit 1
  fi
  echo "  대기 중... ($i/10)"
  sleep 3
done

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [2/3] DB 복원
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "💾 [2/3] DB 복원 중..."

docker exec -i "$CONTAINER" \
  mariadb -u "$DB_USER" -p"$DB_PASS" "$DB" \
  < "$SCRIPT_DIR/$BACKUP_FILE"

echo "✅ DB 복원 완료"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [3/3] 결과 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "🔎 [3/3] 복원 결과 확인..."

docker exec "$CONTAINER" \
  mariadb -u "$DB_USER" -p"$DB_PASS" "$DB" \
  -e "SHOW TABLES;"

echo ""
echo "🎉 완료!"
echo "   접속: mysql -h 127.0.0.1 -P 3307 -u $DB_USER -p$DB_PASS $DB"
