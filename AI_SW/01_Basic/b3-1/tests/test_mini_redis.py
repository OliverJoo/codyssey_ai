import pytest
import time
from mini_redis import MiniRedis

def test_mini_redis_basic():
    redis = MiniRedis()
    
    # SET
    assert redis.execute_command('SET key1 val1') == "OK"
    assert redis.execute_command('SET "key2" "val 2"') == "OK"
    
    # GET
    assert redis.execute_command('GET key1') == '"val1"'
    assert redis.execute_command('GET key2') == '"val 2"'
    assert redis.execute_command('GET missing') == "(nil)"
    
    # EXISTS
    assert redis.execute_command('EXISTS key1') == "(integer) 1"
    assert redis.execute_command('EXISTS missing') == "(integer) 0"
    
    # DBSIZE
    assert redis.execute_command('DBSIZE') == "(integer) 2"
    
    # DEL
    assert redis.execute_command('DEL key1') == "(integer) 1"
    assert redis.execute_command('DEL key1') == "(integer) 0"
    assert redis.execute_command('EXISTS key1') == "(integer) 0"
    assert redis.execute_command('DBSIZE') == "(integer) 1"

def test_mini_redis_lru_and_memory():
    redis = MiniRedis()
    
    # config
    assert redis.execute_command('CONFIG SET maxmemory 30') == "OK"
    
    # u:1 is 3 bytes, "Alice" is 5 bytes => 8 bytes
    assert redis.execute_command('SET u:1 "Alice"') == "OK"
    # u:2 is 3 bytes, "Bob" is 3 bytes => 6 bytes
    assert redis.execute_command('SET u:2 "Bob"') == "OK"
    # u:3 is 3 bytes, "Charlie" is 7 bytes => 10 bytes
    assert redis.execute_command('SET u:3 "Charlie"') == "OK"
    
    # Total memory: 8 + 6 + 10 = 24 bytes <= 30
    info = redis.execute_command('INFO memory')
    assert "used_memory:24" in info
    assert "maxmemory:30" in info
    assert "evicted_keys:0" in info
    
    # u:4 is 3 bytes, "David" is 5 bytes => 8 bytes
    # total will be 32 > 30. LRU eviction needed.
    # LRU order currently: u:3, u:2, u:1 (u:1 is oldest)
    # Evict u:1 -> frees 8 bytes. Total = 24 + 8 - 8 = 24 <= 30
    assert redis.execute_command('SET u:4 "David"') == "OK"
    
    info = redis.execute_command('INFO memory')
    assert "used_memory:24" in info
    assert "evicted_keys:1" in info
    assert redis.execute_command('GET u:1') == "(nil)"
    assert redis.execute_command('GET u:2') == '"Bob"'
    
    # test single key too large
    res = redis.execute_command('SET bigkey "a_very_long_string_that_exceeds_thirty_bytes"')
    assert "OOM command not allowed" in res

def test_mini_redis_ttl():
    redis = MiniRedis()
    
    assert redis.execute_command('SET key1 val1') == "OK"
    assert redis.execute_command('EXPIRE key1 1') == "(integer) 1"
    
    assert redis.execute_command('TTL key1') == "(integer) 1"
    
    time.sleep(1.1)
    
    # lazy eviction should happen here
    assert redis.execute_command('GET key1') == "(nil)"
    assert redis.execute_command('EXISTS key1') == "(integer) 0"
    
    # TTL key should return -2
    assert redis.execute_command('TTL key1') == "(integer) -2"

if __name__ == '__main__':
    pytest.main(['-v', __file__])
