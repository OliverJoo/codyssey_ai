import pytest
from doubly_linked_list import DoublyLinkedList

def test_doubly_linked_list():
    dll = DoublyLinkedList()
    assert len(dll) == 0
    assert dll.is_empty()

    # insert_front
    node1 = dll.insert_front("A")
    assert len(dll) == 1
    assert dll.head.next == node1
    assert dll.tail.prev == node1

    # insert_back
    node2 = dll.insert_back("B")
    assert len(dll) == 2
    assert dll.tail.prev == node2
    assert node1.next == node2
    assert node2.prev == node1

    # move_to_front
    dll.move_to_front(node2)
    assert dll.head.next == node2
    assert node2.next == node1

    # remove_node
    dll.remove_node(node1)
    assert len(dll) == 1
    assert dll.head.next == node2
    assert dll.tail.prev == node2

    # remove_front
    removed = dll.remove_front()
    assert removed == node2
    assert len(dll) == 0
    assert dll.is_empty()

    # remove_back
    node3 = dll.insert_front("C")
    node4 = dll.insert_front("D")
    removed = dll.remove_back()
    assert removed == node3
    assert len(dll) == 1
    assert dll.head.next == node4

if __name__ == '__main__':
    pytest.main(['-v', __file__])
