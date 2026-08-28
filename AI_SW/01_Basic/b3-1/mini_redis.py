import time
import sys
from hash_map import HashMap
from doubly_linked_list import DoublyLinkedList
from min_heap import MinHeap

class MiniRedis:
    def __init__(self):
        self.data = HashMap()
        self.lru = DoublyLinkedList()  # 노드의 data는 key를 저장
        self.lru_nodes = HashMap()     # key -> lru_node 매핑을 위해 해시맵 사용
        self.ttl = MinHeap()
        self.ttl_map = HashMap()       # key -> expire_at 매핑
        
        self.maxmemory = 0
        self.used_memory = 0
        self.evicted_keys = 0

    def _get_size(self, text):
        return len(text.encode('utf-8'))

    def _cleanup_expired(self):
        """힙을 이용하여 만료된 키들을 일괄 삭제합니다."""
        now = int(time.time())
        while not self.ttl.is_empty():
            expire_at, key = self.ttl.peek()
            if expire_at <= now:
                self.ttl.pop()
                # 힙에 있는 정보가 최신인지 확인 (덮어쓰기 등으로 TTL이 변경되었을 수 있음)
                actual_expire = self.ttl_map.get(key)
                if actual_expire == expire_at:
                    self._delete(key)
            else:
                break

    def _check_key_expired(self, key):
        """특정 키가 만료되었는지 확인하고 만료되었다면 삭제합니다."""
        expire_at = self.ttl_map.get(key)
        if expire_at is not None and expire_at <= int(time.time()):
            self._delete(key)
            return True
        return False

    def _delete(self, key):
        """내부 삭제 로직: 데이터, LRU, TTL 구조에서 모두 제거합니다."""
        val = self.data.get(key)
        if val is not None:
            self.used_memory -= (self._get_size(key) + self._get_size(val))
            self.data.remove(key)
            
            node = self.lru_nodes.get(key)
            if node:
                self.lru.remove_node(node)
                self.lru_nodes.remove(key)
                
            self.ttl_map.remove(key)
            return 1
        return 0

    def _update_lru(self, key):
        """LRU 리스트에서 해당 키를 맨 앞으로 이동시킵니다."""
        node = self.lru_nodes.get(key)
        if node:
            self.lru.move_to_front(node)

    def _evict_lru(self):
        """LRU 정책에 따라 가장 오래된 키를 제거합니다."""
        if self.lru.is_empty():
            return
        oldest_node = self.lru.tail.prev
        key = oldest_node.data
        self._delete(key)
        self.evicted_keys += 1

    def execute_command(self, cmd_line):
        tokens = self._parse_command(cmd_line)
        if not tokens:
            return ""
        
        cmd = tokens[0].upper()
        self._cleanup_expired()  # 명령 실행 전 만료된 키 정리

        if cmd == "SET":
            return self.cmd_set(tokens)
        elif cmd == "GET":
            return self.cmd_get(tokens)
        elif cmd == "DEL":
            return self.cmd_del(tokens)
        elif cmd == "EXISTS":
            return self.cmd_exists(tokens)
        elif cmd == "DBSIZE":
            return self.cmd_dbsize(tokens)
        elif cmd == "KEYS":
            return self.cmd_keys(tokens)
        elif cmd == "CONFIG":
            return self.cmd_config(tokens)
        elif cmd == "INFO":
            return self.cmd_info(tokens)
        elif cmd == "EXPIRE":
            return self.cmd_expire(tokens)
        elif cmd == "TTL":
            return self.cmd_ttl(tokens)
        else:
            return f"(error) ERR unknown command '{tokens[0]}'"

    def _parse_command(self, cmd_line):
        """따옴표를 고려하여 명령어를 토큰화합니다."""
        tokens = []
        token = ""
        in_quotes = False
        for char in cmd_line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ' ' and not in_quotes:
                if token:
                    tokens.append(token)
                    token = ""
            else:
                token += char
        if token:
            tokens.append(token)
        return tokens

    # Commands Implementation
    def cmd_set(self, tokens):
        if len(tokens) != 3:
            return "(error) ERR wrong number of arguments for 'SET' command"
        key, value = tokens[1], tokens[2]
        
        item_size = self._get_size(key) + self._get_size(value)
        if self.maxmemory > 0 and item_size > self.maxmemory:
            return "(error) OOM command not allowed when used_memory > 'maxmemory'"

        self._check_key_expired(key)
        
        old_val = self.data.get(key)
        if old_val is not None:
            self.used_memory -= self._get_size(old_val)
        else:
            self.used_memory += self._get_size(key)
        self.used_memory += self._get_size(value)

        # 메모리 초과 시 LRU 제거
        if self.maxmemory > 0:
            while self.used_memory > self.maxmemory:
                # 갱신 중인 키가 맨 뒤에 있으면 안되므로 갱신 전 미리 제거
                self._evict_lru()

        self.data.put(key, value)
        
        # LRU 업데이트
        if old_val is not None:
            self._update_lru(key)
            # 기존 TTL 제거 (초기화)
            self.ttl_map.remove(key)
        else:
            node = self.lru.insert_front(key)
            self.lru_nodes.put(key, node)
            
        return "OK"

    def cmd_get(self, tokens):
        if len(tokens) != 2:
            return "(error) ERR wrong number of arguments for 'GET' command"
        key = tokens[1]
        
        if self._check_key_expired(key):
            return "(nil)"
            
        val = self.data.get(key)
        if val is not None:
            self._update_lru(key)
            return f'"{val}"'
        return "(nil)"

    def cmd_del(self, tokens):
        if len(tokens) != 2:
            return "(error) ERR wrong number of arguments for 'DEL' command"
        key = tokens[1]
        self._check_key_expired(key)
        res = self._delete(key)
        return f"(integer) {res}"

    def cmd_exists(self, tokens):
        if len(tokens) != 2:
            return "(error) ERR wrong number of arguments for 'EXISTS' command"
        key = tokens[1]
        if self._check_key_expired(key):
            return "(integer) 0"
        return "(integer) 1" if self.data.contains(key) else "(integer) 0"

    def cmd_dbsize(self, tokens):
        if len(tokens) != 1:
            return "(error) ERR wrong number of arguments for 'DBSIZE' command"
        return f"(integer) {self.data.get_size()}"

    def cmd_keys(self, tokens):
        if len(tokens) != 1:
            return "(error) ERR wrong number of arguments for 'KEYS' command"
        keys = self.data.keys()
        if not keys:
            return "(empty array)"
        res = []
        for i, k in enumerate(keys):
            res.append(f'{i+1}. "{k}"')
        return "\n".join(res)

    def cmd_config(self, tokens):
        if len(tokens) != 4 or tokens[1].upper() != "SET" or tokens[2].lower() != "maxmemory":
            return "(error) ERR wrong number of arguments for 'CONFIG' command"
        try:
            val = int(tokens[3])
            if val < 0:
                raise ValueError
        except ValueError:
            return "(error) ERR value is not an integer or out of range"
        
        self.maxmemory = val
        if self.maxmemory > 0:
            while self.used_memory > self.maxmemory:
                self._evict_lru()
        return "OK"

    def cmd_info(self, tokens):
        if len(tokens) != 2 or tokens[1].lower() != "memory":
            return "(error) ERR wrong number of arguments for 'INFO' command"
        res = [
            f"used_memory:{self.used_memory}",
            f"maxmemory:{self.maxmemory}",
            f"evicted_keys:{self.evicted_keys}"
        ]
        return "\n".join(res)

    def cmd_expire(self, tokens):
        if len(tokens) != 3:
            return "(error) ERR wrong number of arguments for 'EXPIRE' command"
        key = tokens[1]
        try:
            seconds = int(tokens[2])
        except ValueError:
            return "(error) ERR value is not an integer or out of range"

        if self._check_key_expired(key) or not self.data.contains(key):
            return "(integer) 0"

        if seconds <= 0:
            self._delete(key)
            return "(integer) 1"

        expire_at = int(time.time()) + seconds
        self.ttl.push((expire_at, key))
        self.ttl_map.put(key, expire_at)
        return "(integer) 1"

    def cmd_ttl(self, tokens):
        if len(tokens) != 2:
            return "(error) ERR wrong number of arguments for 'TTL' command"
        key = tokens[1]
        
        if self._check_key_expired(key) or not self.data.contains(key):
            return "(integer) -2"
            
        expire_at = self.ttl_map.get(key)
        if expire_at is None:
            return "(integer) -1"
            
        left = expire_at - int(time.time())
        return f"(integer) {left}"

def main():
    redis = MiniRedis()
    while True:
        try:
            cmd_line = input("mini-redis> ")
            if not cmd_line.strip():
                continue
            if cmd_line.strip().lower() in ['exit', 'quit']:
                break
            res = redis.execute_command(cmd_line.strip())
            if res:
                print(res)
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            break

if __name__ == '__main__':
    main()
