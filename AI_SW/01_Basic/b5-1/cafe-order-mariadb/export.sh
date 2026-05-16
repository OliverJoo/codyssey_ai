#!/bin/bash
# export.sh — MacBook(Apple Silicon)에서 실행
# 사용법: ./export.sh [USB경로 또는 출력디렉토리]
# 예시:  ./export.sh /Volumes/MyUSB
#        ./export.sh ./transfer

set -e

OUTPUT_DIR="${1:-.}"
BACKUP_FILE="cafe_order_db_backup.sql"
CONTAINER="cafe-mariadb-1182"
DB="cafe_order_db"
DB_USER="cafe_user"
DB_PASS="CafePass_1182"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 [1/3] MariaDB 덤프 생성 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p "$OUTPUT_DIR"

docker exec "$CONTAINER" \
  mariadb-dump -u "$DB_USER" -p"$DB_PASS" "$DB" \
  > "$OUTPUT_DIR/$BACKUP_FILE"

echo "✅ 덤프 완료: $OUTPUT_DIR/$BACKUP_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 [2/3] compose.yaml 복사 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# compose.yaml이 현재 디렉토리에 있다고 가정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/compose.yaml" "$OUTPUT_DIR/compose.yaml"

echo "✅ compose.yaml 복사 완료"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 [3/3] import.sh 생성 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > "$OUTPUT_DIR/import.sh" << 'IMPORT_EOF'
#!/bin/bash
# import.sh — 인텔 아이맥에서 실행
# 사용법: ./import.sh
# 이 파일과 같은 디렉토리에 compose.yaml, cafe_order_db_backup.sql 이 있어야 함

set -e

BACKUP_FILE="cafe_order_db_backup.sql"
CONTAINER="cafe-mariadb-1182"
DB="cafe_order_db"
DB_USER="cafe_user"
DB_PASS="CafePass_1182"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 [1/3] Docker Compose 시작..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$SCRIPT_DIR"
docker compose up -d

echo "⏳ MariaDB 초기화 대기 중 (15초)..."
sleep 15

# 실제로 DB가 준비될 때까지 최대 30초 추가 대기
echo "🔍 DB 연결 확인 중..."
for i in $(seq 1 10); do
  if docker exec "$CONTAINER" mariadb -u "$DB_USER" -p"$DB_PASS" -e "SELECT 1;" "$DB" > /dev/null 2>&1; then
    echo "✅ DB 준비 완료!"
    break
  fi
  echo "  대기 중... ($i/10)"
  sleep 3
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 [2/3] DB 복원 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker exec -i "$CONTAINER" \
  mariadb -u "$DB_USER" -p"$DB_PASS" "$DB" \
  < "$SCRIPT_DIR/$BACKUP_FILE"

echo "✅ DB 복원 완료"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔎 [3/3] 복원 결과 확인..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker exec "$CONTAINER" \
  mariadb -u "$DB_USER" -p"$DB_PASS" "$DB" \
  -e "SHOW TABLES;"

echo ""
echo "🎉 모든 작업 완료!"
echo "   접속: mysql -h 127.0.0.1 -P 3307 -u $DB_USER -p$DB_PASS $DB"
IMPORT_EOF

chmod +x "$OUTPUT_DIR/import.sh"
echo "✅ import.sh 생성 완료"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 전달 파일 목록:"
ls -lh "$OUTPUT_DIR/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "➡️  이 파일들을 USB 또는 GitHub에 올린 후"
echo "   인텔 아이맥에서: ./import.sh 실행"
