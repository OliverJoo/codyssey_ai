from doubly_linked_list import DoublyLinkedList

class DynamicArray:
    """동적 배열 구현 (보너스 1)"""
    def __init__(self, capacity=2):
        self.capacity = capacity
        self.size = 0
        self.array = [None] * capacity

    def append(self, value):
        if self.size == self.capacity:
            self._resize()
        self.array[self.size] = value
        self.size += 1

    def get(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")
        return self.array[index]

    def set(self, index, value):
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")
        self.array[index] = value

    def remove(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")
        val = self.array[index]
        for i in range(index, self.size - 1):
            self.array[i] = self.array[i + 1]
        self.array[self.size - 1] = None
        self.size -= 1
        return val

    def _resize(self):
        self.capacity *= 2
        new_array = [None] * self.capacity
        for i in range(self.size):
            new_array[i] = self.array[i]
        self.array = new_array

    def __len__(self):
        return self.size

# 보너스 2: 스택, 큐, 덱 구현 (이중 연결 리스트 재사용)

class Stack(DoublyLinkedList):
    """이중 연결 리스트를 상속받은 스택 구현"""
    def push(self, data):
        self.insert_back(data)

    def pop(self):
        node = self.remove_back()
        return node.data if node else None

    def peek(self):
        if self.is_empty():
            return None
        return self.tail.prev.data

class Queue(DoublyLinkedList):
    """이중 연결 리스트를 상속받은 큐 구현"""
    def enqueue(self, data):
        self.insert_back(data)

    def dequeue(self):
        node = self.remove_front()
        return node.data if node else None

class Deque(DoublyLinkedList):
    """이중 연결 리스트를 상속받은 덱 구현"""
    def append(self, data):
        self.insert_back(data)
        
    def appendleft(self, data):
        self.insert_front(data)
        
    def pop(self):
        node = self.remove_back()
        return node.data if node else None
        
    def popleft(self):
        node = self.remove_front()
        return node.data if node else None

# 보너스 3, 4: 이진 트리 및 BST

class TreeNode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class BST:
    """이진 탐색 트리 구현 (보너스 4)"""
    def __init__(self):
        self.root = None

    def insert(self, key, value=None):
        if not self.root:
            self.root = TreeNode(key, value)
        else:
            self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if key < node.key:
            if node.left is None:
                node.left = TreeNode(key, value)
            else:
                self._insert(node.left, key, value)
        elif key > node.key:
            if node.right is None:
                node.right = TreeNode(key, value)
            else:
                self._insert(node.right, key, value)
        else:
            node.value = value # Update

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None:
            return None
        if key == node.key:
            return node.value
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)
            
    def inorder_traversal(self):
        result = []
        self._inorder(self.root, result)
        return result
        
    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.key)
            self._inorder(node.right, result)

# 보너스 5: Pub/Sub 기능

class PubSub:
    """채널 기반 메시징 (Pub/Sub)"""
    def __init__(self):
        # channel -> list of subscribers (queues)
        self.channels = {}

    def subscribe(self, channel):
        if channel not in self.channels:
            self.channels[channel] = []
        q = Queue()
        self.channels[channel].append(q)
        return q

    def publish(self, channel, message):
        count = 0
        if channel in self.channels:
            for q in self.channels[channel]:
                q.enqueue(message)
                count += 1
        return count
