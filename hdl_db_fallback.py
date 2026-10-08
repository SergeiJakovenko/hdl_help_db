"""
hdl_db_fallback — резервный фактор.
Проверяет пароль через PBKDF2-хеш (см. hdl_db_hash).
"""
from hdl_db_hash import prompt_and_verify


def verify() -> bool:
    return prompt_and_verify()


if __name__ == "__main__":
    print("[*] Fallback verify:", verify())