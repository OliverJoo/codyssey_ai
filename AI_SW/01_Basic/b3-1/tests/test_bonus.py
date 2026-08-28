import pytest
from bonus import DynamicArray, Stack, Queue, Deque, BST, PubSub

def test_dynamic_array():
    arr = DynamicArray()
    arr.append(10)
    arr.append(20)
    assert len(arr) == 2
    assert arr.get(0) == 10
    assert arr.get(1) == 20
    
    # 2배 확장 확인
    arr.append(30)
    assert len(arr) == 3
    assert arr.capacity >= 4
    
    # set & remove
    arr.set(0, 100)
    assert arr.get(0) == 100
    
    val = arr.remove(1)
    assert val == 20
    assert len(arr) == 2
    assert arr.get(1) == 30

def test_stack_queue_deque():
    # Stack
    s = Stack()
    s.push(1)
    s.push(2)
    assert s.pop() == 2
    assert s.peek() == 1
    
    # Queue
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    assert q.dequeue() == 1
    assert q.dequeue() == 2
    
    # Deque
    dq = Deque()
    dq.append(1)
    dq.appendleft(0)
    assert dq.pop() == 1
    assert dq.popleft() == 0

def test_bst():
    bst = BST()
    bst.insert(5, "five")
    bst.insert(3, "three")
    bst.insert(7, "seven")
    
    assert bst.search(3) == "three"
    assert bst.search(10) is None
    
    assert bst.inorder_traversal() == [3, 5, 7]

def test_pubsub():
    ps = PubSub()
    q1 = ps.subscribe("channel_1")
    q2 = ps.subscribe("channel_1")
    
    count = ps.publish("channel_1", "Hello")
    assert count == 2
    assert q1.dequeue() == "Hello"
    assert q2.dequeue() == "Hello"

if __name__ == '__main__':
    pytest.main(['-v', __file__])
