"""
hdl_help_serve — мини-сервер для отдачи справки по HTTP.
Работает самостоятельно.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SHARE_FILE = Path(__file__).parent / "server_share.bin"
TOKEN_FILE = Path(__file__).parent / "server_token.txt"
PORT = 8787

def _share():
    if not SHARE_FILE.exists():
        raise SystemExit("Нет server_share.bin — сначала `hdl_help_cli.py init`.")
    return SHARE_FILE.read_bytes()

def _token():
    if not TOKEN_FILE.exists():
        raise SystemExit("Нет server_token.txt.")
    return TOKEN_FILE.read_text().strip()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/share":
            return self.send_error(404)
        if self.headers.get("X-Vault-Token") != _token():
            return self.send_error(403)
        share = _share()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(share)))
        self.end_headers()
        self.wfile.write(share)

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print(f"[*] HDL Help server: http://127.0.0.1:{PORT}/share")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()