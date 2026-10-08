"""
hdl_db_codec — кодирование и разделение секрета.
Работает самостоятельно.
"""
from __future__ import annotations
import os
from cryptography.fernet import Fernet

def new_key() -> bytes:
    return Fernet.generate_key()

def encrypt(key: bytes, data: bytes) -> bytes:
    return Fernet(key).encrypt(data)

def decrypt(key: bytes, token: bytes) -> bytes:
    return Fernet(key).decrypt(token)

def split3(secret: bytes) -> tuple[bytes, bytes, bytes]:
    a = os.urandom(len(secret))
    b = os.urandom(len(secret))
    c = bytes(x ^ y ^ z for x, y, z in zip(secret, a, b))
    return a, b, c

def combine3(a: bytes, b: bytes, c: bytes) -> bytes:
    return bytes(x ^ y ^ z for x, y, z in zip(a, b, c))

if __name__ == "__main__":
    k = new_key()
    tok = encrypt(k, b"secret")
    assert decrypt(k, tok) == b"secret"
    a, b, c = split3(k)
    assert combine3(a, b, c) == k
    print("[+] codec cube self-test OK")