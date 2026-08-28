# Mini Redis 구축 (AI/SW Basic)

## 📌 미션 소개
Redis는 전 세계에서 가장 널리 사용되는 In-Memory Key-Value 데이터 저장소입니다. 
본 프로젝트는 Redis의 빠른 속도를 뒷받침하는 핵심 내부 자료구조(해시맵, 이중 연결 리스트, 최소 힙)를 파이썬의 내장 컬렉션(`dict`, `set` 등)을 사용하지 않고 밑바닥부터 직접 구현한 **CLI 기반 Mini Redis**입니다. 

이를 통해 평소 당연하게 사용하던 내장 자료형의 동작 원리를 이해하고, 메모리 제한 환경에서 LRU(Least Recently Used) 알고리즘을 통한 데이터 제거와 TTL(Time To Live)을 이용한 데이터 만료 기능을 체득하는 것을 목표로 합니다.

---

## 📂 폴더 구조

```text
b3-1/
├── mini_redis.py           # 메인 CLI 인터페이스 및 Mini Redis 코어 로직
├── hash_map.py             # 직접 구현한 해시 함수 및 체이닝 방식의 해시맵
├── doubly_linked_list.py   # O(1) 이동 및 삽입/삭제를 지원하는 이중 연결 리스트
├── min_heap.py             # TTL 우선순위 처리를 위한 최소 힙(Min Heap)
├── bonus.py                # 보너스 자료구조 (동적 배열, 스택/큐/덱, BST, PubSub)
└── tests/                  # TDD를 위한 단위 테스트(Unit Tests)
    ├── test_mini_redis.py
    ├── test_hash_map.py
    ├── test_doubly_linked_list.py
    ├── test_min_heap.py
    └── test_bonus.py
```

---

## 🚀 주요 기능

### 1. 기본 명령어 (String 타입)
- `SET key value`: 키에 값을 저장합니다. 성공 시 내부적으로 LRU 추적이 업데이트됩니다.
- `GET key`: 키의 값을 조회합니다. 조회 성공 시 LRU 우선순위가 갱신됩니다.
- `DEL key`: 키를 삭제합니다. (데이터, LRU, TTL 구조에서 모두 제거)
- `EXISTS key`: 키의 존재 여부를 반환합니다.
- `DBSIZE`: 전체 저장된 키의 개수를 반환합니다.
- `KEYS`: 저장된 전체 키 목록을 반환합니다.

### 2. 메모리 관리 (LRU 자동 제거)
- `CONFIG SET maxmemory <bytes>`: 사용할 최대 메모리를 바이트 단위로 설정합니다. 
- `INFO memory`: 현재 메모리 사용량, 최대 메모리 제한, 메모리 초과로 인해 제거(evict)된 키의 개수를 확인합니다.
  - *동작 방식*: `SET` 명령어 실행 시 데이터 크기가 `maxmemory`를 초과하게 되면, 가장 오랫동안 사용되지 않은(LRU) 데이터부터 순차적으로 자동 삭제됩니다.

### 3. TTL (만료 시간 관리)
- `EXPIRE key <seconds>`: 특정 키에 만료 시간(초 단위)을 설정합니다.
- `TTL key`: 특정 키의 남은 만료 시간(초)을 조회합니다.
  - *동작 방식*: 최소 힙(Min Heap)에 만료 정보를 저장하여, 명령어 실행 전 만료된 키를 `Lazy Deletion` 방식으로 빠르게 정리합니다.

---

## 🛠️ 실행 및 사용 방법

본 프로젝트는 Python 3.8 이상(권장: `conda env py312` 등)에서 실행 가능합니다.

### 1. 프로그램 실행
```bash
python mini_redis.py
```
위 명령어를 실행하면 `mini-redis>` 프롬프트가 나타나며 명령어들을 입력할 수 있습니다. 
종료하려면 `exit` 또는 `quit`을 입력하거나 `Ctrl+C`를 누르세요.

**실행 예시:**
```text
mini-redis> CONFIG SET maxmemory 30
OK
mini-redis> SET user:1 "Alice"
OK
mini-redis> SET user:2 "Bob"
OK
mini-redis> INFO memory
used_memory:22
maxmemory:30
evicted_keys:0
```

### 2. 단위 테스트 (TDD) 실행
코드는 TDD 방법론을 기반으로 작성되었습니다. `pytest` 패키지를 통해 기능들이 의도한 대로 정확히 동작하는지 검증할 수 있습니다.
```bash
# pytest 설치가 안되어 있을 경우
pip install pytest

# 전체 테스트 실행
PYTHONPATH=. pytest tests/
```

---

## 💡 제약 사항 및 개발 규칙 (학습 목적)
- 파이썬 내장 `dict`, `set`, `collections` 의 사용을 엄격히 제한하고 클래스와 노드 기반으로 직접 자료구조를 작성하였습니다.
- 해시맵의 로드 팩터(0.75)를 측정하여 버킷의 크기를 2배로 확장하는 리사이징(Resizing)이 내부적으로 구현되어 있습니다.
- 모든 자료구조 연산은 Redis와 유사하게 O(1) 혹은 O(log N) 에 근접하도록 설계되었습니다.
