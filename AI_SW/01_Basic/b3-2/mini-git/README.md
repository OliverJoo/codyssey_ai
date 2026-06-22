# Mini Git

Python으로 간단하게 구현한 모의 Git 저장소 CLI 도구입니다. 커밋 그래프(DAG) 관리, 위상 정렬 로그, 역색인을 통한 검색, 그리고 커밋 최단 경로 탐색 등의 기능을 포함하고 있습니다.

## 주요 기능 및 명령어

* **저장소 초기화**: `INIT <username>`
* **브랜치 생성**: `BRANCH <branch_name>`
* **브랜치 전환**: `SWITCH <branch_name>`
* **커밋 생성**: `COMMIT <message>`
* **커밋 로그**: `LOG [--sort-by=date|author]` (위상 정렬 및 조건부 정렬)
* **최단 경로 탐색**: `PATH <hash1> <hash2>` (최단 경로 중 사전순 가장 빠른 경로 출력)
* **조상 추적**: `ANCESTORS <hash>`
* **커밋 검색**: 
  * 키워드 검색: `SEARCH <keyword>`
  * 작성자 검색: `SEARCH --author=<author>`

## 실행 방법

```bash
python3 main.py
```

---

## 실제 실행 기록 (Session Log)

`main.py` 프로그램을 통해 실행한 실제 기능별 상호작용 기록입니다.

### 1. 저장소 및 브랜치 관리
```bash
mini-git> init Tom
Initialized repository.
Current branch: main
Current user: Tom

mini-git> commit 'init commit'
[main c03427] init commit

mini-git> commit 'add login feature'
[main e5078f] add login feature

mini-git> commit 'fix login feature'
[main 227fec] fix login feature

mini-git> commit 'refact login feature'
[main 3f1fc0] refact login feature

mini-git> branch payment
Created branch: payment

mini-git> switch payment
Switched to branch: payment

mini-git> commit 'add new payment'
[payment 08f33e] add new payment

mini-git> commit 'add another payment'
[payment 2b09cb] add another payment

mini-git> switch main
Switched to branch: main

mini-git> commit 'refact login feature'
[main 22a3b0] refact login feature
```

### 2. 커밋 로그 및 탐색
```bash
mini-git> log
commit c03427 (Tom, 2026-06-22 22:28:30)
    init commit

commit e5078f (Tom, 2026-06-22 22:30:37)
    add login feature

commit 227fec (Tom, 2026-06-22 22:30:42)
    fix login feature

commit 3f1fc0 (Tom, 2026-06-22 22:30:50)
    refact login feature

commit 08f33e (Tom, 2026-06-22 22:31:25)
    add new payment

commit 22a3b0 (Tom, 2026-06-22 22:31:54) [main]
    refact login feature

commit 2b09cb (Tom, 2026-06-22 22:31:30) [payment]
    add another payment

mini-git> path 22a3b0 2b09cb
Path: 22a3b0 -> 3f1fc0 -> 08f33e -> 2b09cb

mini-git> ancestors 22a3b0
commit 3f1fc0 (Tom, 2026-06-22 22:30:50) refact login feature
commit 227fec (Tom, 2026-06-22 22:30:42) fix login feature
commit e5078f (Tom, 2026-06-22 22:30:37) add login feature
commit c03427 (Tom, 2026-06-22 22:28:30) init commit
```

### 3. 검색 및 정렬
```bash
mini-git> search login
Found 4 commit(s):
  - e5078f: add login feature
  - 227fec: fix login feature
  - 3f1fc0: refact login feature
  - 22a3b0: refact login feature

mini-git> search --author=Tom
Found 7 commit(s) by Tom:
  - c03427: init commit
  - e5078f: add login feature
  - 227fec: fix login feature
  - 3f1fc0: refact login feature
  - 08f33e: add new payment
  - 2b09cb: add another payment
  - 22a3b0: refact login feature

mini-git> log --sort-by=author
commit c03427 (Tom, 2026-06-22 22:28:30)
    init commit

commit e5078f (Tom, 2026-06-22 22:30:37)
    add login feature
...
```

### 4. CLI 인터페이스(REPL) 종료
```bash
mini-git> exit
Goodbye!
```

---

## 필수 제출물 및 실행 방법

1. **필수 제출물**
   * `main.py`: Mini Git 핵심 구동 엔트리포인트 파일
   * `README.md`: 프로젝트 명세 및 실행 예제 파일

2. **실행 명령**
   ```bash
   python3 main.py
   ```
