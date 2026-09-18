# b6-2 — AI 기반 Git 메시지 생성기

Git 저장소의 `git status`와 `git diff`를 읽어 AI API로 commit 메시지 또는 PR 제목·본문 초안을 만드는 Python 3.10+ 터미널 프로그램입니다. 실제 commit, push, PR 생성은 하지 않습니다.

처리 흐름은 [diagram-design 인터랙티브 다이어그램](diagrams/04_ai-gitgen-flow.html)에서 확인하세요. 브라우저에서 확대·축소하거나 드래그해 이동할 수 있습니다. 기존 파일명을 사용해야 하는 경우 [05_diagram_viewer.html](05_diagram_viewer.html)이 같은 다이어그램을 엽니다.

## 1. 학습·시연 순서

| 순서 | 파일 | 역할 |
|---:|---|---|
| 1 | [01_setup.sh](01_setup.sh) | Git과 Python 3.10+ 확인 |
| 2 | [02_run_demo.sh](02_run_demo.sh) | 임시 저장소·모의 API로 commit/PR 전체 시연 |
| 3 | [03_run_tests.sh](03_run_tests.sh) | 자동 테스트 실행 |
| 4 | [04_ai-gitgen-flow.html](diagrams/04_ai-gitgen-flow.html) | 프로그램 처리 흐름과 확대·축소·드래그 보기 |
| 5 | [05_diagram_viewer.html](05_diagram_viewer.html) | 이전 파일명과 호환되는 다이어그램 입구 |
| 6 | [06_verify_submission.sh](06_verify_submission.sh) | 파일명, 링크, 문법, 테스트 최종 검사 |

질문별 답은 [README_answer.md](README_answer.md), 스크롤형 설명은 [README_answer.html](README_answer.html)에서 확인합니다. 원본 질문 사본은 [b6-2-question.png](b6-2-question.png)입니다.

## 2. 준비 환경

필수 도구는 Git과 Python 3.10 이상뿐이며 외부 Python 패키지는 사용하지 않습니다.

### macOS — Homebrew 사용

```bash
brew install git python@3.12
bash 01_setup.sh
```

### Ubuntu/Debian 또는 Linux VM

```bash
sudo apt update
sudo apt install -y git python3
bash 01_setup.sh
```

`python3 --version`이 3.10 미만이면 운영체제의 최신 Python 저장소나 `pyenv`로 3.10 이상을 설치하세요.

## 3. 3분 실행

### 비용 없는 로컬 시연

```bash
bash 01_setup.sh
bash 02_run_demo.sh
bash 03_run_tests.sh
```

`02_run_demo.sh`는 임시 Git 저장소와 로컬 모의 HTTP API를 만든 뒤 모두 자동 정리합니다. 현재 작업 저장소, 외부 API, 실제 비용에 영향을 주지 않습니다.

### 실제 AI API 사용

OpenAI Chat Completions 형식과 호환되는 API 키와 URL을 환경 변수로 지정합니다. 키를 파일에 쓰거나 commit하지 마세요.

```bash
export AI_API_KEY='발급받은-키'
export AI_API_URL='https://api.openai.com/v1/chat/completions'
```

변경 사항이 있는 Git 저장소의 **루트**에서 이 프로젝트의 `main.py`를 실행합니다.

```bash
python3 /절대/경로/b6-2/main.py commit
python3 /절대/경로/b6-2/main.py pr
```

## 4. 명령과 옵션

```text
python3 main.py {commit,pr} [옵션]

--model MODEL                 기본: gpt-4o-mini
--temperature 0..2           기본: 0.2
--max-tokens 64..2000        기본: 500
--safe-mode / --no-safe-mode 기본: ON
--max-files N                기본: 10
--max-diff-lines N           기본: 200
--dry-run                     API 호출 없이 프롬프트 표시
--convention-file FILE        보너스: JSON 규칙 적용
```

PDF 표기와 호환되도록 `-model`, `-temperature`, `-max_tokens` 별칭도 지원합니다.

예시:

```bash
python3 main.py commit --model gpt-4o-mini --temperature 0.1 --max-tokens 300
python3 main.py pr --temperature 0.4 --max-tokens 700
python3 main.py commit --dry-run
```

변경이 없으면 API를 호출하지 않고 정상 종료합니다. 환경 변수 누락, 인증 실패, 사용량 제한, 네트워크 실패, 잘못된 JSON 응답은 원인별 오류 메시지를 출력합니다.

## 5. 출력 형식

commit 출력:

```text
=== COMMIT TITLE ===
feat: AI Git 메시지 생성기 추가

=== COMMIT BODY ===
- src/ai_gitgen 모듈 추가
- Git 변경 기반 초안 생성
```

commit 제목은 한 줄, 권장 50자, 최대 72자입니다. 본문이 있으면 최대 2개 핵심 항목을 출력합니다.

PR 출력:

```markdown
=== PR TITLE ===
Git 변경 기반 PR 초안 생성 기능 추가

=== PR BODY ===
## Why
- 반복적인 PR 설명 작성을 줄이기 위해

## What
- 변경 내용을 읽어 PR 제목과 본문을 생성

## How to Test
- 자동 테스트와 로컬 시연 스크립트 실행
```

PR 제목은 최대 80자이며 본문의 세 제목과 각 한 개 이상의 bullet을 검증합니다. 규칙을 어긴 AI 응답은 후처리하거나 명확한 오류로 중단합니다.

## 6. 코드 구조

```text
b6-2/
├── main.py                         # 실행 진입점
├── src/ai_gitgen/
│   ├── cli.py                      # 옵션과 전체 흐름
│   ├── git_reader.py               # status/diff 수집
│   ├── safety.py                   # 마스킹·파일/줄 제한
│   ├── prompts.py                  # commit/PR 프롬프트
│   ├── api_client.py               # AI API 1회 호출
│   ├── validators.py               # JSON·제목·본문 검증
│   ├── config.py                   # 보너스 규칙 파일
│   └── models.py                   # 데이터 구조
├── tests/                          # 모의 API와 자동 테스트
├── diagrams/                       # diagram-design 독립 실행형 HTML
└── bonus/                          # 기본 평가와 분리한 보너스 자료
```

처리 순서는 `collect_changes()` → `protect_changes()` → `build_prompt()` → `request_completion()` → `format_commit()` 또는 `format_pr()`입니다. 이 관계는 [처리 흐름도](diagrams/04_ai-gitgen-flow.html)에도 같은 순서로 표현했습니다.

## 7. 안전성과 비용

- API 키는 `AI_API_KEY`에서만 읽고 코드·설정·로그에 저장하지 않습니다.
- safe mode는 이메일, `sk-...`, Bearer 토큰, key/secret/password/token 값을 `[MASKED]`로 바꿉니다.
- 기본 입력은 10개 파일, diff 200줄로 제한해 민감정보 노출과 토큰 비용을 줄입니다.
- 명령 하나당 API는 한 번만 호출하며 마지막에 호출 횟수를 표시합니다.
- `--dry-run`으로 실제 전송 내용을 먼저 확인할 수 있습니다.
- `--no-safe-mode`는 교육용 비교 외에는 사용하지 마세요.
- AI 결과는 사실이 아닐 수 있으므로 실제 diff와 비교한 뒤 사람이 수정·사용해야 합니다.

## 8. 테스트

```bash
bash 03_run_tests.sh
```

검사 항목은 변경 없음, API 키 누락, 실제 로컬 HTTP commit/PR 생성, 옵션 전달, safe-mode 마스킹, 제목 길이, PR 필수 섹션입니다.

최종 제출 전:

```bash
bash 06_verify_submission.sh
```

## 9. 보너스 문제

보너스는 [bonus/README_BONUS.md](bonus/README_BONUS.md)에 분리했습니다.

- 실제 PR 증빙 양식
- JSON 기반 팀 컨벤션 적용 전·후 비교
- safe mode ON/OFF 비교

실제 PR 링크는 학습자가 본인 저장소에서 수행한 뒤 증빙 양식에 직접 입력해야 합니다.

## 10. 다이어그램 보기

- [diagram-design 흐름도](diagrams/04_ai-gitgen-flow.html): inline SVG, 설명 텍스트와 확대·축소·드래그 기능을 포함한 독립 실행형 HTML
- [호환용 뷰어](05_diagram_viewer.html): 기존 학습 순서의 파일명을 유지하면서 새 흐름도를 표시

다이어그램은 Codex CLI에 설치된 `diagram-design` 플러그인 2.6.12의 기본 라이트 스타일로 작성했습니다. Git 변경 수집, safe mode, 프롬프트, 외부 AI API, 규칙 검증, 사람 최종 검토의 책임 경계를 색과 행으로 구분합니다.
