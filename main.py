"""CLI: ambil post Reddit lalu simpan ke SQLite.

Contoh:
    python main.py
    python main.py --subreddits forex,wallstreetbets --limit 50 --db data.db
"""

import argparse
import sys
from typing import List, Optional

from scraper import RedditScraper
from storage import SQLiteStorage


def parse_subreddits(raw: Optional[str]) -> Optional[List[str]]:
    if not raw:
        return None
    return [s.strip() for s in raw.split(",") if s.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape post Reddit lalu simpan ke SQLite"
    )
    parser.add_argument(
        "--subreddits",
        default=None,
        help="subreddit dipisah koma, mis. forex,wallstreetbets",
    )
    parser.add_argument(
        "--limit", type=int, default=25, help="jumlah post per subreddit (default 25)"
    )
    parser.add_argument(
        "--db", default="reddit_posts.db", help="path SQLite (default reddit_posts.db)"
    )
    args = parser.parse_args()

    scraper = RedditScraper()
    storage = SQLiteStorage(args.db)
    storage.connect()

    try:
        subreddits = parse_subreddits(args.subreddits)
        target = subreddits or scraper._parse_subreddits()
        print(f"[*] Mengambil {args.limit} post per subreddit dari: {', '.join(target)}")
        posts = scraper.fetch(subreddits=subreddits, limit=args.limit)
        saved = storage.upsert_many(posts)
        print(
            f"[+] Berhasil ambil {len(posts)} post, tersimpan {saved} "
            f"(total di db: {storage.count()})."
        )
    except Exception as exc:
        print(f"[-] Error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        storage.close()


if __name__ == "__main__":
    main()
