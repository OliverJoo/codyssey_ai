import uuid, time, shlex
from collections import deque

# ── 정렬 알고리즘 ──────────────────────────────────────────────
def merge_sort(lst, key=lambda x: x):
    """
    안정 정렬(Stable Sort)인 합병 정렬(Merge Sort)을 수행합니다.
    주어진 리스트를 절반으로 쪼갠 뒤 재귀적으로 정렬하고 병합합니다.
    
    :param lst: 정렬할 대상 리스트
    :param key: 정렬 기준 값을 추출하는 단항 함수
    :return: 정렬된 새로운 리스트
    """
    if len(lst) <= 1: return lst
    mid = len(lst) // 2
    left  = merge_sort(lst[:mid], key)
    right = merge_sort(lst[mid:], key)
    return _merge(left, right, key)

def _merge(left, right, key):
    """
    두 개의 정렬된 리스트(left, right)를 정렬 상태를 유지하며 하나로 병합합니다.
    
    :param left: 정렬된 왼쪽 리스트
    :param right: 정렬된 오른쪽 리스트
    :param key: 정렬 기준 값을 추출하는 단항 함수
    :return: 두 리스트가 병합되어 정렬된 새로운 리스트
    """
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result

# ── 공통 데코레이터 ─────────────────────────────────────────────
def require_init(func):
    """저장소가 초기화되었는지(작성자 등록 여부) 확인하는 데코레이터입니다."""
    def wrapper(self, *args, **kwargs):
        if not self.author:
            print("Repository not initialized."); return
        return func(self, *args, **kwargs)
    return wrapper

# ── 핵심 자료구조 ───────────────────────────────────────────────
class Commit:
    """
    커밋 그래프의 단일 노드를 나타냅니다.
    git의 커밋처럼 메시지, 작성자, 타임스탬프, 그리고 부모 커밋들의 해시 목록(DAG 구성 요소)을 가집니다.
    """
    def __init__(self, message, author, parents=None, commit_hash=None):
        # 고유한 6자리 16진수 문자열 해시를 지정하거나 새로 생성합니다.
        self.hash = commit_hash or uuid.uuid4().hex[:6]
        self.message = message
        self.author = author
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.parents = parents or [] # 다중 부모(예: merge) 지원

class InvertedIndex:
    """
    메시지 내 키워드 및 작성자 정보를 기준으로 커밋 해시들을 빠르게 찾을 수 있도록 돕는 역색인(Inverted Index) 구조입니다.
    """
    def __init__(self):
        self.keyword_index = {} # { keyword (lowercase): set(commit_hashes) }
        self.author_index = {}  # { author: set(commit_hashes) }

    def add_commit(self, commit):
        """커밋의 메시지와 작성자명을 토큰화하여 인덱스에 추가합니다."""
        for token in commit.message.lower().split():
            self.keyword_index.setdefault(token, set()).add(commit.hash)
        self.author_index.setdefault(commit.author, set()).add(commit.hash)

    def search_keyword(self, keyword):
        """특정 키워드가 포함된 메시지를 가진 커밋 해시 집합을 반환합니다."""
        return self.keyword_index.get(keyword.lower(), set())

    def search_author(self, author):
        """특정 작성자가 작성한 커밋 해시 집합을 반환합니다."""
        return self.author_index.get(author, set())

# ── 저장소 ─────────────────────────────────────────────────────
class Repository:
    """
    Mini Git 저장소의 핵심 상태(커밋 기록, 브랜치 목록, HEAD 포인터, 작성자 설정 및 인덱스)와 
    다양한 서브 명령어들의 실행 로직을 처리하는 컨트롤러 클래스입니다.
    """
    def __init__(self):
        self.commits  = {}               # { hash: Commit 객체 }
        self.branches = {}               # { branch_name: 최신 commit_hash }
        self.head     = None             # 현재 활성화된 브랜치 이름 (string)
        self.author   = None             # 현재 세션의 기본 커미터 이름 (string)
        self.index    = InvertedIndex()  # 검색 효율화를 위한 역색인 인스턴스

    def cmd_init(self, user_name):
        """저장소를 새롭게 초기화하고, 기본 작성자명 설정 및 기본 브랜치(main)를 만듭니다."""
        self.__init__()
        self.author = user_name
        self.branches = {"main": None}
        self.head = "main"
        print(f"Initialized repository.\nCurrent branch: main\nCurrent user: {user_name}\n")

    @require_init
    def cmd_branch(self, name):
        """새로운 브랜치를 생성합니다. 신규 브랜치는 현재 HEAD가 가리키는 커밋을 함께 참조합니다."""
        if name in self.branches:
            print(f"Branch already exists: {name}"); return
        self.branches[name] = self.branches.get(self.head)
        print(f"Created branch: {name}")

    @require_init
    def cmd_switch(self, name):
        """현재 활성화된 브랜치(HEAD)를 지정된 브랜치로 전환합니다."""
        if name not in self.branches:
            print(f"Unknown branch: {name}"); return
        self.head = name
        print(f"Switched to branch: {name}")

    @require_init
    def cmd_commit(self, message):
        """새로운 커밋을 생성하고 저장합니다. 현재 브랜치의 마지막 커밋이 부모 커밋이 됩니다."""
        parent_hash = self.branches.get(self.head)
        parents = [parent_hash] if parent_hash else []
        
        # 중복되지 않는 유일한 6자리 해시 생성 보장
        while True:
            c_hash = uuid.uuid4().hex[:6]
            if c_hash not in self.commits:
                break
                
        c = Commit(message, self.author, parents, commit_hash=c_hash)
        self.commits[c.hash] = c
        self.branches[self.head] = c.hash
        self.index.add_commit(c)
        print(f"[{self.head} {c.hash}] {message}")

    @require_init
    def cmd_log(self, sort_by=None):
        """
        저장소 내 모든 커밋 목록을 위상 정렬(Topological Sort)하여 출력합니다.
        기본적으로 부모 커밋이 자식 커밋보다 나중에 출력되는 인과 관계 정렬(Kahn's Algorithm)을 사용합니다.
        
        :param sort_by: 정렬 조건 ('date' -> 시간순 정렬, 'author' -> 작성자 이름순 정렬, None -> 위상 정렬 결과 그대로 유지)
        """
        if not self.commits:
            print("No commits."); return
        
        # 위상 정렬을 위한 진입 차수(in-degree) 및 인접 자식 목록(children) 초기화
        in_degree = {h: 0 for h in self.commits}
        children  = {h: [] for h in self.commits}
        
        # 커밋 그래프 구축: p(부모) -> h(자식) 방향의 간선
        # git의 parents 목록은 자신을 가리키는 부모 해시들이므로,
        # 자식 입장에서 부모 포인터 개수를 세어 진입 차수를 계산합니다.
        for h, c in self.commits.items():
            for p in c.parents:
                if p in self.commits:
                    in_degree[h] += 1
                    children[p].append(h)
                    
        # 진입 차수가 0인 커밋(부모가 없는 루트 커밋들)을 위상 정렬용 큐에 먼저 삽입합니다.
        queue  = deque([h for h, d in in_degree.items() if d == 0])
        result = []
        
        # Kahn 알고리즘을 사용한 위상 정렬 수행
        while queue:
            node = queue.popleft()
            result.append(self.commits[node])
            for ch in children[node]:
                in_degree[ch] -= 1
                if in_degree[ch] == 0:
                    queue.append(ch)
                    
        # 사용자가 지정한 보조 정렬 방식에 따라 merge_sort를 이용해 정렬을 수행합니다.
        # merge_sort는 안정 정렬이므로 위상적 순서를 부분적으로 유지하며 추가 조건으로 정렬합니다.
        if sort_by == "date":
            result = merge_sort(result, key=lambda c: c.timestamp)
        elif sort_by == "author":
            result = merge_sort(result, key=lambda c: c.author)
            
        # 정렬된 커밋들을 형식에 맞춰 출력하며, 해당 커밋을 가리키는 브랜치 라벨도 함께 출력합니다.
        for c in result:
            branch_label = [b for b, h in self.branches.items() if h == c.hash]
            label = f" [{', '.join(branch_label)}]" if branch_label else ""
            print(f"commit {c.hash} ({c.author}, {c.timestamp}){label}")
            print(f"    {c.message}\n")

    @require_init
    def cmd_path(self, h1, h2):
        """
        두 커밋(h1, h2) 사이의 최단 경로(Shortest Path)를 무방향 그래프 상에서 탐색하여 출력합니다.
        동일한 길이의 최단 경로가 여러 개 존재할 경우, 경로 상의 노드들을 조인한 문자열 기준으로 
        사전순(Lexicographical)으로 가장 빠른 경로를 선택하여 출력합니다.
        
        :param h1: 출발지 커밋 해시
        :param h2: 목적지 커밋 해시
        """
        for h in [h1, h2]:
            if h not in self.commits:
                print(f"Unknown commit: {h}"); return
        if h1 == h2:
            print(f"Path: {h1}"); return
            
        # 부모-자식 간 관계를 양방향(무방향) 인접 리스트(adj)로 구축합니다.
        adj = {h: [] for h in self.commits}
        for h, c in self.commits.items():
            for p in c.parents:
                if p in adj:
                    adj[h].append(p); adj[p].append(h)
                    
        # 시작 노드로부터 각 노드에 도달하기 위한 최단 경로의 길이를 기록하는 테이블입니다.
        # 전역 visited 집합을 사용할 때 최단 경로 다수가 선점당하는 문제를 방지하기 위해 사용합니다.
        dist = {h: float('inf') for h in self.commits}
        dist[h1] = 1
        
        queue = deque([[h1]]) # BFS 탐색을 위한 경로 큐 (각 원소는 현재까지의 경로 리스트)
        best_paths = []       # 목적지에 최단 거리로 도달한 모든 경로들을 담을 후보 리스트
        best_len = float('inf') # 발견한 최단 경로의 길이를 보관하는 변수 (기본 무한대)
        
        while queue:
            path = queue.popleft()
            
            # 현재 처리 중인 경로의 길이가 이미 찾은 최단 경로보다 크거나 같다면
            # 큐의 탐색 속성(너비 우선)에 의해 이후 경로들은 모두 최단 경로가 될 수 없으므로 루프를 중단합니다.
            if len(path) >= best_len:
                break
            node = path[-1]
            
            # 인접 노드들을 해시값 기준으로 사전순 정렬한 뒤 순차적으로 방문합니다.
            for nb in merge_sort(adj.get(node, []), key=lambda x: x):
                new_len = len(path) + 1
                
                # 새로운 경로 길이가 이미 도달한 최단 목적지 경로보다 길다면 탐색하지 않습니다.
                if new_len > best_len:
                    continue
                    
                if nb == h2:
                    # 목적지 도달 시 최단 거리를 고정/유지하고, 경로 후보에 추가합니다.
                    best_len = new_len
                    best_paths.append(path + [nb])
                # 해당 노드에 도달한 새로운 거리가 이전에 도달했던 최단 거리 이하인 경우에만 큐에 추가합니다.
                # (중복 노드 방문을 걸러내되, 동일한 길이의 최단 다중 경로는 허용하는 역할)
                elif new_len <= dist.get(nb, float('inf')):
                    dist[nb] = new_len
                    queue.append(path + [nb])
                    
        if not best_paths:
            print("No path"); return
            
        # 후보 최단 경로들 중 문자열 조인 결과("hash1->hash2") 기준 사전순으로 가장 빠른 경로를 선택합니다.
        best = best_paths[0]
        for p in best_paths[1:]:
            if "->".join(p) < "->".join(best): best = p
            
        print("Path: " + " -> ".join(best))

    @require_init
    def cmd_ancestors(self, commit_hash):
        """
        지정된 커밋의 모든 조상(Ancestors) 커밋을 역추적하여 출력합니다.
        너비 우선 탐색(BFS) 방식으로 부모 목록을 순차적으로 탐색합니다.
        
        :param commit_hash: 탐색을 시작할 커밋 해시
        """
        if commit_hash not in self.commits:
            print(f"Unknown commit: {commit_hash}"); return
        visited, queue = set(), deque(self.commits[commit_hash].parents)
        while queue:
            h = queue.popleft()
            if h in visited or h not in self.commits: continue
            visited.add(h)
            c = self.commits[h]
            print(f"commit {c.hash} ({c.author}, {c.timestamp}) {c.message}")
            queue.extend(c.parents)
        if not visited: print("No ancestors.")

    @require_init
    def cmd_search(self, keyword):
        """
        메시지 텍스트 내에서 특정 키워드를 검색하여 매칭된 커밋 목록을 출력합니다.
        역색인(InvertedIndex)을 활용하여 O(1) 수준의 빠른 키워드 조회를 수행합니다.
        
        :param keyword: 검색할 키워드 (대소문자 구분 없음)
        """
        hashes = self.index.search_keyword(keyword)
        if not hashes:
            print(f"No commits found for keyword: '{keyword}'"); return
        print(f"Found {len(hashes)} commit(s):")
        for h in hashes:
            c = self.commits[h]
            print(f"  - {c.hash}: {c.message}")

    @require_init
    def cmd_search_author(self, author):
        """
        특정 작성자(Author)가 작성한 모든 커밋 목록을 출력합니다.
        역색인(InvertedIndex)을 활용하여 빠르게 필터링합니다.
        
        :param author: 검색할 작성자 이름 (대소문자 및 띄어쓰기 매칭 필요)
        """
        hashes = self.index.search_author(author)
        if not hashes:
            print(f"No commits found for author: '{author}'"); return
        print(f"Found {len(hashes)} commit(s) by {author}:")
        for h in hashes:
            c = self.commits[h]
            print(f"  - {c.hash}: {c.message}")

# ── CLI REPL ───────────────────────────────────────────────────
def parse_command(line):
    """
    사용자가 입력한 한 줄의 명령어를 쉘(shell) 구문 규칙에 따라 파싱하여 토큰 목록으로 반환합니다.
    shlex.split을 사용하여 공백 기준 분리 및 겹따옴표를 통한 인자 그룹화를 올바르게 지원합니다.
    
    :param line: 입력 원본 문자열
    :return: 첫 단어가 대문자로 정규화된 토큰 리스트. 파싱 실패 시 빈 리스트.
    """
    try:
        tokens = shlex.split(line.strip())
    except ValueError:
        return []
    if not tokens: return []
    tokens[0] = tokens[0].upper() # 명령어 대문자화로 통일
    return tokens

def run_repl(repo):
    """
    대화형 CLI 인터페이스(REPL)를 실행하여 사용자의 개별 입력을 처리합니다.
    사용자가 QUIT 혹은 EXIT를 입력하거나 Ctrl+C/Ctrl+D를 입력할 때까지 지속해서 대기합니다.
    
    :param repo: 명령을 실행할 대상 Repository 인스턴스
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
        
        if cmd in ("EXIT", "QUIT"):
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
    repo = Repository()
    run_repl(repo)