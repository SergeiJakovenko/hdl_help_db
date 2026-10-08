"""
hdl_db_store — хранилище статей HDL.
Работает самостоятельно. Тестируется отдельно.
"""
from __future__ import annotations
import hashlib
import sqlite3
from pathlib import Path
from typing import Optional

SLOTS = {
    "secrets":   "compiled_index",
    "share2":    "icon_cache_v1",
    "prefs":     "user_layout_v1",
}

HDL_ARTICLES = [
    ("HDL syntax overview",     "Introduction to Hardware Description Language constructs and basic grammar."),
    ("Entity and architecture", "Entities describe the interface; architectures describe behavior."),
    ("Process and sensitivity", "A process is the basic unit of concurrent behavior in HDL."),
    ("Signal vs variable",      "Signals update at end of delta cycle; variables update immediately."),
    ("Generics and parameters", "Generics parameterize entities at elaboration time."),
    ("Testbench structure",     "A testbench instantiates the DUT and applies stimuli."),
    ("Synthesis constraints",   "Timing constraints guide the synthesizer to meet Fmax."),
    ("Clock domain crossing",   "Use synchronizers for safe signal transfer between domains."),
    ("FSM design patterns",     "One-hot, gray, binary — tradeoffs in state encoding."),
    ("Package and library",     "Packages group declarations; libraries organize packages."),
    ("Resource estimation",     "LUT/FF/BRAM estimation before place and route."),
    ("Timing report reading",   "Slack, arrival, required — interpreting static timing reports."),
]


def _db_key(slot: str) -> str:
    if slot in SLOTS:
        return SLOTS[slot]
    h = hashlib.sha256(slot.encode()).hexdigest()[:8]
    return f"cache_{h}"


class Storage:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(self.path)
        self._con.execute("PRAGMA journal_mode=DELETE")

    def seed_help(self) -> None:
        self._con.executescript("""
            CREATE TABLE IF NOT EXISTS help_articles (
                id INTEGER PRIMARY KEY,
                topic TEXT, content TEXT, updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS help_metadata (
                key TEXT PRIMARY KEY, value BLOB
            );
        """)
        n = self._con.execute("SELECT COUNT(*) FROM help_articles").fetchone()[0]
        if n == 0:
            self._con.executemany(
                "INSERT INTO help_articles (topic, content, updated_at) "
                "VALUES (?, ?, datetime('now'))",
                HDL_ARTICLES,
            )
        self._con.commit()

    def put(self, slot: str, value: bytes) -> None:
        self._con.execute(
            "INSERT OR REPLACE INTO help_metadata (key, value) VALUES (?, ?)",
            (_db_key(slot), value),
        )
        self._con.commit()

    def get(self, slot: str) -> Optional[bytes]:
        row = self._con.execute(
            "SELECT value FROM help_metadata WHERE key = ?", (_db_key(slot),)
        ).fetchone()
        return row[0] if row else None

    def articles(self):
        return self._con.execute(
            "SELECT id, topic, content, updated_at FROM help_articles ORDER BY id"
        ).fetchall()

    def find_article(self, name: str):
        return self._con.execute(
            "SELECT id, topic, content, updated_at FROM help_articles "
            "WHERE topic LIKE ? LIMIT 1",
            (f"%{name}%",)
        ).fetchone()

    def close(self) -> None:
        self._con.close()


if __name__ == "__main__":
    st = Storage(Path("./_demo.db"))
    st.seed_help()
    st.put("secrets", b"hello")
    print("get:", st.get("secrets"))
    print("unknown slot:", st.get("generator_v1"))
    for row in st.articles():
        print(row[0], row[1])
    st.close()