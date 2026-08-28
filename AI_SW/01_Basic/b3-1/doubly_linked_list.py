class Node:
    """이중 연결 리스트의 노드 클래스"""
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    """이중 연결 리스트 클래스"""
    def __init__(self):
        self.head = Node(None)  # Dummy head
        self.tail = Node(None)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def insert_front(self, data):
        """리스트의 맨 앞에 데이터를 삽입합니다."""
        new_node = Node(data)
        self._insert_node(self.head, new_node, self.head.next)
        return new_node

    def insert_back(self, data):
        """리스트의 맨 뒤에 데이터를 삽입합니다."""
        new_node = Node(data)
        self._insert_node(self.tail.prev, new_node, self.tail)
        return new_node

    def _insert_node(self, prev_node, new_node, next_node):
        prev_node.next = new_node
        new_node.prev = prev_node
        new_node.next = next_node
        next_node.prev = new_node
        self._size += 1

    def remove_front(self):
        """리스트의 맨 앞 노드를 삭제하고 반환합니다."""
        if self.is_empty():
            return None
        node = self.head.next
        self.remove_node(node)
        return node

    def remove_back(self):
        """리스트의 맨 뒤 노드를 삭제하고 반환합니다."""
        if self.is_empty():
            return None
        node = self.tail.prev
        self.remove_node(node)
        return node

    def remove_node(self, node):
        """특정 노드를 삭제합니다."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1

    def move_to_front(self, node):
        """특정 노드를 리스트의 맨 앞으로 이동시킵니다."""
        if node == self.head.next:
            return
        # 기존 위치에서 제거 (size 변경 안함)
        node.prev.next = node.next
        node.next.prev = node.prev
        # 맨 앞에 삽입
        first = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = first
        first.prev = node

    def is_empty(self):
        """리스트가 비어있는지 확인합니다."""
        return self._size == 0

    def __len__(self):
        return self._size
