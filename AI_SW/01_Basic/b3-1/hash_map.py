from doubly_linked_list import DoublyLinkedList

class HashMap:
    """체이닝 방식을 이용한 해시맵 (이중 연결 리스트 사용)"""
    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        self.buckets = [DoublyLinkedList() for _ in range(capacity)]

    def _hash(self, key):
        """직접 설계한 해시 함수 (다항식 롤링 해시)"""
        if not isinstance(key, str):
            key = str(key)
        hash_val = 0
        p = 31
        m = 10**9 + 9
        p_pow = 1
        for char in key:
            hash_val = (hash_val + ord(char) * p_pow) % m
            p_pow = (p_pow * p) % m
        return hash_val % self.capacity

    def put(self, key, value):
        """키와 값을 저장합니다. 이미 존재하는 키면 값을 업데이트합니다."""
        bucket_idx = self._hash(key)
        bucket = self.buckets[bucket_idx]

        # 이미 존재하는 키인지 확인
        curr = bucket.head.next
        while curr != bucket.tail:
            k, _ = curr.data
            if k == key:
                curr.data = (key, value)
                return
            curr = curr.next

        # 새로운 키 삽입
        bucket.insert_back((key, value))
        self.size += 1

        # 로드 팩터 확인 및 리사이즈
        if self.size / self.capacity > 0.75:
            self._resize()

    def _resize(self):
        """버킷 배열을 2배 확장하고 데이터를 재해싱합니다."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [DoublyLinkedList() for _ in range(self.capacity)]
        self.size = 0

        for bucket in old_buckets:
            curr = bucket.head.next
            while curr != bucket.tail:
                k, v = curr.data
                self.put(k, v)
                curr = curr.next

    def get(self, key):
        """키에 해당하는 값을 반환합니다. 없으면 None을 반환합니다."""
        bucket_idx = self._hash(key)
        bucket = self.buckets[bucket_idx]

        curr = bucket.head.next
        while curr != bucket.tail:
            k, v = curr.data
            if k == key:
                return v
            curr = curr.next
        return None

    def remove(self, key):
        """키에 해당하는 데이터를 삭제합니다. (삭제 성공 시 True 반환, 실패 시 False 반환)"""
        bucket_idx = self._hash(key)
        bucket = self.buckets[bucket_idx]

        curr = bucket.head.next
        while curr != bucket.tail:
            k, _ = curr.data
            if k == key:
                bucket.remove_node(curr)
                self.size -= 1
                return True
            curr = curr.next
        return False

    def contains(self, key):
        """키가 존재하는지 확인합니다."""
        return self.get(key) is not None

    def keys(self):
        """저장된 모든 키를 리스트 형태로 반환합니다."""
        result = []
        # 요구사항: 내장 리스트는 반환/출력을 위한 용도로는 사용 가능 (내장 컬렉션을 핵심 저장소로 쓰는 것만 금지)
        for bucket in self.buckets:
            curr = bucket.head.next
            while curr != bucket.tail:
                k, _ = curr.data
                result.append(k)
                curr = curr.next
        return result

    def get_size(self):
        """현재 저장된 요소의 개수를 반환합니다."""
        return self.size
