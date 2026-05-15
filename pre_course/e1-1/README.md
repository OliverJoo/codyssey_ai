# codyssey_ai

 ## 1. 미션 개요 정리

### 1-1. 미션 목표
- Linux 기본 명령어를 사용해 **폴더/파일 생성·이동·삭제**를 수행하고, 그 흔적을 남긴다.
- 파일/디렉토리 권한을 변경하고, **변경 전후 결과를 확인**한다.
- Docker가 정상 동작하는지 확인하고, `hello-world` 실행 및 컨테이너 기본 조작을 수행한다.
- Dockerfile로 커스텀 이미지를 빌드하고, **포트 매핑을 통해 브라우저 접속**을 검증한다.
- Bind Mount / Volume을 사용해 **호스트-컨테이너 연동**과 **데이터 영속성**을 검증한다.
- Git 설정, GitHub 저장소 연동, VSCode GitHub 로그인 상태를 확인한다.
- 최종적으로, 작업 과정을 README 기준으로 **재현 가능하게 문서화**한다.

### 1-2. 범위
- **2-1. 환경 준비**
- **2-2. Docker 기초 실습**
- **2-3. Dockerfile 빌드 및 포트 매핑**
- **2-4. Docker 볼륨 실습**
- **2-5. Git 설정 및 GitHub 연동**
- **2-6. 프로젝트 디렉토리 구조 설계 및 재현 가능한 설정 정리**

### 1-3. 실습 환경
| 항목 | 값 |
|---|---|
| OS | [직접 입력: 예) macOS Sequoia 15.3.1] |
| Shell | [직접 입력: 예) /bin/zsh] |
| Terminal | [직접 입력: 예) iTerm2 / Terminal.app] |
| Docker Runtime | [직접 입력: 예) OrbStack / Docker Desktop] |
| Docker Version | [실행 결과 붙여넣기] |
| Git Version | [실행 결과 붙여넣기] |
| VSCode Version | [직접 입력] |

### 1-4. 사전 확인
- 첨부파일의 미션 목표와 범위를 확인했다.
- 첨부파일의 요구 항목과 평가 질문 전체가 작업 순서 안에 연결되도록 설계했다.
- 명령어는 **macOS 기준**으로 작성했다.
- **보너스 과제는 제외**했다.

---

## 2. 전체 작업 순서

---

### 2-1. 환경 준비

#### 단계 1. 작업 루트 및 증거 수집 구조 생성
- **목적**
  - 실습 파일, 로그, 스크린샷, Docker 관련 파일을 한 저장소 아래로 모아 재현성을 확보한다.

- **의존 관계**
  - 없음

- **실행 전 요약**
  - 홈 디렉토리 아래 실습 루트를 만들고, 로그/스크린샷/소스/임시 작업 폴더를 분리한다.

- **명령어 또는 절차**
```bash
cd ~
mkdir -p ~/dev/codyssey-mission-01/{app,docker,docs/logs,docs/screenshots,bind-site,tmp}
cd ~/dev/codyssey-mission-01
pwd
ls -la
touch README.md
```

- **로그 기록용 권장 절차**
```bash
script -aq docs/logs/01-session.txt
# 작업 종료 후
exit
```

- **확인 방법**
```bash
pwd
find . -maxdepth 2 | sort
```
- `app/`, `docker/`, `docs/logs/`, `docs/screenshots/`, `bind-site/`, `tmp/`, `README.md` 가 보이면 정상 완료.

- **주의 사항**
  - `script` 로그를 사용할 경우, GitHub 인증 직전에는 종료해 민감정보 노출을 방지한다.

- **연결된 평가 질문**
  - 프로젝트 디렉토리 구조를 어떤 기준으로 구성했는지 설명할 수 있는가?
  - 포트/볼륨 설정을 어떤 방식으로 재현 가능하게 정리했는지 설명할 수 있는가?

---

#### 단계 2. macOS 도구 설치 및 런타임 기동
- **목적**
  - Git, Docker CLI, Docker 런타임, VSCode 환경을 준비한다.

- **의존 관계**
  - 1단계 완료 후

- **실행 전 요약**
  - macOS에서는 CLI 설치와 런타임 기동을 구분해야 한다. Docker 런타임은 **OrbStack 또는 Docker Desktop 중 하나만** 사용한다.

- **명령어 또는 절차**
```bash
brew --version
brew update
brew install git
brew install docker

# 권장: OrbStack
brew install --cask orbstack
open -a OrbStack

# 대체: Docker Desktop
# brew install --cask docker
# open -a Docker

sw_vers
uname -m
echo $SHELL
echo $TERM_PROGRAM
git --version
docker --version
```

- **확인 방법**
```bash
which git
which docker
docker --version
git --version
```
- `docker --version` 출력이 보여야 한다.
- OrbStack 또는 Docker Desktop이 **실행 중** 상태여야 한다.

- **주의 사항**
  - OrbStack과 Docker Desktop을 동시에 실행하지 않는다.
  - `brew install docker` 는 CLI 설치이며, 실제 컨테이너 실행을 위해서는 런타임이 올라와 있어야 한다.

- **연결된 평가 질문**
  - `docker --version`이 출력되고, Docker가 동작 가능한 상태인가?
  - Git 설정 및 GitHub 연동이 확인되는가?

---

#### 단계 3. Linux 기본 명령어 실습 로그 남기기
- **목적**
  - CLI로 폴더/파일 생성, 이동, 복사, 삭제 흔적을 남긴다.

- **의존 관계**
  - 1, 2단계 완료 후

- **실행 전 요약**
  - 평가자는 “CLI를 실제로 다뤘는가”를 먼저 본다. 따라서 명령어와 출력 결과를 함께 남긴다.

- **명령어 또는 절차**
```bash
cd ~/dev/codyssey-mission-01
pwd
ls -la

mkdir -p practice/dir-a practice/dir-b
cd practice
pwd
cd ..

touch practice/empty.txt
echo "hello mission" > practice/note.txt
cat practice/note.txt

cp practice/note.txt practice/note-copy.txt
mv practice/note-copy.txt practice/dir-a/note-renamed.txt
mv practice/dir-a/note-renamed.txt practice/dir-b/

ls -la practice
ls -la practice/dir-b

rm practice/empty.txt
rm practice/dir-b/note-renamed.txt
rmdir practice/dir-a practice/dir-b

ls -la practice
```

- **확인 방법**
  - 로그에 아래 명령어 흔적이 모두 남아야 한다.
    - `pwd`
    - `ls -la`
    - `mkdir`
    - `touch`
    - `cat`
    - `cp`
    - `mv`
    - `rm`
    - `rmdir`

- **주의 사항**
  - `rm` 실행 전, 현재 경로와 대상 파일명을 다시 확인한다.

- **연결된 평가 질문**
  - 터미널에서 기본 명령어로 폴더/파일 생성·이동·삭제를 수행한 흔적이 있는가?
  - 절대 경로/상대 경로를 어떤 상황에서 선택하는지 설명할 수 있는가?

---

#### 단계 4. 파일/디렉토리 권한 변경 실습
- **목적**
  - 파일 1개, 디렉토리 1개에 대해 권한 변경 전후를 확인한다.

- **의존 관계**
  - 3단계 완료 후

- **실행 전 요약**
  - `chmod` 자체보다 중요한 것은 **변경 전/후의 `ls -l` 결과**를 남기는 것이다.

- **명령어 또는 절차**
```bash
cd ~/dev/codyssey-mission-01

mkdir -p permissions-demo/dir-sample
touch permissions-demo/file-sample.txt

cat > permissions-demo/run.sh <<'EOF'
#!/bin/bash
echo permission-ok
EOF

ls -ld permissions-demo/dir-sample
ls -l permissions-demo

chmod 700 permissions-demo/dir-sample
chmod 644 permissions-demo/file-sample.txt
chmod 755 permissions-demo/run.sh

ls -ld permissions-demo/dir-sample
ls -l permissions-demo

./permissions-demo/run.sh
```

- **확인 방법**
```bash
ls -ld permissions-demo/dir-sample
ls -l permissions-demo
```
- `dir-sample` 권한 변경 전/후 비교
- `file-sample.txt` 가 `-rw-r--r--` 형태인지 확인
- `run.sh` 가 `-rwxr-xr-x` 형태인지 확인
- `./permissions-demo/run.sh` 실행 결과가 출력되면 정상

- **주의 사항**
  - 디렉토리의 `x` 권한은 실행보다는 **진입/탐색 가능 여부**에 가깝다.

- **연결된 평가 질문**
  - 파일 권한 변경 결과가 확인되는가?
  - 파일 권한 숫자 표기(예: 755, 644)가 어떤 규칙으로 결정되는지 설명할 수 있는가?

---

### 2-2. Docker 기초 실습

#### 단계 5. Docker 설치 및 데몬 점검
- **목적**
  - Docker CLI와 Docker 엔진이 실제로 통신 가능한 상태인지 확인한다.

- **의존 관계**
  - 2단계 완료 후

- **실행 전 요약**
  - `docker --version` 만으로는 부족하다. 반드시 `docker info` 로 엔진 상태를 확인한다.

- **명령어 또는 절차**
```bash
docker --version
docker version
docker info
docker context ls
```

- **확인 방법**
- `docker --version` 출력 확인
- `docker info` 에 **Client / Server 정보**가 보이면 정상
- `docker context ls` 결과가 출력되면 컨텍스트 정상

- **주의 사항**
  - `Cannot connect to the Docker daemon` 오류가 나면 런타임이 기동되지 않은 상태다.

- **연결된 평가 질문**
  - `docker --version`이 출력되고, Docker가 동작 가능한 상태인가?

---

#### 단계 6. hello-world 및 Ubuntu 컨테이너 실행
- **목적**
  - Docker가 컨테이너를 pull/run 할 수 있는지 확인하고, `exec` / `attach` 차이를 관찰한다.

- **의존 관계**
  - 5단계 완료 후

- **실행 전 요약**
  - `hello-world` 는 가장 빠른 성공 검증이고, `ubuntu` 는 내부 진입과 라이프사이클 관찰에 적합하다.

- **명령어 또는 절차**
```bash
docker run --name hello-mission hello-world
docker ps -a
docker logs hello-mission

docker run -dit --name ubuntu-shell ubuntu bash
docker exec -it ubuntu-shell bash -lc "echo exec-shell-ok && ls / | head"

docker attach ubuntu-shell
# 컨테이너 내부에서 아래 실행
echo attach-shell-ok
exit

docker ps -a
docker start ubuntu-shell
docker exec -it ubuntu-shell bash -lc "echo restarted-ok"
```

- **확인 방법**
- `Hello from Docker!` 출력 확인
- `docker ps -a` 에 `hello-mission`, `ubuntu-shell` 기록 확인
- `exec-shell-ok`, `attach-shell-ok`, `restarted-ok` 출력 기록 확인

- **주의 사항**
  - `attach` 로 붙은 메인 프로세스에서 `exit` 하면 컨테이너가 종료된다.
  - `docker exec` 는 보조 프로세스 실행이므로 원래 컨테이너와 동작 의미가 다르다.

- **연결된 평가 질문**
  - `docker run hello-world`가 정상 실행되는가?
  - 이미지와 컨테이너의 차이를 "빌드/실행/변경" 관점에서 구분해 설명할 수 있는가?

---

#### 단계 7. 이미지/컨테이너 목록, 로그, 리소스, 정리
- **목적**
  - 운영 명령과 정리 흔적을 남긴다.

- **의존 관계**
  - 6단계 완료 후

- **실행 전 요약**
  - 조회 → 상태 확인 → 정리까지 있어야 운영 흐름이 완성된다.

- **명령어 또는 절차**
```bash
docker start ubuntu-shell

docker images
docker ps
docker ps -a
docker logs hello-mission
docker stats --no-stream ubuntu-shell

docker stop ubuntu-shell
docker rm hello-mission ubuntu-shell
docker ps -a
```

- **확인 방법**
- `docker images` 에 다운로드/빌드된 이미지 목록 확인
- `docker ps` / `docker ps -a` 차이 설명 가능 여부 확인
- `docker stats --no-stream` 결과 확인
- `docker rm` 이후 컨테이너가 목록에서 제거되었는지 확인

- **주의 사항**
  - 삭제 전 필요한 로그와 스크린샷을 먼저 확보한다.

- **연결된 평가 질문**
  - 이미지/컨테이너 목록 확인 및 정리 흔적이 있는가?
  - 컨테이너 삭제 후 데이터가 사라진 경험이 있다면, 이를 방지하기 위한 대안을 설명할 수 있는가?

---

### 2-3. Dockerfile 빌드 및 포트 매핑

#### 단계 8. 웹 서버 소스 및 Dockerfile 작성
- **목적**
  - NGINX 베이스 이미지를 활용한 정적 웹 서버 커스텀 이미지를 준비한다.

- **의존 관계**
  - 1단계 완료 후

- **실행 전 요약**
  - 평가 목적상 가장 안정적인 방식은 **NGINX + 정적 HTML** 조합이다.

- **명령어 또는 절차**
```bash
cd ~/dev/codyssey-mission-01

cat > app/index.html <<'EOF'
<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mission Web</title>
</head>
<body>
  <h1>Mission Web Server OK</h1>
  <p>custom nginx image build success</p>
</body>
</html>
EOF

cat > docker/Dockerfile <<'EOF'
FROM nginx:alpine
LABEL org.opencontainers.image.title="codyssey-mission-web"
ENV APP_ENV=dev
COPY app/ /usr/share/nginx/html/
EXPOSE 80
HEALTHCHECK CMD wget -q -O - http://localhost:80/ || exit 1
EOF
```

- **확인 방법**
```bash
cat docker/Dockerfile
cat app/index.html
```
- `FROM`, `COPY`, `EXPOSE` 포함 여부 확인
- Dockerfile의 커스텀 포인트를 README에 설명

- **주의 사항**
  - 단순 복붙보다, 파일명/문구/포트는 본인 실습 기준으로 정리한다.

- **연결된 평가 질문**
  - Dockerfile로 이미지 빌드가 가능한가?
  - 이미지와 컨테이너의 차이를 "빌드/실행/변경" 관점에서 구분해 설명할 수 있는가?

---

#### 단계 9. 커스텀 이미지 빌드 및 포트 매핑 실행
- **목적**
  - Dockerfile로 이미지를 빌드하고, 호스트 포트를 통해 웹 서버에 접속한다.

- **의존 관계**
  - 8단계 완료 후

- **실행 전 요약**
  - 내부 포트 80을 쓰더라도 외부 접속을 위해서는 `-p` 설정이 필요하다.

- **명령어 또는 절차**
```bash
cd ~/dev/codyssey-mission-01

docker build -f docker/Dockerfile -t codyssey-mission-web:1.0 .
docker run -d --name mission-web -p 8080:80 codyssey-mission-web:1.0

docker ps
curl http://localhost:8080
docker logs mission-web
open http://localhost:8080
```

- **확인 방법**
- `docker build` 성공 로그 확인
- `docker ps` 에 `8080->80` 포트 매핑 표시 확인
- `curl http://localhost:8080` 응답 확인
- 브라우저 접속 스크린샷 저장

- **주의 사항**
  - 8080 포트 충돌 시 `8081:80` 으로 변경하고, README에 변경 이유를 기록한다.

- **연결된 평가 질문**
  - Dockerfile로 이미지 빌드가 가능한가?
  - 매핑된 포트로 접속이 가능한가?
  - 컨테이너 내부 포트로 직접 접속할 수 없는 이유와 필요한 이유를 설명할 수 있는가?

---

#### 단계 10. Bind Mount로 변경 반영 검증
- **목적**
  - 호스트 파일 변경이 컨테이너에 즉시 반영되는지 확인한다.

- **의존 관계**
  - 9단계 완료 후

- **실행 전 요약**
  - 재빌드 없이도 호스트 수정 내용이 반영된다는 점을 보여준다.

- **명령어 또는 절차**
```bash
cd ~/dev/codyssey-mission-01

cat > bind-site/index.html <<'EOF'
<h1>Bind Mount v1</h1>
EOF

docker run -d --name mission-bind -p 8081:80 \
  -v "$(pwd)/bind-site:/usr/share/nginx/html:ro" \
  nginx:alpine

curl http://localhost:8081

cat > bind-site/index.html <<'EOF'
<h1>Bind Mount v2</h1>
<p>host change reflected</p>
EOF

curl http://localhost:8081
docker inspect mission-bind --format '{{json .Mounts}}'
```

- **확인 방법**
- 첫 번째 `curl` 과 두 번째 `curl` 응답 차이 확인
- `docker inspect` 에 host path / target path 확인

- **주의 사항**
  - bind mount는 macOS에서 **절대 경로 기반**이 안전하다.
  - 브라우저 캐시보다 `curl` 결과를 우선 증거로 사용한다.

- **연결된 평가 질문**
  - 포트/볼륨 설정을 어떤 방식으로 재현 가능하게 정리했는지 설명할 수 있는가?
  - 절대 경로/상대 경로를 어떤 상황에서 선택하는지 설명할 수 있는가?

---

### 2-4. Docker 볼륨 실습

#### 단계 11. Named Volume 생성 및 영속성 검증
- **목적**
  - 컨테이너 삭제 후에도 데이터가 유지되는 구조를 확인한다.

- **의존 관계**
  - 5단계 완료 후

- **실행 전 요약**
  - 데이터가 컨테이너 writable layer가 아니라 volume에 저장되도록 구성한다.

- **명령어 또는 절차**
```bash
docker volume create missiondata
docker volume ls

docker run -d --name volume-writer -v missiondata:/data ubuntu sleep infinity
docker exec volume-writer bash -lc "echo persisted-data > /data/hello.txt && cat /data/hello.txt"

docker rm -f volume-writer

docker run -d --name volume-reader -v missiondata:/data ubuntu sleep infinity
docker exec volume-reader bash -lc "cat /data/hello.txt"

docker volume inspect missiondata
```

- **확인 방법**
- writer 컨테이너에서 저장한 파일을 reader 컨테이너에서 다시 읽을 수 있는지 확인
- `docker volume inspect missiondata` 결과 확인

- **주의 사항**
  - `docker rm -f volume-writer` 는 컨테이너만 삭제한다.
  - `docker volume rm missiondata` 를 실행하면 실제 데이터도 삭제된다.

- **연결된 평가 질문**
  - Docker 볼륨 데이터가 컨테이너 삭제 후에도 유지되는가?
  - 컨테이너 삭제 후 데이터가 사라진 경험이 있다면, 이를 방지하기 위한 대안을 설명할 수 있는가?

---

### 2-5. Git 설정 및 GitHub 연동

#### 단계 12. Git 전역 설정, 로컬 초기화, 첫 커밋
- **목적**
  - Git 사용자 정보 및 기본 브랜치 설정 후, 로컬 저장소를 초기화한다.

- **의존 관계**
  - 1단계 완료 후

- **실행 전 요약**
  - GitHub 연동 전에 Git 전역 설정과 첫 커밋이 먼저 있어야 한다.

- **명령어 또는 절차**
```bash
git --version
git config --global user.name "YOUR_NAME"
git config --global user.email "YOUR_EMAIL"
git config --global init.defaultBranch main
git config --list --global

cd ~/dev/codyssey-mission-01
git init
git status
git add .
git commit -m "Initialize mission 1 workspace and evidence"
git log --oneline -n 3
```

- **확인 방법**
- `git config --list --global` 에 `user.name`, `user.email`, `init.defaultBranch=main` 확인
- `git log --oneline` 에 첫 커밋 확인

- **주의 사항**
  - 공개 이메일 대신 GitHub noreply 이메일 사용 가능
  - 토큰/비밀번호는 README와 로그에 남기지 않는다.

- **연결된 평가 질문**
  - Git 설정 및 GitHub 연동이 확인되는가?

---

#### 단계 13. GitHub 저장소 연결 및 VSCode 연동
- **목적**
  - GitHub 원격 저장소를 연결하고, VSCode에서 GitHub 로그인 상태를 확인한다.

- **의존 관계**
  - 12단계 완료 후

- **실행 전 요약**
  - 인증 과정은 민감정보가 노출될 수 있으므로, 로그 기록 도구는 미리 종료하는 것이 안전하다.

- **명령어 또는 절차**
```bash
cd ~/dev/codyssey-mission-01
git remote add origin https://github.com/<your-account>/<repo-name>.git
git branch -M main
git push -u origin main
git remote -v
open https://github.com/<your-account>/<repo-name>
```

- **대체 절차 (GitHub CLI 사용 시)**
```bash
brew install gh
gh auth login
gh repo create codyssey-mission-01 --public --source=. --remote=origin --push
```

- **VSCode 절차**
```bash
open -a "Visual Studio Code" ~/dev/codyssey-mission-01
```
- VSCode 우상단 **Accounts** → **Sign in with GitHub**
- Source Control 탭에서 저장소 인식 여부 확인

- **확인 방법**
- `git remote -v` 출력
- GitHub 저장소 웹 페이지 확인
- VSCode GitHub 로그인 상태 스크린샷 확보

- **주의 사항**
  - 인증 토큰, 인증 코드, 이메일 전체 주소는 마스킹한다.

- **연결된 평가 질문**
  - Git 설정 및 GitHub 연동이 확인되는가?

---

### 2-6. 프로젝트 디렉토리 구조 설계 및 재현 가능한 설정 정리

#### 단계 14. 디렉토리 구조 설명과 재현 문서 정리
- **목적**
  - 구조 기준, 포트/볼륨 설정, 검증 방식, 트러블슈팅 내용을 README에 정리한다.

- **의존 관계**
  - 1~13단계 완료 후

- **실행 전 요약**
  - 이 단계는 단순 실습 결과를 **설명 가능한 제출물**로 바꾸는 단계다.

- **명령어 또는 절차**
```bash
cd ~/dev/codyssey-mission-01
find . -maxdepth 3 -not -path "./.git*" | sort

sw_vers
echo $SHELL
echo $TERM_PROGRAM
docker --version
git --version
docker ps -a
docker images
docker volume ls
```

- **README에 반드시 포함할 항목**
```md
## 1) 실행 환경
- OS
- Shell / Terminal
- Docker 버전
- Git 버전

## 2) 수행 체크리스트
- 터미널 기본 조작
- 권한 변경
- Docker 설치/점검
- hello-world
- Dockerfile 빌드/실행
- 포트 매핑 접속
- Bind Mount 반영
- Volume 영속성
- Git 설정 + GitHub/VSCode 연동

## 3) 수행 로그
- 명령어 + 출력 결과 코드블록

## 4) 검증 결과
- 브라우저 / curl
- docker ps / logs / stats
- volume 전후 비교

## 5) 구조 설명
- 디렉토리 설계 기준
- 포트/볼륨 재현 방식

## 6) 트러블슈팅
- 문제 → 가설 → 확인 → 해결/대안

## 7) 보안 주의
- 민감정보 마스킹
```

- **포트 정리 표 예시**

| 서비스 | 실행 명령 | Host:Container | 접속 URL |
|---|---|---|---|
| mission-web | `docker run -d --name mission-web -p 8080:80 ...` | `8080:80` | `http://localhost:8080` |
| mission-bind | `docker run -d --name mission-bind -p 8081:80 ...` | `8081:80` | `http://localhost:8081` |

- **스토리지 정리 표 예시**

| 유형 | 소스 | 타깃 | 목적 | 검증 방법 |
|---|---|---|---|---|
| Bind Mount | `$(pwd)/bind-site` | `/usr/share/nginx/html` | 호스트 변경 즉시 반영 | `curl` 전/후 비교 |
| Named Volume | `missiondata` | `/data` | 컨테이너 삭제 후 데이터 유지 | writer 삭제 후 reader에서 `cat` |

- **확인 방법**
- README만 읽고도 누가 실행하더라도 재현 순서와 검증 기준을 이해할 수 있어야 한다.

- **주의 사항**
  - bind mount는 개인 PC 절대경로가 들어갈 수 있으므로 `$(pwd)` 기준으로 재현 방법을 적는 것이 좋다.

- **연결된 평가 질문**
  - 프로젝트 디렉토리 구조를 어떤 기준으로 구성했는지 설명할 수 있는가?
  - 포트/볼륨 설정을 어떤 방식으로 재현 가능하게 정리했는지 설명할 수 있는가?

---

## 3. 개념 설명 섹션 (항목 3 대응)

### 3-1. 이미지 vs 컨테이너 (빌드/실행/변경 관점)

| 관점 | 이미지(Image) | 컨테이너(Container) |
|---|---|---|
| 본질 | 실행 템플릿 | 실행 중 인스턴스 |
| 생성 시점 | `docker build` | `docker run` |
| 변경 방식 | Dockerfile 수정 후 다시 빌드 | 실행 중 변경 가능하지만 기본적으로 일시적 |
| 지속성 | 재사용 가능, 버전 태깅 가능 | 삭제 시 writable layer 변경분은 사라질 수 있음 |
| 예시 | `codyssey-mission-web:1.0` | `mission-web`, `mission-bind` |

- **설명 문장 예시**
  - 이미지는 **설계도**, 컨테이너는 **그 설계도로 실행된 실제 인스턴스**다.
  - Dockerfile을 수정하면 이미지를 다시 빌드해야 하고, 컨테이너 내부에서만 변경한 내용은 볼륨/마운트가 없으면 삭제 시 사라질 수 있다.

---

### 3-2. 포트 매핑이 필요한 이유
- 컨테이너는 기본적으로 **격리된 네트워크 네임스페이스**에서 실행된다.
- 컨테이너 내부 `80` 포트에서 웹 서버가 떠 있어도, 호스트 브라우저가 그 포트에 직접 붙는 구조가 아니다.
- 그래서 `-p 8080:80` 처럼 **호스트 포트와 컨테이너 포트를 publish** 해야 외부 접속이 가능하다.

- **설명 문장 예시**
  - 컨테이너 내부 포트는 컨테이너 네트워크 안에서만 열려 있으므로, 호스트에서 접속하려면 `docker run -p host_port:container_port` 설정이 필요하다.

---

### 3-3. 절대 경로 vs 상대 경로 선택 기준

| 기준 | 절대 경로 | 상대 경로 |
|---|---|---|
| 의미 | 루트부터 전체 경로 | 현재 디렉토리 기준 경로 |
| 장점 | 모호성 없음, Docker bind mount에 안전 | 짧고 가독성 좋음 |
| 단점 | 사용자 환경 의존 가능 | 현재 위치가 바뀌면 깨질 수 있음 |
| 권장 사용처 | `-v "$(pwd)/bind-site:..."`, 로그 수집, 시스템 파일 | repo 내부 파일 이동, 일반 CLI 조작 |

- **설명 문장 예시**
  - Docker bind mount처럼 호스트 경로를 정확하게 지정해야 하는 경우에는 절대 경로가 안전하고, 저장소 내부 이동이나 일반 파일 조작은 상대 경로가 간결하다.

---

### 3-4. 파일 권한 숫자 표기 규칙 (755, 644 등)
- 권한 값 규칙
  - `r = 4`
  - `w = 2`
  - `x = 1`

- 세 자리의 의미
  - 첫째 자리: owner
  - 둘째 자리: group
  - 셋째 자리: others

- 예시
  - `755 = 7 / 5 / 5 = (rwx) / (r-x) / (r-x)`
  - `644 = 6 / 4 / 4 = (rw-) / (r--) / (r--)`

- **설명 문장 예시**
  - `run.sh` 에 755를 주는 이유는 owner는 읽기/쓰기/실행이 가능해야 하고, group/others는 읽기와 실행만 필요하기 때문이다.
  - 일반 텍스트 파일은 실행이 필요 없기 때문에 644가 적절하다.

---

## 4. 문제 해결 시나리오 섹션 (항목 4 대응)

### 4-1. 호스트 포트 충돌 진단 순서

#### 상황
- `docker run -d --name mission-web -p 8080:80 ...` 실행 시 `address already in use` 오류 발생

#### 진단 순서
1. 오류 메시지 확인
```bash
docker run -d --name mission-web -p 8080:80 codyssey-mission-web:1.0
```

2. 해당 포트를 사용하는 프로세스 확인
```bash
lsof -nP -iTCP:8080 -sTCP:LISTEN
```

3. Docker 컨테이너 점유 여부 확인
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

4. macOS 프로세스 정보 확인
```bash
ps -p <PID> -o pid,ppid,command=
```

5. 조치
- 예전 컨테이너가 점유 중이면 중지/삭제
```bash
docker stop <container_name>
docker rm <container_name>
```
- 다른 앱이면 앱 종료
- 종료가 불가능하면 포트 변경
```bash
docker run -d --name mission-web -p 8081:80 codyssey-mission-web:1.0
```

6. 재검증
```bash
curl http://localhost:8081
```

- **설명 포인트**
  - 문제의 핵심은 컨테이너 내부 포트가 아니라 **호스트 포트 바인딩 실패**다.

---

### 4-2. 컨테이너 삭제 후 데이터 유실 방지 방법

#### 잘못된 방식
- 데이터를 컨테이너 내부 writable layer에만 저장
- 컨테이너 삭제 시 데이터도 함께 사라질 수 있음

#### 대안 1. Named Volume 사용
```bash
docker volume create missiondata
docker run -d --name app1 -v missiondata:/data ubuntu sleep infinity
```

#### 대안 2. Bind Mount 사용
```bash
docker run -d --name app2 -v "$(pwd)/host-data:/data" ubuntu sleep infinity
```

#### 대안 3. 백업 파일 생성
```bash
docker run --rm -v missiondata:/data -v "$(pwd):/backup" ubuntu \
  tar czf /backup/missiondata-backup.tgz /data
```

- **설명 포인트**
  - 정적 파일·소스는 bind mount가 편하고,
  - 상태 데이터·업로드 파일·DB 계열은 named volume이 더 안정적이다.

---

### 4-3. 가장 어려운 지점 + 가설 → 확인 → 조치 프레임 예시

> 아래는 예시입니다. 실제 제출 시에는 **본인이 겪은 실제 문제**로 바꾸는 것이 가장 좋습니다.

#### 문제
- `docker --version` 은 되는데 `docker info` 는 실패했다.

#### 가설
- Docker CLI만 설치되어 있고, 런타임(OrbStack/Docker Desktop)이 실행되지 않았을 수 있다.
- 또는 Docker context가 올바르지 않을 수 있다.

#### 확인
```bash
docker --version
docker info
docker context ls
ps aux | grep -E "OrbStack|Docker"
```

#### 조치
```bash
open -a OrbStack
# 또는
open -a Docker

docker info
```

---

## 7. 첨부 자료 목록 예시

- `docs/logs/01-session.txt`
- `docs/logs/02-docker.txt`
- `docs/screenshots/01-localhost-8080.png`
- `docs/screenshots/02-github-repo.png`
- `docs/screenshots/03-vscode-github-login.png`
- `docker/Dockerfile`
- `app/index.html`

---