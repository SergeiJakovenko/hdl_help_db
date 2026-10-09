"""
hdl_db_hash — хеширование резервного пароля.
Работает самостоятельно.

    python hdl_db_hash.py set        # задать пароль (спросит скрытно)
    python hdl_db_hash.py check      # проверить пароль
"""
from __future__ import annotations
import getpass
import hashlib
import hmac
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent



HASH_FILE = BASE_DIR /"hdl_settings.hash"
ITERATIONS = 600_000
SALT_LEN = 16
KEY_LEN = 32


def _pbkdf2(password: str, salt: bytes, iterations: int = ITERATIONS) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, KEY_LEN
    )


def save_password(password: str) -> None:
    salt = os.urandom(SALT_LEN)
    digest = _pbkdf2(password, salt)
    blob = f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"
    HASH_FILE.write_text(blob)
    print(f"[+] Хеш записан в {HASH_FILE}")


def verify_password(password: str) -> bool:
    if not HASH_FILE.exists():
        return False
    parts = HASH_FILE.read_text().strip().split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    iterations = int(parts[1])
    salt = bytes.fromhex(parts[2])
    expected = bytes.fromhex(parts[3])
    got = _pbkdf2(password, salt, iterations)
    return hmac.compare_digest(got, expected)


def prompt_and_verify() -> bool:
    """Удобно для импорта из других кубов."""
    pw = getpass.getpass("Резервный пароль: ")
    return verify_password(pw)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "set":
        p1 = getpass.getpass("Новый пароль: ")
        p2 = getpass.getpass("Повтори: ")
        if p1 != p2:
            raise SystemExit("[!] Не совпадают.")
        save_password(p1)
    elif cmd == "check":
        pw = getpass.getpass("Пароль: ")
        print("[+] OK" if verify_password(pw) else "[!] Неверно")
    else:
        print("hdl_db_hash.py set | check")