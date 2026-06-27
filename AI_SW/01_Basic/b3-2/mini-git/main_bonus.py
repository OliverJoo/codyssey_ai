import uuid
import time
import random
from collections import deque

# 기존 main.py 모듈로부터 필요한 클래스와 함수들을 가져옵니다.
# 기존 코드를 일체 수정하지 않고 활용하기 위해 모듈 임포트 방식을 취합니다.
from main import Repository, Commit, merge_sort, require_init, parse_command

# ── 추가 정렬 알고리즘 구현 ─────────────────────────────────────────

def quick_sort(lst, key=lambda x: x):
    """
    분할 정복(Divide and Conquer) 방식의 퀵 정렬(Quick Sort) 알고리즘을 수행합니다.
    기본적으로 리스트의 중간값을 피벗으로 선정하여 분할합니다.
    
    :param lst: 정렬할 대상 리스트
    :param key: 정렬 기준 값을 추출하는 단항 함수
    :return: 정렬된 새로운 리스트
    """
    if len(lst) <= 1:
        return lst
    
    # 중간 위치의 원소를 피벗으로 선택합니다.
    pivot = lst[len(lst) // 2]
    pivot_val = key(pivot)
    
    # 피벗 값을 기준으로 작은 값, 같은 값, 큰 값을 분류합니다.
    left = [x for x in lst if key(x) < pivot_val]
    middle = [x for x in lst if key(x) == pivot_val]
    right = [x for x in lst if key(x) > pivot_val]
    
    # 각 부분 리스트를 재귀적으로 정렬한 후 병합하여 반환합니다.
    return quick_sort(left, key) + middle + quick_sort(right, key)


def insertion_sort(lst, key=lambda x: x):
    """
    삽입 정렬(Insertion Sort) 알고리즘을 수행합니다.
    리스트의 두 번째 원소부터 시작하여 앞선 원소들과 비교하며 적절한 위치에 삽입합니다.
    
    :param lst: 정렬할 대상 리스트
    :param key: 정렬 기준 값을 추출하는 단항 함수
    :return: 정렬된 새로운 리스트
    """
    arr = list(lst)  # 원본 리스트 복사
    for i in range(1, len(arr)):
        curr = arr[i]
        curr_val = key(curr)
        j = i - 1
        
        # 정렬된 이전 영역에서 현재 원소보다 큰 값들을 오른쪽으로 한 칸씩 이동시킵니다.
        while j >= 0 and key(arr[j]) > curr_val:
            arr[j + 1] = arr[j]
            j -= 1
            
        # 알맞은 위치에 현재 원소를 삽입합니다.
        arr[j + 1] = curr
        
    return arr


# ── 보너스 기능을 추가한 확장 저장소 클래스 ──────────────────────────

class BonusRepository(Repository):
    """
    기존 Repository 기능을 상속받아 확장한 클래스입니다.
    Diff(비교), Merge(병합), 정렬 알고리즘 성능 비교(Compare Sort) 기능을 제공합니다.
    """
    def __init__(self):
        super().__init__()

    def cmd_diff(self, file1, file2):
        """
        LCS(Longest Common Subsequence) 알고리즘을 사용하여 두 텍스트 파일을
        줄(line) 단위로 비교하고 추가된 줄(+), 삭제된 줄(-), 공통인 줄( )을 구분하여 출력합니다.
        
        :param file1: 비교할 첫 번째 파일의 경로
        :param file2: 비교할 두 번째 파일의 경로
        """
        try:
            # 두 파일을 UTF-8 인코딩 형식으로 읽어 줄 단위 리스트로 변환합니다.
            with open(file1, 'r', encoding='utf-8') as f1:
                lines1 = [line.rstrip('\n') for line in f1]
            with open(file2, 'r', encoding='utf-8') as f2:
                lines2 = [line.rstrip('\n') for line in f2]
        except FileNotFoundError as e:
            # 대상 파일이 존재하지 않는 경우의 예외 처리
            print(f"Error: File not found - {e.filename}")
            return
        except Exception as e:
            print(f"Error: {e}")
            return

        m, n = len(lines1), len(lines2)
        
        # LCS 기록을 위한 DP 테이블을 초기화합니다.
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if lines1[i-1] == lines2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        # DP 테이블을 역추적하며 두 파일 간의 차이점(diff)을 복원합니다.
        diff_result = []
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and lines1[i-1] == lines2[j-1]:
                # 두 라인이 동일한 경우 (공통 줄)
                diff_result.append(f"  {lines1[i-1]}")
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
                # file2에 새로운 라인이 추가된 경우
                diff_result.append(f"+ {lines2[j-1]}")
                j -= 1
            elif i > 0 and (j == 0 or dp[i][j-1] < dp[i-1][j]):
                # file1에서 기존 라인이 삭제된 경우
                diff_result.append(f"- {lines1[i-1]}")
                i -= 1

        # 역순으로 역추적된 결과를 원래 순서로 정렬하여 화면에 출력합니다.
        diff_result.reverse()
        for line in diff_result:
            print(line)

    @require_init
    def cmd_merge(self, branch_name):
        """
        지정된 브랜치와 현재 브랜치를 병합(Merge)합니다.
        현재 브랜치의 HEAD와 병합 대상 브랜치의 HEAD를 공동 부모로 갖는 새로운 Merge Commit을 생성합니다.
        
        :param branch_name: 병합 대상 브랜치명
        """
        if branch_name not in self.branches:
            print(f"Unknown branch: {branch_name}")
            return
            
        current_hash = self.branches.get(self.head)
        target_hash = self.branches.get(branch_name)

        # 예외 케이스: 병합을 진행할 양측의 커밋이 모두 없는 경우
        if not current_hash and not target_hash:
            print("Both branches have no commits to merge.")
            return
            
        # 예외 케이스: 현재 브랜치에 커밋이 없는 경우 (Fast-forward 형태 병합)
        if not current_hash:
            self.branches[self.head] = target_hash
            print(f"Fast-forward merged branch '{branch_name}' into '{self.head}'.")
            return
            
        # 예외 케이스: 대상 브랜치에 커밋이 없는 경우 (이미 최신)
        if not target_hash:
            print(f"Already up-to-date. Branch '{branch_name}' has no commits.")
            return

        # 예외 케이스: 두 브랜치가 동일한 커밋을 가리키고 있는 경우
        if current_hash == target_hash:
            print("Already up-to-date.")
            return

        # 중복되지 않는 유일한 6자리 해시가 나올 때까지 반복해서 생성합니다.
        while True:
            c_hash = uuid.uuid4().hex[:6]
            if c_hash not in self.commits:
                break

        # 머지 커밋 메시지 설정 및 공동 부모(parents) 지정
        message = f"Merge branch '{branch_name}' into '{self.head}'"
        parents = [current_hash, target_hash]
        
        # 커밋 객체를 생성하여 저장소에 기록합니다.
        merge_commit = Commit(message, self.author, parents, commit_hash=c_hash)
        self.commits[merge_commit.hash] = merge_commit
        self.branches[self.head] = merge_commit.hash
        
        # 인덱스 갱신 (검색을 위함)
        self.index.add_commit(merge_commit)
        print(f"[{self.head} {merge_commit.hash}] {message}")

    def cmd_compare_sort(self):
        """
        직접 구현한 3가지 정렬 알고리즘(Merge Sort, Quick Sort, Insertion Sort)을
        다양한 리스트 크기(100, 500, 1000, 2000)를 대상으로 실행 시간을 비교 측정하여 출력합니다.
        """
        sizes = [100, 500, 1000, 2000]
        print(f"{'Size':<8} | {'Merge Sort (ms)':<16} | {'Quick Sort (ms)':<16} | {'Insertion Sort (ms)':<20}")
        print("-" * 75)
        
        for size in sizes:
            # 1부터 10000 사이의 난수로 이루어진 데이터 리스트 생성
            test_data = [random.randint(1, 10000) for _ in range(size)]
            
            # 1. Merge Sort 성능 측정
            data_copy = list(test_data)
            start_time = time.perf_counter()
            merge_sort(data_copy)
            merge_duration = (time.perf_counter() - start_time) * 1000  # ms 단위
            
            # 2. Quick Sort 성능 측정
            data_copy = list(test_data)
            start_time = time.perf_counter()
            quick_sort(data_copy)
            quick_duration = (time.perf_counter() - start_time) * 1000
            
            # 3. Insertion Sort 성능 측정
            data_copy = list(test_data)
            start_time = time.perf_counter()
            insertion_sort(data_copy)
            insertion_duration = (time.perf_counter() - start_time) * 1000
            
            # 측정 결과 표 형태로 출력
            print(f"{size:<8} | {merge_duration:<16.4f} | {quick_duration:<16.4f} | {insertion_duration:<20.4f}")
        print()


# ── CLI REPL 확장 ──────────────────────────────────────────────

def run_bonus_repl(repo):
    """
    대화형 CLI 인터페이스(REPL)를 기동합니다.
    기존 mini-git 명령어 외에 보너스 명령어인 DIFF, MERGE, COMPARE-SORT를 지원합니다.
    
    :param repo: 명령을 수행할 BonusRepository 인스턴스
    """
    while True:
        try:
            line = input("mini-git> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!"); break
        if not line: continue
        tokens = parse_command(line)
        if not tokens:
            print("Invalid args"); continue
        cmd, args = tokens[0], tokens[1:]
        is_valid = True
        
        # 보너스용 명령어 우선 파싱 처리
        if cmd == "DIFF":
            if len(args) == 2:
                repo.cmd_diff(args[0], args[1])
            else:
                is_valid = False
        elif cmd == "MERGE":
            if len(args) == 1:
                repo.cmd_merge(args[0])
            else:
                is_valid = False
        elif cmd == "COMPARE-SORT":
            if len(args) == 0:
                repo.cmd_compare_sort()
            else:
                is_valid = False
                
        # 기존 main.py 명령어 처리 위임
        elif cmd in ("EXIT", "QUIT"):
            print("Goodbye!"); break
        elif cmd == "INIT":
            if len(args) == 1: repo.cmd_init(args[0])
            else: is_valid = False
        elif cmd == "BRANCH":
            if len(args) == 1: repo.cmd_branch(args[0])
            else: is_valid = False
        elif cmd == "SWITCH":
            if len(args) == 1: repo.cmd_switch(args[0])
            else: is_valid = False
        elif cmd == "COMMIT":
            if args: repo.cmd_commit(" ".join(args))
            else: is_valid = False
        elif cmd == "LOG":
            sort_by = None
            if args:
                if len(args) == 1 and args[0].startswith("--sort-by="):
                    val = args[0].split("=", 1)[1]
                    if val in ("date", "author"):
                        sort_by = val
                    else:
                        is_valid = False
                else:
                    is_valid = False
            if is_valid:
                repo.cmd_log(sort_by)
        elif cmd == "PATH":
            if len(args) == 2: repo.cmd_path(args[0], args[1])
            else: is_valid = False
        elif cmd == "ANCESTORS":
            if len(args) == 1: repo.cmd_ancestors(args[0])
            else: is_valid = False
        elif cmd == "SEARCH":
            if not args:
                is_valid = False
            elif args[0].startswith("--author="):
                repo.cmd_search_author(args[0].split("=", 1)[1])
            else:
                repo.cmd_search(" ".join(args))
        else:
            print(f"Unknown command: {cmd}")
            continue
            
        if not is_valid:
            print("Invalid args")


if __name__ == "__main__":
    # 확장된 BonusRepository를 사용하여 mini-git REPL을 가동합니다.
    repo = BonusRepository()
    run_bonus_repl(repo)
