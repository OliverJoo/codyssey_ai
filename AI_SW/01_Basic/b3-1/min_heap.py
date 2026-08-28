class MinHeap:
    """만료 시간(TTL) 관리를 위한 최소 힙"""
    def __init__(self):
        self.heap = []

    def push(self, item):
        """새로운 요소를 힙에 추가합니다."""
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        """가장 작은 요소를 제거하고 반환합니다."""
        if self.is_empty():
            return None
        
        # 첫 요소와 마지막 요소를 교환
        self._swap(0, len(self.heap) - 1)
        # 마지막 요소(최소값) 추출
        min_item = self.heap.pop()
        
        # 새로운 루트를 기준으로 힙 속성 복원
        if not self.is_empty():
            self._heapify_down(0)
            
        return min_item

    def peek(self):
        """가장 작은 요소를 제거하지 않고 반환합니다."""
        if self.is_empty():
            return None
        return self.heap[0]

    def _heapify_up(self, index):
        """요소를 위로 이동시키며 힙 속성을 유지합니다."""
        parent_index = (index - 1) // 2
        # 부모가 존재하고 현재 노드가 부모보다 작을 때 교환
        while index > 0 and self.heap[index] < self.heap[parent_index]:
            self._swap(index, parent_index)
            index = parent_index
            parent_index = (index - 1) // 2

    def _heapify_down(self, index):
        """요소를 아래로 이동시키며 힙 속성을 유지합니다."""
        size = len(self.heap)
        while True:
            left_child = 2 * index + 1
            right_child = 2 * index + 2
            smallest = index

            if left_child < size and self.heap[left_child] < self.heap[smallest]:
                smallest = left_child

            if right_child < size and self.heap[right_child] < self.heap[smallest]:
                smallest = right_child

            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break

    def _swap(self, i, j):
        """두 인덱스의 요소를 교환합니다."""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def size(self):
        """힙에 저장된 요소의 개수를 반환합니다."""
        return len(self.heap)

    def is_empty(self):
        """힙이 비어있는지 확인합니다."""
        return len(self.heap) == 0
