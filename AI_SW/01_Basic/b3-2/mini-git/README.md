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

#### 💡 탐색 시나리오의 커밋 그래프 시각화 및 무방향 탐색 원리

이 세션 로그 시나리오에서 생성된 커밋 그래프의 관계는 다음과 같습니다.

```text
              c03427 (init commit)
                 │
              e5078f (add login feature)
                 │
              227fec (fix login feature)
                 │
              3f1fc0 (refact login feature)  <-- 공통 조상 (LCA)
             ╱      ╲
            ╱        ╲
      08f33e          22a3b0 (refact login feature - main HEAD)
        │
      2b09cb (payment HEAD)
```

과제 요구사항에 명시된 대로 **"커밋-부모 연결을 무방향 간선으로 간주"**하여 최단 경로를 탐색하기 때문에, 단방향성 DAG 흐름에 갇히지 않고 `main` 브랜치 HEAD(`22a3b0`)에서 공통 조상인 `3f1fc0`을 거쳐 `payment` 브랜치 HEAD(`2b09cb`)로 오르내리는 `22a3b0 ➔ 3f1fc0 ➔ 08f33e ➔ 2b09cb` 경로를 올바르게 찾아낼 수 있습니다.

#### 🚫 경로가 없는 경우 (No path) 시나리오

두 커밋 사이에 어떤 연결 고리(조상 관계)도 없는 독립된 루트 커밋들이 존재할 때 `No path`가 발생합니다. 이는 Git의 `--orphan` 브랜치 생성과 유사하게, 이전 커밋 이력이 없는 새로운 독립된 커밋 트리를 여러 개 만들었을 때 유도할 수 있습니다.

**시나리오 예시:**

```bash
mini-git> init UserA
Initialized repository.

mini-git> branch orphan-branch
Created branch: orphan-branch

mini-git> commit "Root commit on main"
[main 7a2b1c] Root commit on main

mini-git> switch orphan-branch
Switched to branch: orphan-branch

mini-git> commit "Root commit on orphan-branch"
[orphan-branch 8f3d4e] Root commit on orphan-branch

mini-git> path 7a2b1c 8f3d4e
No path
```

* **원리 설명**: 두 커밋 `7a2b1c`와 `8f3d4e`는 각각 부모 커밋이 없는 독립된 **루트 노드(Root Node)**입니다. 무방향 그래프로 간주하더라도 두 컴포넌트(Component) 간에 연결된 간선이 아예 없기 때문에, 최단 경로 탐색 알고리즘은 연결 고리를 찾지 못하고 `No path`를 올바르게 출력합니다.

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
   * `main_bonus.py`: 보너스 기능이 확장된 엔트리포인트 파일
   * `README.md`: 프로젝트 명세 및 실행 예제 파일
2. **실행 명령**

   * 기본 과제 실행:
     ```bash
     python3 main.py
     ```
   * 보너스 과제 실행:
     ```bash
     python3 main_bonus.py
     ```

---

## Bonus 과제

보너스 과제 요구사항을 반영하여 `main_bonus.py`를 구현하였습니다. 원본 `main.py` 파일의 기존 코드는 수정하지 않고, 상속 및 모듈 가져오기를 통해 기능을 안전하게 확장하였습니다.

### 1. 추가된 보너스 기능 및 명령어

* **Diff (간단 비교)**: `DIFF <file1> <file2>`
  * 두 텍스트 파일을 줄 단위로 비교합니다. 동적 계획법(DP) 기반의 LCS(Longest Common Subsequence) 알고리즘을 사용해 추가된 줄(`+`), 삭제된 줄(`-`), 공통인 줄()을 정확히 판별하여 출력합니다.
* **Merge (브랜치 병합 흉내내기)**: `MERGE <branch_name>`
  * 현재 브랜치의 HEAD와 대상 브랜치의 HEAD를 부모 목록(`parents`)으로 가지는 새로운 Merge Commit을 생성합니다.
* **정렬 알고리즘 성능 비교**: `COMPARE-SORT`
  * 직접 구현한 세 가지 정렬 알고리즘(`Merge Sort`, `Quick Sort`, `Insertion Sort`)의 성능을 비교합니다. 100, 500, 1000, 2000 크기의 난수 배열을 생성해 정렬 실행 시간(ms)을 표 형태로 출력합니다.

### 2. 보너스 기능 실제 실행 기록 (Bonus Session Log)

`main_bonus.py` 프로그램을 기동하여 추가된 보너스 기능들을 실제로 실행해본 결과 로그입니다.

#### A. Diff 및 정렬 알고리즘 비교 테스트

```bash
mini-git> diff test1.txt test2.txt
  Hello World
- This is a test file.
+ This is a modified test file.
  We are verifying the diff algorithm.
+ Welcome to Python.
  Good bye.

mini-git> compare-sort
Size     | Merge Sort (ms)  | Quick Sort (ms)  | Insertion Sort (ms) 
---------------------------------------------------------------------------
100      | 0.0766           | 0.0766           | 0.1044            
500      | 0.4718           | 1.2141           | 3.9218            
1000     | 0.9702           | 1.1478           | 11.8832           
2000     | 2.3658           | 2.4153           | 70.5035
```

#### B. 브랜치 병합 (Merge) 테스트

```bash
mini-git> init UserA
Initialized repository.
Current branch: main
Current user: UserA

mini-git> commit "Initial"
[main 1c47b4] Initial

mini-git> branch branchB
Created branch: branchB

mini-git> commit "commitA"
[main 21b7ab] commitA

mini-git> switch branchB
Switched to branch: branchB

mini-git> commit "commitB"
[branchB 075e63] commitB

mini-git> switch main
Switched to branch: main

mini-git> merge branchB
[main 9783b0] Merge branch 'branchB' into 'main'

mini-git> log
commit 1c47b4 (UserA, 2026-06-27 13:51:33)
    Initial

commit 21b7ab (UserA, 2026-06-27 13:51:33)
    commitA

commit 075e63 (UserA, 2026-06-27 13:51:33) [branchB]
    commitB

commit 9783b0 (UserA, 2026-06-27 13:51:33) [main]
    Merge branch 'branchB' into 'main'
```
