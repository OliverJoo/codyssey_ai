import pytest
from hash_map import HashMap

def test_hash_map():
    hm = HashMap(capacity=4)
    assert hm.get_size() == 0

    # put and get
    hm.put("key1", "value1")
    hm.put("key2", "value2")
    assert hm.get_size() == 2
    assert hm.get("key1") == "value1"
    assert hm.get("key2") == "value2"

    # update
    hm.put("key1", "new_value1")
    assert hm.get("key1") == "new_value1"
    assert hm.get_size() == 2

    # remove
    assert hm.remove("key1") is True
    assert hm.get("key1") is None
    assert hm.get_size() == 1
    assert hm.remove("key1") is False

    # contains
    assert hm.contains("key2") is True
    assert hm.contains("key3") is False

    # keys
    hm.put("key3", "value3")
    keys = hm.keys()
    assert "key2" in keys
    assert "key3" in keys
    assert len(keys) == 2

    # resize test
    for i in range(10):
        hm.put(f"k{i}", f"v{i}")
    
    assert hm.capacity >= 16  # Initial 4 -> 8 -> 16
    for i in range(10):
        assert hm.get(f"k{i}") == f"v{i}"

if __name__ == '__main__':
    pytest.main(['-v', __file__])
