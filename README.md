# Codyssey Missions 🚀

2026 Codyssey AI/SW 개발 역량 강화 미션 수행 코드 및 프로젝트 아티팩트 모노레포(Monorepo)입니다.

---

## 📌 저장소 구조

```text
codyssey_missions/
├── pre_course/                # 선발 과정 미션
│   ├── e1-1/                  # Git 기초 및 팀 협업 환경 설정
│   ├── e1-2/                  # 콘솔 퀴즈 게임 프로그램 (Python)
│   └── e1-3/                  # Mini NPU Simulator (MAC 연산 시뮬레이터)
│
└── AI_SW/                     # 본 과정 미션
    ├── 01_Basic/              # 기초 심화 트랙 (OS, DB, Git, Web, AI)
    │   ├── b1-1/              # Linux 시스템 자가 점검 및 모니터링 자동화
    │   ├── b1-2/              # Linux 프로세스 장애 분석 (OOM, CPU Spike, Deadlock)
    │   ├── b2-1/              # 가계부 콘솔 프로그램 (TDD 및 계층형 모듈화)
    │   ├── b2-2/              # GitHub Flow 4인 협업 (PR, 코드 리뷰, 충돌 해결)
    │   ├── b3-1/              # Mini Redis (자료구조 기반 In-Memory Key-Value 저장소)
    │   ├── b3-2/mini-git/     # Python 기반 모의 Git CLI (DAG 커밋 그래프 관리)
    │   ├── b4-1/              # 순수 HTML/CSS/JS 반응형 포트폴리오 웹사이트
    │   ├── b5-1/              # MariaDB 카페 주문 관리 시스템 DB 설계 및 분석 쿼리
    │   ├── b6-2/              # AI 기반 Git 커밋 메시지 및 PR 초안 자동 생성 CLI
    │   └── b7-1/              # AI Chatbot 프로젝트 및 테스트 환경
    │
    ├── 02_Advanced/           # 심화 트랙 (진행 예정)
    └── 03_Master/             # 마스터 트랙 (진행 예정)
```

---

## 📂 미션별 상세 안내

### 1. Pre-Course (선발 과정)

| 미션 | 프로젝트명 | 주요 기술 | 설명 |
|---|---|---|---|
| **e1-1** | Git 협업 기초 | `Git`, `GitHub` | SSH 키 설정, 원격 저장소 관리 및 기본 브랜치 협업 |
| **e1-2** | 퀴즈 게임 프로그램 | `Python` | 파일 I/O 및 콘솔 기반 인터랙티브 객관식/주관식 퀴즈 게임 |
| **e1-3** | Mini NPU Simulator | `Python`, `Matrix` | 패턴 및 필터 행렬 MAC(Multiply-Accumulate) 연산 가속기 시뮬레이터 |

---

### 2. AI/SW Basic (01_Basic)

| 미션 | 프로젝트명 | 주요 기술 | 핵심 내용 |
|---|---|---|---|
| **b1-1** | 시스템 자가 점검기 | `Shell`, `Linux` | CPU, Memory, Disk 리소스 주기적 모니터링 및 임계치 경고 스크립트 |
| **b1-2** | Linux 장애 분석 | `Linux`, `GDB`, `strace` | OOM, CPU 급증, Deadlock 프로세스 원인 추적 및 트러블슈팅 리포트 작성 |
| **b2-1** | 나만의 용돈 기입장 | `Python`, `unittest` | TDD 기반 계층형 아키텍처 가계부 애플리케이션 (`budget_app`) |
| **b2-2** | GitHub Flow 협업 | `Git`, `GitHub Flow` | 4인 팀 협업 실습 (Issue, Branch, PR, Code Review, Conflict 해소) |
| **b3-1** | Mini Redis | `Python`, `Socket` | 외부 라이브러리 없이 구현한 TCP 소켓 기반 In-Memory Key-Value DB |
| **b3-2** | Mini Git | `Python`, `CLI` | Git 내부 원리(Blob, Tree, Commit DAG 및 refs)를 재현한 모의 Git 도구 |
| **b4-1** | 순수 웹 포트폴리오 | `HTML5`, `CSS3`, `Vanilla JS` | 프레임워크 없이 구현한 반응형 웹 포트폴리오 (이벤트 루프 & DOM 제어) |
| **b5-1** | 카페 주문 관리 DB | `MariaDB`, `SQL` | 3정규화 DB 모델링(ERD), 인덱스 설계, 매출 집계 윈도우 함수 및 뷰 작성 |
| **b6-2** | AI Git 메시지 생성기 | `Python 3.12`, `OpenAI API` | `git diff` 분석, 개인정보 마스킹(Safe Mode), Conventional Commits/PR 생성기 |
| **b7-1** | AI 챗봇 시스템 | `Python`, `LLM` | AI Chatbot 구현 및 대화 테스트 파이프라인 |

---

## 🛠 공통 개발 환경

- **OS**: macOS (Apple Silicon arm64)
- **Language**: Python 3.10+ (기본 Conda 환경: `py312`), Bash / POSIX Shell
- **Database**: MariaDB 11+
- **Tools**: Git, Pytest

---

## 📜 커밋 컨벤션 (Conventional Commits)

본 저장소의 모든 커밋은 Conventional Commits 규격을 따릅니다:

```text
<type>(<scope>): <subject>

- <body bullet 1>
- <body bullet 2>
```

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 추가 및 수정
- `test`: 테스트 코드 추가 및 리팩토링
- `refactor`: 코드 리팩토링
- `chore`: 빌드 업무, 패키지 매니저, gitignore 등 기타 설정 변경
