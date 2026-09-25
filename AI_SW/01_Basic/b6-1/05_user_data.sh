#!/usr/bin/env bash
# EC2 최초 부팅 때 Nginx와 /health 응답을 구성한다.
set -Eeuo pipefail

# 배포판에 맞는 패키지 관리자로 Nginx를 설치한다.
if command -v dnf >/dev/null 2>&1; then
  # Amazon Linux 2023에는 curl-minimal이 기본 설치되어 있으므로 일반 curl을
  # 함께 설치하면 패키지 충돌이 발생할 수 있다.
  dnf install -y nginx
elif command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y nginx curl
else
  echo "지원하지 않는 Linux 배포판입니다." >&2
  exit 1
fi

# Amazon Linux와 Ubuntu의 기본 document root 모두에 동일한 파일을 둔다.
# 04 스크립트는 web/index.html을 base64로 전달한다. 로컬 단독 실행 때는
# 같은 디렉터리의 원본을 사용하고, 둘 다 없을 때만 최소 fallback을 사용한다.
PAGE_FILE="$(mktemp)"
if [[ -n "${CODYSSEY_PAGE_BASE64:-}" ]]; then
  printf '%s' "$CODYSSEY_PAGE_BASE64" | base64 --decode > "$PAGE_FILE"
elif [[ -r "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/web/index.html" ]]; then
  cp "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/web/index.html" "$PAGE_FILE"
else
  cat > "$PAGE_FILE" <<'HTML'
<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Codyssey b6-1</title></head>
<body><h1>Hello Cloud</h1><p>Codyssey b6-1 web service is running.</p></body>
</html>
HTML
fi
for web_root in /usr/share/nginx/html /var/www/html; do
  mkdir -p "$web_root"
  cp "$PAGE_FILE" "$web_root/index.html"
  printf 'OK\n' > "$web_root/health"
done
rm -f "$PAGE_FILE"

# 이전 버전의 커스텀 server block이 있으면 기본 설정과의 충돌을 막기 위해 제거한다.
rm -f /etc/nginx/conf.d/codyssey.conf

# 설정 문법을 확인한 뒤 부팅 시 자동 시작한다.
nginx -t
systemctl enable --now nginx
curl --fail --silent http://localhost/health
touch /var/lib/codyssey-b6-1-ready
