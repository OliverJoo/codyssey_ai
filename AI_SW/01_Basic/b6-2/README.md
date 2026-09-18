# b6-2 — AI 기반 Git 커밋 및 PR 초안 생성기 (`ai_gitgen`)

Git 저장소의 스테이징/비스테이징 변경 사항(`git status`, `git diff`)을 분석하고, OpenAI 호환 AI API를 호출하여 Conventional Commits 커밋 메시지 또는 규격화된 PR(Pull Request) 제목·본문 초안을 생성하는 Python 3.10+ 기반 CLI 도구입니다.

실제 `git commit`, `git push`, PR 생성을 임의로 수행하지 않으며, 개발자가 검토 후 적용할 수 있도록 안전하게 초안을 터미널에 출력합니다.

전체 처리 흐름은 [04_ai-gitgen-flow.html](diagrams/04_ai-gitgen-flow.html) 또는 [05_diagram_viewer.html](05_diagram_viewer.html) 인터랙티브 다이어그램에서 확대·축소 및 드래그하며 확인할 수 있습니다.

---

## 📌 주요 특징

- **Git 변경 내역 자동 수집**: Git 저장소 루트를 자동 감지하고 `git status --short` 및 `git diff`를 수집 (변경 사항이 없을 경우 불필요한 API 호출 차단)
- **안전 모드 (Safe Mode)**:
  - 개인정보 및 민감정보(이메일, 전화번호, API Key, Bearer Token, Password 등)를 정규식으로 감지하여 `[MASKED]` 치환
  - 컨텍스트 초과 및 비용 방지를 위해 전송 파일 수(기본 10개) 및 diff 줄 수(기본 200줄) 제한
- **규격 검증 및 포맷터**:
  - `commit`: 첫 줄 50~72자 제한 및 본문 핵심 불릿 요약
  - `pr`: 제목 80자 제한 및 필수 3대 섹션(`## Why`, `## What`, `## How to Test`) 보정
- **무의존성 순수 표준 라이브러리**: 외부 패키지 설치 없이 Python 3.10+ 내장 라이브러리(`urllib`, `json`, `argparse` 등)만으로 구동
- **팀 커스텀 컨벤션 지원**: JSON 규칙 파일(`--convention-file`)을 주입하여 프로젝트별 커밋 컨벤션 커스터마이징 가능
- **Dry-run 지원**: API 호출 없이 AI에 전달될 프롬프트와 보안 마스킹 결과를 사전 점검

---

## 🚀 시작하기

### 1. 준비 환경
- Python 3.10 이상
- Git

### 2. 환경 변수 설정
OpenAI Chat Completions 형식과 호환되는 API 키를 환경 변수에 등록합니다. API 키는 코드에 하드코딩하거나 파일에 기록하지 않습니다.

```bash
# 필수: API 키 등록
export AI_API_KEY="your-api-key"

# 선택: 사용자 지정 엔드포인트 URL (기본값: https://copa.codyssey.kr/v1/chat/completions)
export AI_API_URL="https://copa.codyssey.kr/v1/chat/completions"
```

---

## 💻 사용법

> ⚠️ 변경 사항이 있는 **Git 저장소 루트 디렉터리**에서 실행합니다.

### 1. 커밋 메시지 초안 생성 (`commit`)

```bash
# 기본 실행 (기본 모델: gpt-5.4-mini)
python AI_SW/01_Basic/b6-2/main.py commit

# 옵션 지정 (모델, 창의성, 토큰 수 등)
python AI_SW/01_Basic/b6-2/main.py commit --model gpt-5.4-mini --temperature 0.1 --max-tokens 300

# API 호출 없이 프롬프트와 마스킹 결과만 확인 (비용 0원)
python AI_SW/01_Basic/b6-2/main.py commit --dry-run
```

#### 터미널 출력 예시
```text
[INFO] safe-mode=ON, 파일 2/2, diff 1줄, 마스킹 0건

=== COMMIT TITLE ===
b6-1, b6-2 디렉터리 추가

=== COMMIT BODY ===
- AI_SW/01_Basic 아래 b6-1, b6-2 경로가 새로 추가됨

[INFO] API 호출 횟수: 1
[NOTICE] AI 초안입니다. 복사하기 전에 diff와 함께 사람이 검토하세요.
```

---

### 2. PR 제목 및 본문 초안 생성 (`pr`)

```bash
# PR 초안 생성 실행
python AI_SW/01_Basic/b6-2/main.py pr --temperature 0.2 --max-tokens 500
```

#### 터미널 출력 예시
```markdown
[INFO] safe-mode=ON, 파일 1/1, diff 9줄, 마스킹 0건

=== PR TITLE ===
Git 변경 기반 PR 초안 생성 기능 추가

=== PR BODY ===
## Why
- 반복적인 PR 설명 작성을 줄이기 위해

## What
- 변경 내용을 읽어 PR 제목과 본문을 생성

## How to Test
- 자동 테스트와 로컬 시연 스크립트 실행

[INFO] API 호출 횟수: 1
[NOTICE] AI 초안입니다. 복사하기 전에 diff와 함께 사람이 검토하세요.
```

---

### 3. 예외 및 특수 상황 처리

- **변경 사항이 없는 경우**:
  ```text
  [INFO] 변경 사항이 없습니다. AI API를 호출하지 않습니다.
  ```
- **API Key가 설정되지 않은 경우**:
  ```text
  [ERROR] AI_API_KEY 환경 변수가 없습니다. README의 설정 방법을 확인하세요.
  ```
- **인증 실패 / 네트워크 오류 시**:
  ```text
  [ERROR] API 키가 거부되었습니다. AI_API_KEY를 확인하세요.
  [ERROR] 네트워크 연결에 실패했습니다: <상세 원인>
  ```

---

## ⚙️ CLI 옵션 상세 안내

```text
python main.py {commit,pr} [옵션]
```

| 옵션 | 단축 별칭 | 기본값 | 허용 범위 | 설명 |
|---|---|---|---|---|
| `--model` | `-model` | `gpt-5.4-mini` | 문자열 | 사용할 AI 모델 이름 |
| `--temperature` | `-temperature` | `0.2` | `0.0` ~ `2.0` | 생성 창의성 정도 |
| `--max-tokens` | `-max_tokens` | `500` | `64` ~ `2000` | 최대 출력 토큰 수 |
| `--safe-mode` | `--no-safe-mode` | `True` (ON) | 불리언 | 민감정보 마스킹 및 diff 제한 활성화 |
| `--max-files` | - | `10` | `1` ~ `100` | AI에 전송할 최대 파일 수 |
| `--max-diff-lines` | - | `200` | `1` ~ `5000` | AI에 전송할 최대 diff 줄 수 |
| `--dry-run` | - | `False` | 플래그 | API 호출 없이 생성된 프롬프트만 출력 |
| `--convention-file` | - | `None` | 파일 경로 | 커스텀 컨벤션 JSON 파일 경로 |

---

## 🛡️ 안전 모드 및 운영/비용 관리

1. **민감정보 보호**:
   - `safe-mode`가 켜져 있으면 diff 내 이메일, 전화번호, API Key 패턴(`sk-...`, Bearer 등), 비밀번호 등이 자동 감지되어 `[MASKED]`로 치환됩니다.
2. **토큰 및 비용 제한**:
   - diff 크기가 과도하게 커지면 기본 최대 10개 파일, 200줄까지만 잘라서 전송하므로 컨텍스트 초과 및 비용 급증을 방지합니다.
   - 단일 실행 시 AI API를 정확히 **1회**만 호출하며, 실행 종료 시 `API 호출 횟수: 1`을 명시합니다.
3. **사람 중심의 최종 검토**:
   - AI가 생성한 결과는 초안이므로, 직접 변경 diff와 대조하여 검토 후 `git commit -m` 또는 GitHub PR에 복사·붙여넣기하여 반영합니다.

---

## 📂 프로젝트 구조

```text
b6-2/
├── main.py                         # CLI 진입점
├── src/
│   └── ai_gitgen/
│       ├── __init__.py             # 패키지 메타데이터
│       ├── cli.py                  # 옵션 파서 및 전체 파이프라인
│       ├── git_reader.py           # 저장소 검증 및 git status/diff 수집
│       ├── safety.py               # 마스킹 및 전송 크기 제어
│       ├── prompts.py              # 모드별 프롬프트 빌더
│       ├── api_client.py           # OpenAI 호환 Chat Completions 클라이언트
│       ├── validators.py           # 길이 및 마크다운 헤더 유효성 검증
│       ├── config.py               # JSON 기반 컨벤션 로더
│       └── models.py               # 데이터 구조체 (GitChanges, SafeChanges 등)
├── tests/                          # 단위 테스트 및 로컬 모의 API
│   ├── mock_ai_server.py           # 외부 비용 없는 로컬 모의 HTTP 서버
│   ├── test_cli.py                 # CLI 옵션 및 엔드투엔드 테스트
│   ├── test_validators.py          # 길이/섹션 유효성 검증 테스트
│   └── verify_links.py             # 문서 링크 및 파일 정합성 검사기
├── diagrams/                       # 아키텍처 및 처리 흐름 다이어그램
│   └── 04_ai-gitgen-flow.html      # Pan/Zoom 지원 인터랙티브 흐름도
├── bonus/                          # 보너스 과제 자료
│   ├── README_BONUS.md             # 보너스 설명서
│   ├── PR_EVIDENCE_TEMPLATE.md     # 실제 PR 증빙 템플릿
│   ├── convention_example.json     # 커스텀 컨벤션 규칙 예시
│   ├── 01_compare_convention.sh    # 컨벤션 적용 전/후 비교 스크립트
│   └── 02_compare_safe_mode.sh     # safe-mode ON/OFF 비교 스크립트
├── 01_setup.sh                     # 환경 확인 스크립트
├── 02_run_demo.sh                  # 로컬 모의 서버 기반 전체 시연 스크립트
├── 03_run_tests.sh                 # 자동 테스트 실행 스크립트
├── 05_diagram_viewer.html          # 다이어그램 뷰어
└── 06_verify_submission.sh         # 제출물 최종 정합성 검증 스크립트
```

---

## 🧪 테스트 및 시연 스크립트

외부 API 호출 비용 없이 로컬 모의 API 서버를 활용해 모든 기능을 검증할 수 있습니다.

```bash
# 1. 환경 확인 (Git 및 Python 3.10+)
bash AI_SW/01_Basic/b6-2/01_setup.sh

# 2. 임시 저장소와 모의 API 서버를 통한 전체 시연 (commit / pr)
bash AI_SW/01_Basic/b6-2/02_run_demo.sh

# 3. 단위 테스트 실행 (CLI 및 유효성 검증기)
bash AI_SW/01_Basic/b6-2/03_run_tests.sh

# 4. 제출 전 파일명, 링크, 문법, 테스트 종합 검증
bash AI_SW/01_Basic/b6-2/06_verify_submission.sh
```

---

## 🎁 보너스 과제 안내

보너스 과제에 대한 상세 설명 및 실습 파일은 [bonus/README_BONUS.md](bonus/README_BONUS.md)를 참조하세요.

1. **실제 리포지토리 PR 적용 증빙**: [bonus/PR_EVIDENCE_TEMPLATE.md](bonus/PR_EVIDENCE_TEMPLATE.md) 양식 활용
2. **팀 컨벤션 커스터마이징 비교**: [bonus/01_compare_convention.sh](bonus/01_compare_convention.sh) 실행
3. **안전 모드 ON/OFF 비교**: [bonus/02_compare_safe_mode.sh](bonus/02_compare_safe_mode.sh) 실행
