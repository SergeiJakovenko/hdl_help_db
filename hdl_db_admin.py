"""
hdl_db_admin — добавление, изменение, удаление записей.
Работает самостоятельно. Перезаписывает только слот "secrets",
не трогая S1/S2/S3. Ключ берётся из уже собранных долей.
"""
from __future__ import annotations
import asyncio
import getpass
import json
import sys
from pathlib import Path

from hdl_db_store import Storage
from hdl_db_codec import decrypt, encrypt, combine3
from hdl_db_access import ServerFactor, DPAPIFactor, HelloFactor
from hdl_db_fallback import verify as verify_fallback

VAULT_DIR  = Path(r"C:\Users\serjak\Documents\HDL_Help")
DB_PATH    = VAULT_DIR / "hdl_help.db"
CFG_PATH   = VAULT_DIR / "hdl_settings.ini"

SCRIPT_DIR = Path(__file__).parent
SERVER_URL = "http://127.0.0.1:8787/share"
SERVER_TOK = SCRIPT_DIR / "server_token.txt"


async def unlock():
    """Возвращает (key, data). Ключ нужен, чтобы потом перезаписать данные."""
    ok = await HelloFactor().verify()
    if not ok:
        print("[*] Windows Hello недоступен. Использую резервный пароль.")
        if not verify_fallback():
            raise SystemExit("[!] Доступ запрещён.")

    st = Storage(DB_PATH)
    s2 = st.get("share2")
    token = st.get("secrets")
    st.close()

    s1 = ServerFactor(SERVER_URL, SERVER_TOK).fetch()
    s3 = DPAPIFactor(CFG_PATH).read()

    key = combine3(s1, s2, s3)
    data = json.loads(decrypt(key, token).decode())
    return key, data


def save(key: bytes, data: dict) -> None:
    st = Storage(DB_PATH)
    st.put("secrets", encrypt(key, json.dumps(data).encode()))
    st.close()


def read_value(name: str) -> str:
    """Если значение не дано в аргументах — спросить через getpass."""
    return getpass.getpass(f"Значение для '{name}': ")


async def main() -> None:
    if len(sys.argv) < 3:
        print("hdl_db_admin.py add <name> [value] | set <name> [value] | remove <name>")
        return

    cmd = sys.argv[1]
    name = sys.argv[2]

    key, data = await unlock()

    if cmd == "add":
        if name in data:
            print(f"[!] '{name}' уже есть. Используй set.")
            return
        value = sys.argv[3] if len(sys.argv) > 3 else read_value(name)
        data[name] = value
        save(key, data)
        print(f"[+] Добавлено: {name} (записей: {len(data)})")

    elif cmd == "set":
        value = sys.argv[3] if len(sys.argv) > 3 else read_value(name)
        existed = name in data
        data[name] = value
        save(key, data)
        print(f"[+] {'Изменено' if existed else 'Добавлено'}: {name} (записей: {len(data)})")

    elif cmd == "remove":
        if name not in data:
            print(f"[!] '{name}' нет.")
            return
        del data[name]
        save(key, data)
        print(f"[+] Удалено: {name} (осталось: {len(data)})")

    else:
        print("hdl_db_admin.py add <name> [value] | set <name> [value] | remove <name>")


if __name__ == "__main__":
    asyncio.run(main())


