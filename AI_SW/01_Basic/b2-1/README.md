# 나만의 용돈 기입장 콘솔 프로그램 (budget_app)

Python 표준 라이브러리만을 활용하여 구축된 파일 입출력(JSONL/CSV) 기반의 가계부 콘솔 애플리케이션입니다.  
제너레이터 스트리밍, 데코레이터 공통 관심사 분리, 타입 힌트, 계층별 모듈화(Model-Storage-Service-CLI) 및 TDD(테스트 주도 개발) 방법론을 준수하여 작성되었습니다.

---

## 1. 아키텍처 및 모듈 구조

```text
b2-1/
├── budget_app/
│   ├── __init__.py
│   ├── __main__.py          # Base CLI 진입점 (python -m budget_app)
│   ├── models.py            # Transaction, Category, Budget 데이터클래스 및 유효성 검증
│   ├── storage.py           # JSONL 파일 기반 영구 저장소 (yield 스트리밍 처리)
│   ├── service.py           # 비즈니스 로직 (CRUD, 검색, 요약 통계, 예산, CSV 가져오기/내보내기)
│   ├── decorators.py        # 예외 처리(@handle_cli_errors), 실행 시간 측정 데코레이터
│   ├── cli.py               # 명령행 인자(argparse) 파싱 및 대화형 입력 처리
│   └── bonus.py             # [보너스] Base 클래스를 상속받은 확장 모듈
├── tests/
│   ├── __init__.py
│   ├── test_models.py       # 모델 및 유효성 검증 테스트
│   ├── test_storage.py      # 저장소 및 스트리밍 테스트
│   ├── test_service.py      # 비즈니스 로직 테스트
│   ├── test_cli.py          # CLI 인자 및 대화형 입출력 테스트
│   └── test_bonus.py        # 보너스 과제(원자성, 테이블, 백업, 반복거래) 테스트
├── main.py                  # 기본 실행 래퍼 스크립트
├── main_bonus.py            # 보너스 확장 실행 래퍼 스크립트
└── README.md                # 본 문서
```

### 계층별 책임 설명
1. **모델 계층 (`models.py`)**:
   - `dataclass`를 사용하여 데이터 구조(`Transaction`, `Category`, `Budget`)를 정의하고 타입 힌트를 적용합니다.
   - 날짜(`YYYY-MM-DD`), 금액(양수), 타입(`income`/`expense`) 유효성을 검증하고 `ValidationError`를 발생시킵니다.
2. **저장소 계층 (`storage.py`)**:
   - 3개 이상의 JSONL 파일(`transactions.jsonl`, `categories.jsonl`, `budgets.jsonl`)로 분리 저장합니다.
   - `yield` 기반의 제너레이터를 사용하여 대용량 파일도 메모리에 한 번에 올리지 않고 한 줄씩 스트리밍 처리합니다.
3. **서비스 계층 (`service.py`)**:
   - 비즈니스 규칙(월별 요약 통계 계산, 예산 대비 사용률 및 초과 경고, 카테고리 삭제 시 사용 여부 검증 및 대체 등)을 수행합니다.
4. **데코레이터 계층 (`decorators.py`)**:
   - `@handle_cli_errors`: 사용자 정의 예외 발생 시 스택트레이스 대신 `[오류]` 및 `[힌트]`를 출력하고 `exit code 1`로 안전하게 종료합니다.
   - `@measure_execution_time`: 실행 시간을 밀리초(ms) 단위로 측정합니다.
5. **CLI 계층 (`cli.py`)**:
   - 리눅스 표준인 `--` 옵션 규격을 준수하며, `add` 시 대화형 `input()` 입력을 처리합니다.

---

## 2. 저장 파일 위치 및 형식

기본 저장 위치: `./data` (옵션 `--data-dir <경로>`로 변경 가능)

1. `transactions.jsonl`: 거래 내역 (ID, 타입, 날짜, 금액, 카테고리, 메모, 태그)
2. `categories.jsonl`: 등록된 카테고리 목록 (기본값: food, transport, living, shopping, salary, allowance, etc)
3. `budgets.jsonl`: 월별 설정 예산 (월, 예산 금액)
4. `recurring.jsonl` (보너스): 반복 거래 규칙 (반복일, 타입, 카테고리, 금액, 메모, 태그)

---

## 3. CSV 가져오기/내보내기 스키마

`import` 및 `export` 시 사용하는 CSV 스키마는 다음과 같으며, UTF-8 인코딩 및 헤더를 포함합니다.

| Column | Required | Type | 설명 | 예시 |
| :--- | :---: | :--- | :--- | :--- |
| **date** | Y | String | 거래 날짜 (YYYY-MM-DD) | `2024-01-15` |
| **type** | Y | String | 거래 타입 (`income` 또는 `expense`) | `expense` |
| **category** | Y | String | 등록된 카테고리명 | `food` |
| **amount** | Y | Integer | 양수 정수 금액 | `15000` |
| **memo** | N | String | 메모/설명 | `점심 식사` |
| **tags** | N | String | 쉼표(,)로 구분된 태그 목록 | `lunch,meal` |

---

## 4. 사용 방법 및 주요 명령어 예시

Conda 가상환경(`py312`)에서 실행합니다:

```bash
# 기본 실행
python -m budget_app <command> [options]
# 또는
python main.py <command> [options]
```

### 1) 거래 추가 (`add`) - 대화형 입력
```bash
python -m budget_app add
# 날짜(YYYY-MM-DD): 2024-01-15
# 타입(income/expense): expense
# 카테고리: food
# 금액(양수): 15000
# 메모(선택): 점심
# 태그(쉼표로 구분, 없으면 엔터): meal
# [저장 완료] id=TX-000001
```

### 2) 거래 목록 조회 (`list`)
```bash
python -m budget_app list --limit 5
# TX-000001 | 2024-01-15 | expense | food | 15000 | 점심
```

### 3) 거래 검색 (`search`)
```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food --type expense
```

### 4) 예산 설정 및 월별 요약 (`budget`, `summary`)
```bash
# 2024-01 예산 설정
python -m budget_app budget set --month 2024-01 --amount 500000

# 2024-01 요약 및 예산 사용률/초과 확인 (TOP 3 지출 카테고리)
python -m budget_app summary --month 2024-01 --top 3
```

### 5) 카테고리 관리 (`category`)
```bash
python -m budget_app category list
python -m budget_app category add travel
# 사용 중인 카테고리 삭제 시 대체 카테고리 지정
python -m budget_app category remove travel --replace living
```

### 6) 거래 수정 및 삭제 (`update`, `delete`)
```bash
# 수정
python -m budget_app update --id TX-000001 --amount 18000 --memo "점심 특식"

# 삭제
python -m budget_app delete --id TX-000001
```

### 7) CSV 내보내기 및 가져오기 (`export`, `import`)
```bash
# 2024-01 데이터 내보내기
python -m budget_app export --out export.csv --month 2024-01

# CSV 파일에서 데이터 가져오기
python -m budget_app import --from export.csv
```

---

## 5. 보너스 과제 (상속을 통한 확장 구현)

보너스 과제는 기존 클래스를 상속(`AtomicTransactionRepository`, `BonusBudgetService`, `BonusCLI`)하여 `budget_app/bonus.py` 및 `main_bonus.py`로 구현되었습니다.

```bash
python main_bonus.py <command> [options]
```

1. **저장 원자성 강화 (`AtomicTransactionRepository`)**:
   - `update` 및 `delete` 시 동일 파일 시스템 내 임시 파일(`tempfile`)에 작성 후 `os.replace`로 원자적(Atomic) 교체하여 파일 손상을 방지합니다.
2. **테이블 출력 포맷 (`TableFormatter`)**:
   - 외부 라이브러리 없이 유니코드 전각 문자(한글) 너비를 자동 계산하여 정렬된 ASCII/Unicode 표를 출력합니다.
3. **타임스탬프 백업 (`backup`)**:
   - `python main_bonus.py backup --backup-dir ./backups` 실행 시 `backup_YYYYMMDD_HHMMSS.zip` 형태로 데이터 전체를 압축 백업합니다.
4. **반복 거래 관리 (`recurring`)**:
   - `python main_bonus.py recurring add`: 매월 지정일에 발생할 반복 내역(월세, 구독료 등) 등록
   - `python main_bonus.py recurring list`: 등록된 반복 내역 조회
   - `python main_bonus.py recurring generate --month 2024-01`: 해당 월의 반복 거래 자동 생성 (중복 생성 방지)

---

## 6. 테스트 실행 (TDD)

```bash
# 전체 테스트 실행
python -m unittest discover -s tests -v
```
