# AI/SW 개발 워크스테이션 구축 — 미션 수행 가이드

> **환경:** macOS (Apple Silicon / Intel) | OrbStack 또는 Docker Desktop | zsh

---

## 1. 미션 개요

- **미션명:** AI/SW 개발 워크스테이션 구축
- **목표:** 터미널(Linux CLI), Docker(컨테이너), Git/GitHub(버전 관리)를 직접 세팅하고, 재현 가능한 개발 환경을 구축한 뒤 GitHub Repository로 제출
- **범위:** macOS 터미널 기본 명령어 → 파일 권한 → Docker 설치·운영 → Dockerfile 빌드 → 포트 매핑 → 볼륨 영속성 → Git/GitHub 연동
- **환경 조건 (macOS):**
  - **서울캠퍼스 환경:** 시스템 보안 정책상 `sudo` 권한 제한이 있을 수 있으므로 **OrbStack** 활용
  - **개인 MacBook 환경:** Docker Desktop(`brew install --cask docker`) 또는 OrbStack(`brew install --cask orbstack`) 중 택일
  - macOS의 기본 쉘은 **zsh** (`/bin/zsh`)이며, 터미널 앱 또는 iTerm2 사용
- **제출 방식:** GitHub Repository 링크 제출, `README.md`에 모든 수행 로그·증거 포함

---

## 2. 전체 작업 순서

### 2-1. 환경 준비

#### [STEP 1] Homebrew 설치 확인 (macOS 패키지 관리자)

- **목적:** 이후 Docker, Git 등 도구를 `brew`로 설치하기 위한 사전 준비

```zsh
# Homebrew 설치 여부 확인
brew --version

# 미설치 시 설치 (공식 스크립트)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Apple Silicon(M1/M2/M3) Mac의 경우 PATH 추가
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

- **확인 방법:** `brew --version` 출력 예시: `Homebrew 4.x.x`
- **연결된 평가 질문:** 없음 (사전 준비 단계)

---

#### [STEP 2] Linux 기본 명령어 실습 및 프로젝트 디렉토리 구성

- **목적:** 터미널 조작 흔적을 남기고, 이후 실습에 사용할 작업 디렉토리를 생성한다.

```zsh
# 현재 위치 확인
pwd

# 숨김 파일 포함 목록 확인
ls -la

# 프로젝트 루트 디렉토리 생성
mkdir -p ~/dev-workstation/{app/site,docker,logs,scripts,docs}

# 디렉토리 이동
cd ~/dev-workstation

# 빈 파일 생성
touch README.md logs/terminal.log

# 파일 내용 확인
cat README.md

# 파일 복사
cp README.md docs/README.md.bak

# 파일 이름변경/이동
mv docs/README.md.bak docs/README_backup.md

# 파일 삭제 (⚠️ 복구 불가 주의)
rm docs/README_backup.md

# 최종 디렉토리 구조 확인
ls -la ~/dev-workstation
```

> ⚠️ **주의:** macOS에는 휴지통 경유 없이 `rm`으로 즉시 영구 삭제됩니다. `-rf` 옵션은 특히 신중하게 사용하세요. 실수 방지용으로 `trash` CLI 도구(`brew install trash`) 사용을 권장합니다.

- **확인 방법:** `ls -la ~/dev-workstation` 으로 디렉토리 구조 확인 후 출력 결과를 `README.md` 코드블록으로 기록
- **연결된 평가 질문:** `1-1`, `2-1`

---

#### [STEP 3] 파일 권한 실습 (macOS 동일 적용)

- **목적:** 파일 및 디렉토리에 대한 권한 변경 전/후를 확인하고 기록한다.

```zsh
# 실행 스크립트 파일 생성
touch ~/dev-workstation/scripts/run.sh

# 변경 전 권한 확인
ls -l ~/dev-workstation/scripts/run.sh
# 예상 출력: -rw-r--r--  (644)

# 파일 권한 변경: 644 → 755 (실행 권한 추가)
chmod 755 ~/dev-workstation/scripts/run.sh

# 변경 후 확인
ls -l ~/dev-workstation/scripts/run.sh
# 예상 출력: -rwxr-xr-x  (755)

# 디렉토리 권한 변경: 755 → 700 (소유자만 접근)
ls -ld ~/dev-workstation/logs/
chmod 700 ~/dev-workstation/logs/
ls -ld ~/dev-workstation/logs/
# 예상 출력: drwx------  (700)
```

- **확인 방법:** `ls -l` 출력에서 권한 문자열이 `-rwxr-xr-x` (755), `drwx------` (700)으로 변경됨을 확인
- **연결된 평가 질문:** `1-2`, `3-4`

---

#### [STEP 4] Docker 설치 및 점검 (macOS)

- **목적:** macOS에 Docker 실행 환경을 구성하고 `docker` 명령어 사용 가능 상태를 확인한다.

> **선택지:**
> - **개인 MacBook:** Docker Desktop 또는 OrbStack 중 택일
> - **서울캠퍼스 (sudo 제한):** OrbStack 권장

**옵션 A — OrbStack (권장, sudo 불필요)**

```zsh
# OrbStack 설치
brew install --cask orbstack

# OrbStack 실행 (GUI 앱 실행, 내부적으로 Docker 엔진 자동 구동)
open -a OrbStack
```

**옵션 B — Docker Desktop**

```zsh
# Docker Desktop 설치
brew install --cask docker

# Docker Desktop 실행
open -a Docker

# 상태바에 Docker 고래 아이콘이 나타나고 "Docker Desktop is running" 확인될 때까지 대기
```

**설치 후 공통 점검:**

```zsh
# Docker 버전 확인
docker --version
# 예상 출력: Docker version 26.x.x, build ...

# Docker 데몬 동작 여부 확인
docker info
# Server Version 항목이 출력되면 정상

# 간단한 동작 확인
docker ps
```

> ⚠️ **주의:** Docker Desktop/OrbStack이 실행 중이지 않으면 `docker` 명령어가 `Cannot connect to the Docker daemon` 오류를 반환합니다. 반드시 앱이 실행된 상태에서 명령어를 입력하세요.

- **확인 방법:** `docker --version` 및 `docker info`의 출력 결과를 `README.md`에 코드블록으로 기록
- **연결된 평가 질문:** `1-3`

---

### 2-2. Docker 기초 실습

#### [STEP 5] hello-world 실행 및 컨테이너·이미지 목록 확인

> **의존 관계:** STEP 4 완료 후 수행

- **목적:** Docker 기본 동작 확인, 이미지 다운로드·실행·목록 관리 흐름을 경험한다.

```zsh
# hello-world 컨테이너 실행
docker run hello-world

# 이미지 목록 확인
docker images

# ubuntu 이미지 다운로드
docker pull ubuntu

# ubuntu 컨테이너 실행 및 내부 진입
docker run -it --name ubuntu-test ubuntu bash

# 컨테이너 내부에서 명령 수행 (bash 프롬프트 상태)
ls
echo "hello from ubuntu container"
exit

# 전체 컨테이너 목록 (중지된 컨테이너 포함)
docker ps -a

# 컨테이너 로그 확인
docker logs ubuntu-test

# 리소스 모니터링 (Ctrl+C로 종료)
docker stats --no-stream

# 컨테이너 정리
docker rm ubuntu-test

# 미사용 이미지 정리 (dangling 이미지만 삭제)
docker image prune
```

> ⚠️ **주의:** `docker system prune -a`는 모든 중지 컨테이너와 태그 없는 이미지를 일괄 삭제합니다. 직접 빌드한 이미지가 있다면 반드시 `docker images`로 목록을 확인한 뒤 실행하세요.

- **확인 방법:** `docker run hello-world` 출력에 `Hello from Docker!` 문구 포함 확인 / `docker ps -a` 목록 캡처
- **연결된 평가 질문:** `1-4`, `1-5`

---

### 2-3. Dockerfile 빌드 및 포트 매핑

#### [STEP 6] 웹 서버 소스코드 및 Dockerfile 작성

> **의존 관계:** STEP 4 완료 후 수행

- **목적:** 커스텀 이미지의 기반이 될 정적 HTML 파일과 Dockerfile을 직접 작성한다.

```zsh
cd ~/dev-workstation/app
```

`app/site/index.html` 작성:

```zsh
cat <<'EOF' > site/index.html
<!DOCTYPE html>
<html lang="ko">
  <head><meta charset="UTF-8"><title>Dev Workstation</title></head>
  <body>
    <h1>Hello from my custom nginx!</h1>
    <p>macOS Docker 실습 환경</p>
  </body>
</html>
EOF
```

`app/Dockerfile` 작성 (옵션 A — nginx 베이스 활용):

```zsh
cat <<'EOF' > Dockerfile
FROM nginx:alpine
LABEL org.opencontainers.image.title="my-custom-nginx"
LABEL org.opencontainers.image.description="Custom nginx for dev-workstation mission"
ENV APP_ENV=dev
COPY site/ /usr/share/nginx/html/
EXPOSE 80
EOF
```

- **확인 방법:** `cat app/Dockerfile` 및 `cat app/site/index.html`로 내용 확인
- **연결된 평가 질문:** `1-6`, `2-1`

---

#### [STEP 7] 이미지 빌드 및 포트 매핑으로 컨테이너 실행

> **의존 관계:** STEP 6 완료 후 수행

- **목적:** Dockerfile로 커스텀 이미지를 빌드하고, 포트 매핑으로 macOS 호스트에서 접속을 확인한다.

```zsh
# app 디렉토리에서 이미지 빌드
cd ~/dev-workstation/app
docker build -t my-web:1.0 .

# 빌드된 이미지 확인
docker images | grep my-web

# 포트 매핑으로 컨테이너 실행 (호스트 8080 → 컨테이너 80)
docker run -d -p 8080:80 --name my-web-8080 my-web:1.0

# 실행 중인 컨테이너 확인
docker ps

# 터미널에서 접속 확인
curl http://localhost:8080

# 브라우저에서 접속 (macOS 전용)
open http://localhost:8080

# 두 번째 인스턴스 실행 (재현성 확인)
docker run -d -p 8081:80 --name my-web-8081 my-web:1.0
curl http://localhost:8081

# 컨테이너 로그 확인
docker logs my-web-8080
```

> ⚠️ **주의 (Apple Silicon):** `nginx:alpine` 이미지는 `linux/amd64` 기준 빌드입니다. M1/M2/M3 Mac에서 아키텍처 경고가 발생할 경우 빌드 시 `--platform linux/amd64` 옵션을 추가하거나, `FROM nginx:alpine` 그대로 사용해도 Docker가 자동으로 에뮬레이션하여 실행합니다.

- **확인 방법:** `curl http://localhost:8080` 응답에 `Hello from my custom nginx!` 출력 확인 / 브라우저 주소창(`localhost:8080`)과 응답 화면 스크린샷을 `README.md`에 첨부
- **연결된 평가 질문:** `1-6`, `1-7`, `2-2`

---

#### [STEP 8] 바인드 마운트 실습 (변경 반영 확인)

> **의존 관계:** STEP 7 완료 후 수행

- **목적:** 호스트 파일 변경이 컨테이너에 실시간으로 반영되는 바인드 마운트 동작을 확인한다.

```zsh
# 기존 컨테이너 중지 및 삭제
docker stop my-web-8080 my-web-8081
docker rm my-web-8080 my-web-8081

# 바인드 마운트로 컨테이너 실행 (macOS: $(pwd) 사용)
cd ~/dev-workstation/app
docker run -d -p 8080:80 \
  --name my-web-bind \
  -v $(pwd)/site:/usr/share/nginx/html \
  my-web:1.0

# 변경 전 접속 확인
curl http://localhost:8080

# 호스트에서 파일 수정 (컨테이너 재시작 없이 반영)
echo "<h1>Updated by bind mount on macOS!</h1>" > site/index.html

# 변경 후 접속 확인
curl http://localhost:8080

# 컨테이너 정리
docker stop my-web-bind && docker rm my-web-bind
```

- **확인 방법:** 변경 전/후 `curl` 응답이 다르게 나오면 바인드 마운트 정상 동작
- **연결된 평가 질문:** `1-8` (바인드 마운트 파트)

---

### 2-4. Docker 볼륨 실습

#### [STEP 9] Docker Named Volume 생성·연결·영속성 검증

> **의존 관계:** STEP 4 완료 후 수행 (STEP 8과 독립적으로 수행 가능)

- **목적:** Named Volume을 생성하고 컨테이너 삭제 후에도 데이터가 유지됨을 검증한다.

```zsh
# 볼륨 생성
docker volume create mydata

# 볼륨 목록 확인
docker volume ls

# 볼륨 상세 정보 확인 (macOS에서 Mountpoint 경로 확인)
docker volume inspect mydata

# 볼륨 연결하여 컨테이너 실행
docker run -d --name vol-test -v mydata:/data ubuntu sleep infinity

# 컨테이너 내부에서 데이터 기록
docker exec -it vol-test bash -c "echo 'persistent data test' > /data/hello.txt && cat /data/hello.txt"

# 컨테이너 강제 삭제 (⚠️ 강제 종료 후 삭제 — 볼륨은 유지됨)
docker rm -f vol-test

# 새 컨테이너를 동일 볼륨에 연결
docker run -d --name vol-test2 -v mydata:/data ubuntu sleep infinity

# 데이터 유지 확인
docker exec -it vol-test2 bash -c "cat /data/hello.txt"
# 예상 출력: persistent data test

# 정리 (⚠️ 볼륨 삭제는 영구 삭제 — 필요 시에만 실행)
docker rm -f vol-test2
# docker volume rm mydata   ← 과제 제출 전에는 실행하지 말 것
```

> ⚠️ **주의:** `docker rm -f`는 실행 중인 컨테이너를 강제 종료 후 삭제합니다. `docker volume rm`은 볼륨 데이터를 영구 삭제하므로 검증 완료 후에만 실행하세요.

- **확인 방법:** `vol-test2`에서 `cat /data/hello.txt` 결과가 `persistent data test`이면 영속성 검증 완료
- **연결된 평가 질문:** `1-8`, `4-2`

---

### 2-5. Git 설정 및 GitHub 연동

#### [STEP 10] Git 설치 확인 및 초기 설정

> **의존 관계:** 없음 (STEP 1과 병행 가능)

- **목적:** Git 사용자 정보와 기본 브랜치를 설정한다.

```zsh
# Git 버전 확인 (macOS Xcode Command Line Tools에 포함)
git --version

# 미설치 또는 최신 버전 필요 시
brew install git

# Git 사용자 정보 설정
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 기본 브랜치 이름 설정
git config --global init.defaultBranch main

# macOS 전용: .DS_Store 전역 무시 설정
git config --global core.excludesfile ~/.gitignore_global
echo ".DS_Store" >> ~/.gitignore_global

# 설정 전체 확인
git config --list
```

> ⚠️ **주의:** `git config --list` 출력에 개인 이메일이 포함됩니다. 스크린샷 첨부 시 마스킹 처리하세요.

- **확인 방법:** `git config --list`에서 `user.name`, `user.email`, `init.defaultBranch=main` 항목 확인
- **연결된 평가 질문:** `1-9`

---

#### [STEP 11] GitHub Repository 생성 및 프로젝트 연동

> **의존 관계:** STEP 10 완료 후 수행

- **목적:** 로컬 작업물을 GitHub에 push하고, VSCode와 GitHub를 연동한다.

```zsh
cd ~/dev-workstation

# .gitignore 생성 (민감정보 파일 제외)
cat <<'EOF' > .gitignore
*.env
*.key
*.pem
.DS_Store
.env.local
EOF

# Git 초기화
git init

# 첫 번째 커밋
git add .
git commit -m "feat: initial dev-workstation setup"

# GitHub에서 Repository 생성 후 원격 연결
# (GitHub 웹에서 New Repository 생성 → HTTPS URL 복사)
git remote add origin https://github.com/<your-username>/dev-workstation.git

# main 브랜치로 push
git branch -M main
git push -u origin main

# 연동 확인
git remote -v
git log --oneline
```

**VSCode GitHub 연동 (macOS):**

```zsh
# VSCode에서 프로젝트 열기
code ~/dev-workstation
```

1. VSCode 좌측 사이드바 → Source Control (⌃⇧G)
2. GitHub 계정 로그인 (`Sign in to GitHub`)
3. 저장소 연동 확인 후 스크린샷 캡처

> ⚠️ **주의:** GitHub 토큰, 비밀번호, SSH 개인키가 `README.md`나 로그에 노출되지 않도록 확인하세요. 의심 시 즉시 토큰을 재발급하세요.

- **확인 방법:** `git remote -v`에서 origin URL 확인 / GitHub 웹에서 파일 목록 확인 / VSCode 연동 스크린샷 첨부
- **연결된 평가 질문:** `1-9`

---

### 2-6. 프로젝트 디렉토리 구조 설계 및 재현 가능한 설정 정리

#### [STEP 12] README.md 최종 작성 및 GitHub push

> **의존 관계:** STEP 2~11 모두 완료 후 수행

- **목적:** 모든 수행 결과를 기술 문서에 기록하고, 평가자가 README만으로 동일 환경을 재현할 수 있도록 정리한다.

**README.md 필수 구성 항목 예시:**

```markdown
## 1) 실행 환경
- OS: macOS 14.x (Sonoma) / Apple Silicon M2
- Shell: zsh
- Docker: 26.x (OrbStack 기반)
- Git: 2.x

## 2) 디렉토리 구조
dev-workstation/
├── app/
│   ├── Dockerfile
│   └── site/
│       └── index.html
├── docker/
├── logs/
│   └── terminal.log
├── scripts/
│   └── run.sh
└── README.md

## 3) 수행 체크리스트
- [x] 터미널 기본 조작 및 폴더 구성
- [x] 권한 변경 실습 (파일 1개, 디렉토리 1개)
- [x] Docker 설치/점검 (OrbStack)
- [x] hello-world 실행
- [x] Dockerfile 빌드/실행
- [x] 포트 매핑 접속 (8080, 8081 두 인스턴스)
- [x] 바인드 마운트 변경 반영
- [x] 볼륨 영속성 (컨테이너 삭제 전/후 비교)
- [x] Git 설정 + VSCode GitHub 연동

## 4) 검증 방법 + 결과 증거
(각 항목마다 명령어 + 출력 코드블록 + 스크린샷 링크)

## 5) 트러블슈팅 2건
(문제 → 원인 가설 → 확인 → 해결/대안)
```

**최종 push:**

```zsh
cd ~/dev-workstation
git add README.md
git commit -m "docs: add final README with all evidence"
git push origin main
```

- **확인 방법:** GitHub Repository에서 README 렌더링 확인, 모든 스크린샷·링크 접근 가능 여부 확인
- **연결된 평가 질문:** `2-1`, `2-2`, `1-9`

---

## 3. 개념 설명 섹션

### 3-1. 이미지 vs 컨테이너 (빌드/실행/변경 관점)

| 구분 | 이미지 (Image) | 컨테이너 (Container) |
|---|---|---|
| **정의** | 실행 환경의 스냅샷 (읽기 전용 레이어) | 이미지를 기반으로 실행된 프로세스 인스턴스 |
| **빌드** | `docker build` 로 Dockerfile에서 생성 | `docker run` 으로 이미지를 바탕으로 생성 |
| **실행** | 실행 불가 (설계도 역할) | 실행 가능 (실제 동작하는 격리 환경) |
| **변경** | **변경 불가 (immutable)** — 재빌드 필요 | 내부 변경 가능 (쓰기 레이어 추가됨) — 단, 컨테이너 삭제 시 소멸 |
| **비유** | 붕어빵 틀 (레시피) | 틀로 구워낸 붕어빵 (실제 인스턴스) |

- **빌드 흐름:** `Dockerfile` → `docker build` → 이미지 (레이어 캐시 활용)
- **실행 흐름:** 이미지 → `docker run` → 컨테이너 (읽기 전용 이미지 레이어 + 쓰기 가능 레이어)
- **변경의 핵심:** 컨테이너 내부 변경은 해당 컨테이너에만 적용되며, 삭제 시 소멸됨. 영속화하려면 **볼륨/바인드 마운트** 사용

---

### 3-2. 포트 매핑이 필요한 이유

- **컨테이너는 독립된 네트워크 네임스페이스**를 가지므로, 컨테이너 내부 포트(nginx의 80번)는 macOS 호스트 네트워크와 완전히 분리됨
- `localhost:80`으로 직접 접속 시 컨테이너 내부로 라우팅되지 않음 → **접속 불가**
- `-p 8080:80` 옵션은 **"macOS 호스트의 8080 포트로 오는 요청을 컨테이너의 80 포트로 전달"** 하는 NAT 규칙을 생성함
- 이 구조 덕분에 같은 이미지로 여러 컨테이너를 실행하면서 각기 다른 호스트 포트(8080, 8081)로 분리 운영 가능 → **충돌 없이 다중 인스턴스 실행**

---

### 3-3. 절대 경로 vs 상대 경로 선택 기준

| 구분 | 절대 경로 | 상대 경로 |
|---|---|---|
| **형태** | `/Users/username/dev-workstation/app` | `../app` 또는 `./app` |
| **기준점** | 루트(`/`)에서 시작 | 현재 작업 디렉토리(`pwd`)에서 시작 |
| **macOS 예시** | `/Users/username/dev-workstation` | `~/dev-workstation` (홈 기준) |
| **사용 상황** | 스크립트·cron·launchd 등 실행 위치가 고정되지 않는 경우 | 터미널에서 현재 위치 기반 작업, 프로젝트 내부 참조 |
| **Dockerfile** | 비권장 (경로 하드코딩 문제) | `COPY ./site /usr/share/nginx/html` 권장 |

- **바인드 마운트 `-v` 옵션**에는 절대 경로 또는 `$(pwd)` 활용 필수 (상대 경로 미지원)
- **macOS 특이사항:** `~`는 쉘이 `/Users/username`으로 확장해주므로, 스크립트 내부에서는 `$HOME`을 사용하는 것이 안전

---

### 3-4. 파일 권한 숫자 표기 규칙 (755, 644 등)

권한은 **소유자(owner) / 그룹(group) / 기타(others)** 세 주체에 대해 각각 **r(4), w(2), x(1)** 세 권한의 합으로 표기합니다.

```
chmod 755 run.sh
   7 = 4+2+1 = rwx  (소유자: 읽기+쓰기+실행)
   5 = 4+0+1 = r-x  (그룹:  읽기+실행)
   5 = 4+0+1 = r-x  (기타:  읽기+실행)

chmod 644 config.txt
   6 = 4+2+0 = rw-  (소유자: 읽기+쓰기)
   4 = 4+0+0 = r--  (그룹:  읽기만)
   4 = 4+0+0 = r--  (기타:  읽기만)
```

- **755:** 실행 파일, 디렉토리에 사용 (누구나 접근·실행 가능, 소유자만 수정)
- **644:** 일반 설정·문서 파일에 사용 (소유자만 수정, 나머지는 읽기만)
- **700:** SSH 키, `.env` 등 민감 파일에 사용 (소유자만 접근)
- **macOS 확인법:** `ls -l` 또는 `stat -f "%Sp %p" 파일명`

---

## 4. 문제 해결 시나리오 섹션

### 4-1. 호스트 포트 충돌 진단 순서 (macOS)

`docker run -p 8080:80 ...` 실행 시 `Bind: address already in use` 오류 발생 시나리오:

1. **오류 메시지에서 충돌 포트 번호 확인**

```zsh
# 오류 예시
Error response from daemon: ... Bind for 0.0.0.0:8080 failed: port is already allocated
```

2. **macOS에서 포트 점유 프로세스 확인**

```zsh
# lsof로 포트 점유 확인 (macOS)
lsof -i :8080

# 또는
sudo lsof -iTCP:8080 -sTCP:LISTEN
```

3. **Docker 컨테이너가 점유 중인지 확인**

```zsh
docker ps | grep 8080
docker ps -a | grep 8080
```

4. **조치 A — 충돌 Docker 컨테이너 중지 후 재실행**

```zsh
docker stop <container_name>
docker run -p 8080:80 my-web:1.0
```

5. **조치 B — 다른 호스트 포트 사용**

```zsh
docker run -p 8090:80 my-web:1.0
open http://localhost:8090
```

6. **조치 C — 비-Docker 프로세스(예: macOS 내장 Apache) 종료**

```zsh
# PID 확인 후 종료
kill -9 <PID>

# macOS 내장 Apache 종료 (예시)
sudo apachectl stop
```

---

### 4-2. 컨테이너 삭제 후 데이터 유실 방지 방법

- **원인:** 컨테이너의 쓰기 레이어는 컨테이너 생명주기에 종속됨 → `docker rm` 시 소멸

- **대안 1 — Named Volume 사용 (가장 권장)**

```zsh
docker volume create mydata
docker run -v mydata:/data my-image
# 컨테이너 삭제 후에도 볼륨은 유지됨
```

- **대안 2 — 바인드 마운트 사용 (macOS 호스트 경로 직접 연결)**

```zsh
# macOS에서 절대 경로 또는 $(pwd) 사용 필수
docker run -v $(pwd)/data:/data my-image
# 호스트 파일시스템에 저장 → 컨테이너 삭제와 무관
```

- **대안 3 — `docker commit`** (비권장 — 재현성 낮음, Dockerfile 방식 우선)
- **핵심 원칙:** 영속화가 필요한 데이터는 **항상 컨테이너 외부(볼륨 또는 바인드 마운트)**에 저장

---

### 4-3. 가설 → 확인 → 조치 프레임 예시

**예시 트러블슈팅 1: `curl http://localhost:8080` 응답 없음**

| 단계 | 내용 |
|---|---|
| **문제** | 브라우저/curl 접속 시 `Connection refused` |
| **가설 1** | 컨테이너가 실행 중이지 않다 |
| **확인** | `docker ps` → STATUS 확인 |
| **조치** | `docker start my-web-8080` 또는 `docker run` 재실행 |
| **가설 2** | 포트 매핑이 잘못되었다 |
| **확인** | `docker inspect my-web-8080 \| grep -A5 Ports` |
| **조치** | `-p 8080:80` 옵션 확인 후 컨테이너 재생성 |

**예시 트러블슈팅 2: `docker build` 실패 — `COPY failed: no such file or directory`**

| 단계 | 내용 |
|---|---|
| **문제** | `COPY site/ /usr/share/nginx/html/` 에서 오류 |
| **가설** | `docker build` 실행 위치가 `site/` 폴더를 포함하지 않는다 |
| **확인** | `pwd` 및 `ls site/` 로 빌드 컨텍스트 경로 확인 |
| **조치** | `cd ~/dev-workstation/app` 이동 후 `docker build -t my-web:1.0 .` 재실행 |

**예시 트러블슈팅 3 (macOS 특이사항): Apple Silicon에서 이미지 호환성 경고**

| 단계 | 내용 |
|---|---|
| **문제** | `WARNING: The requested image's platform (linux/amd64) does not match...` |
| **가설** | 빌드된 이미지와 호스트 아키텍처(arm64) 불일치 |
| **확인** | `docker inspect my-web:1.0 \| grep Architecture` |
| **조치** | `docker build --platform linux/amd64 -t my-web:1.0 .` 또는 `FROM nginx:alpine` 그대로 사용(OrbStack/Docker Desktop이 자동 에뮬레이션) |

---

## 5. 평가 질문 매핑표

| 평가 질문 번호 | 질문 요약 | 대응 단계 | 확인 방법 |
|---|---|---|---|
| **1-1** | 폴더/파일 생성·이동·삭제 흔적 | STEP 2 | `ls -la` 출력, README 코드블록 |
| **1-2** | 파일 권한 변경 결과 확인 | STEP 3 | `ls -l` 변경 전/후 비교 캡처 |
| **1-3** | `docker --version` 출력 및 동작 상태 | STEP 4 | `docker --version`, `docker info` 출력 기록 |
| **1-4** | `docker run hello-world` 정상 실행 | STEP 5 | `Hello from Docker!` 문구 포함 출력 확인 |
| **1-5** | 이미지/컨테이너 목록 확인 및 정리 흔적 | STEP 5 | `docker images`, `docker ps -a`, `docker rm` 출력 |
| **1-6** | Dockerfile로 이미지 빌드 가능 | STEP 6, 7 | `docker build` 성공, `docker images` 목록 확인 |
| **1-7** | 매핑된 포트로 접속 가능 | STEP 7 | `curl http://localhost:8080` 응답, 브라우저 스크린샷 |
| **1-8** | 볼륨 데이터 컨테이너 삭제 후 유지 | STEP 8, 9 | `vol-test2`에서 `cat /data/hello.txt` 동일 출력 확인 |
| **1-9** | Git 설정 및 GitHub 연동 확인 | STEP 10, 11 | `git config --list`, `git remote -v`, VSCode 스크린샷 |
| **2-1** | 프로젝트 디렉토리 구조 설명 능력 | STEP 2, 12 | README 디렉토리 트리 섹션 |
| **2-2** | 포트/볼륨 설정 재현 가능하게 정리 | STEP 7, 9, 12 | README 검증 방법 섹션 + 명령어 코드블록 |
| **3-1** | 이미지 vs 컨테이너 (빌드/실행/변경) | 개념 설명 3-1 | 빌드·실행·변경 관점 표 참조 |
| **3-2** | 컨테이너 포트 직접 접속 불가 이유 | 개념 설명 3-2 | 네트워크 네임스페이스 격리 설명 |
| **3-3** | 절대 경로/상대 경로 선택 기준 | 개념 설명 3-3 | 상황별 비교 표 참조 |
| **3-4** | 파일 권한 숫자 표기 규칙 | 개념 설명 3-4, STEP 3 | r=4, w=2, x=1 합산 규칙 |
| **4-1** | 호스트 포트 충돌 시 진단 순서 | 문제 해결 4-1 | `lsof -i :8080`, `docker ps`, `kill` 순서 |
| **4-2** | 컨테이너 삭제 후 데이터 유실 방지 | STEP 9, 문제 해결 4-2 | Named Volume / 바인드 마운트 대안 |
| **4-3** | 가장 어려웠던 지점 + 가설→확인→조치 | 문제 해결 4-3, STEP 12 | README 트러블슈팅 2건 이상 기록 |
