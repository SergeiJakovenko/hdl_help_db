"""
hdl_help_cli — CLI для работы с БД справки.
Склеивает кубы. Сам ничего не делает.
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
from pathlib import Path

from hdl_db_store import Storage
from hdl_db_codec import new_key, encrypt, decrypt, split3, combine3
from hdl_db_access import ServerFactor, DPAPIFactor, HelloFactor
from hdl_db_fallback import verify as verify_fallback

VAULT_DIR  = Path(r"C:\Users\serjak\Documents\HDL_Help")
DB_PATH    = VAULT_DIR / "hdl_help.db"
CFG_PATH   = VAULT_DIR / "hdl_settings.ini"

SCRIPT_DIR = Path(__file__).parent
SERVER_URL = "http://127.0.0.1:8787/share"
SERVER_TOK = SCRIPT_DIR / "server_token.txt"
SERVER_S1  = SCRIPT_DIR / "server_share.bin"


def do_init(secrets_file: Path) -> None:
    data = {}
    for line in secrets_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()

    st = Storage(DB_PATH)
    st.seed_help()

    key = new_key()
    st.put("secrets", encrypt(key, json.dumps(data).encode()))

    s1, s2, s3 = split3(key)
    st.put("share2", s2)
    SERVER_S1.write_bytes(s1)
    DPAPIFactor(CFG_PATH).write(s3)
    if not SERVER_TOK.exists():
        SERVER_TOK.write_text(os.urandom(24).hex())
    st.close()

    print(f"[+] Данные → {DB_PATH}")
    print(f"[+] S1     → {SERVER_S1}")
    print(f"[+] S3     → {CFG_PATH}")
    print(f"[!] Удали {secrets_file} после проверки.")


async def do_unlock() -> dict:
    hello_ok = await HelloFactor().verify()
    if not hello_ok:
        print("[*] Windows Hello недоступен. Использую резервный пароль.")
        if not verify_fallback():
            raise SystemExit("[!] Доступ запрещён. Неверный резервный пароль.")

    st = Storage(DB_PATH)
    s2 = st.get("share2")
    token = st.get("secrets")
    st.close()

    s1 = ServerFactor(SERVER_URL, SERVER_TOK).fetch()
    s3 = DPAPIFactor(CFG_PATH).read()

    key = combine3(s1, s2, s3)
    return json.loads(decrypt(key, token).decode())


def show_topics() -> None:
    st = Storage(DB_PATH)
    st.seed_help()
    rows = st.articles()
    st.close()
    if not rows:
        print("[!] Статей нет.")
        return
    for i, t, _, _ in rows:
        print(f"  {i:3d}  {t}")


def show_article(name: str) -> None:
    st = Storage(DB_PATH)
    st.seed_help()
    row = st.find_article(name)
    st.close()
    if not row:
        print(f"[!] Нет статьи по запросу '{name}'")
        return
    i, t, c, u = row
    print(f"# {t}")
    print(f"# id={i}, обновлено {u}")
    print()
    print(c)


def main() -> None:
    if len(sys.argv) < 2:
        print("hdl_help_cli.py init <secrets.txt> | list | show <topic> | entries | get <key>")
        return
    cmd = sys.argv[1]

    if cmd == "init":
        src = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("secrets.txt")
        do_init(src)
        return
    if cmd == "list":
        show_topics()
        return
    if cmd == "show" and len(sys.argv) == 3:
        show_article(sys.argv[2])
        return

    data = asyncio.run(do_unlock())
    if cmd == "entries":
        for k in sorted(data):
            print(" ", k)
    elif cmd == "get" and len(sys.argv) == 3:
        print(data.get(sys.argv[2], "[нет такого ключа]"))
    else:
        print("hdl_help_cli.py init <secrets.txt> | list | show <topic> | entries | get <key>")


if __name__ == "__main__":
    main()