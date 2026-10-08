"""
hdl_db_access — контроль доступа.
Работает самостоятельно.
"""
from __future__ import annotations
import asyncio
import urllib.request
from pathlib import Path

import win32crypt
from winsdk.windows.security.credentials.ui import (
    UserConsentVerifier, UserConsentVerifierAvailability,
    UserConsentVerificationResult,
)

DPAPI_DESC = "HDL_Help_Config"


class ServerFactor:
    def __init__(self, url: str, token_path: Path, timeout: float = 5.0):
        self.url = url
        self.token_path = Path(token_path)
        self.timeout = timeout

    def fetch(self) -> bytes:
        tok = self.token_path.read_text().strip()
        req = urllib.request.Request(self.url, headers={"X-Vault-Token": tok})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read()


class DPAPIFactor:
    def __init__(self, cfg_path: Path):
        self.cfg_path = Path(cfg_path)

    def write(self, data: bytes) -> None:
        blob = win32crypt.CryptProtectData(data, DPAPI_DESC, None, None, None, 0)
        self.cfg_path.write_bytes(blob)

    def read(self) -> bytes:
        raw = self.cfg_path.read_bytes()
        _, plain = win32crypt.CryptUnprotectData(raw, None, None, None, 0)
        return plain


class HelloFactor:
    """Гейт — Windows Hello. Асинхронный, чтобы вызываться внутри asyncio."""
    def __init__(self, message: str = "Разблокировать HDL_Help"):
        self.message = message

    async def verify(self) -> bool:
        avail = await UserConsentVerifier.check_availability_async()
        if avail != UserConsentVerifierAvailability.AVAILABLE:
            return False
        res = await UserConsentVerifier.request_verification_async(self.message)
        return res == UserConsentVerificationResult.VERIFIED


if __name__ == "__main__":
    print("[*] Hello verify:", asyncio.run(HelloFactor().verify()))