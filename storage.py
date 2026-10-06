"""Penyimpanan SQLite lokal untuk post Reddit hasil scrape."""

import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class SQLiteStorage:
    """Simpan post ke database SQLite lokal (upsert by post_id)."""

    def __init__(self, db_path: str = "reddit_posts.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()
        return self._conn

    def _init_schema(self) -> None:
        if self._conn is None:
            raise RuntimeError("Database belum terhubung. Panggil connect() dulu.")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                post_id       TEXT PRIMARY KEY,
                subreddit     TEXT NOT NULL,
                title         TEXT NOT NULL,
                selftext      TEXT,
                author        TEXT,
                url           TEXT,
                permalink     TEXT,
                score         INTEGER,
                num_comments  INTEGER,
                created_utc   REAL,
                flair         TEXT,
                scraped_at    TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def upsert_many(self, posts: List[Dict[str, Any]]) -> int:
        """Simpan/update banyak post. Return jumlah baris yang ditulis."""
        if not posts or self._conn is None:
            return 0
        scraped_at = datetime.now(timezone.utc).isoformat()
        rows = [
            (
                p["post_id"],
                p["subreddit"],
                p["title"],
                p.get("selftext", ""),
                p.get("author", ""),
                p.get("url", ""),
                p.get("permalink", ""),
                p.get("score", 0),
                p.get("num_comments", 0),
                p.get("created_utc", 0.0),
                p.get("flair", ""),
                scraped_at,
            )
            for p in posts
        ]
        self._conn.executemany(
            """
            INSERT INTO posts (
                post_id, subreddit, title, selftext, author, url, permalink,
                score, num_comments, created_utc, flair, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(post_id) DO UPDATE SET
                score        = excluded.score,
                num_comments = excluded.num_comments,
                flair        = excluded.flair,
                scraped_at   = excluded.scraped_at
            """,
            rows,
        )
        self._conn.commit()
        return len(rows)

    def count(self) -> int:
        if self._conn is None:
            return 0
        cur = self._conn.execute("SELECT COUNT(*) FROM posts")
        return cur.fetchone()[0]

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
