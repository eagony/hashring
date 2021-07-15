import hashlib

def gen_key(key):
    u"""根据字符串哈希出key值"""
    m = hashlib.md5()
    m.update(key.encode('utf-8'))
    return m.hexdigest()