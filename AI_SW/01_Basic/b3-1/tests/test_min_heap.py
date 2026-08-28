import pytest
from min_heap import MinHeap

def test_min_heap():
    heap = MinHeap()
    assert heap.is_empty()
    
    # push items (expire_at, key)
    heap.push((10, "key1"))
    heap.push((5, "key2"))
    heap.push((20, "key3"))
    heap.push((1, "key4"))
    
    assert heap.size() == 4
    assert heap.peek() == (1, "key4")
    
    # pop items
    assert heap.pop() == (1, "key4")
    assert heap.peek() == (5, "key2")
    assert heap.pop() == (5, "key2")
    
    # push more
    heap.push((15, "key5"))
    assert heap.pop() == (10, "key1")
    assert heap.pop() == (15, "key5")
    assert heap.pop() == (20, "key3")
    
    assert heap.is_empty()
    assert heap.pop() is None

if __name__ == '__main__':
    pytest.main(['-v', __file__])
