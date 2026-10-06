"""Reddit scraper untuk pengumpulan data sentimen pasar.

Mengambil post terbaru dari subreddit yang dikonfigurasi memakai library
resmi `praw` dan mengembalikannya sebagai list of dict (tanpa coupling ke DB).
"""

import os
from typing import Any, Dict, List, Optional

import praw
from dotenv import load_dotenv

DEFAULT_SUBREDDITS = "forex,wallstreetbets,economics,stocks,cryptocurrency"


class RedditScraper:
    """Ambil post terbaru dari satu/beberapa subreddit."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        load_dotenv()
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET", "")
        self.user_agent = user_agent or os.getenv(
            "REDDIT_USER_AGENT", "python:reddit-sentiment-scraper:v1.0"
        )

    def _client(self) -> praw.Reddit:
        if not self.client_id or not self.client_secret:
            raise RuntimeError(
                "REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET belum di-set. "
                "Salin .env.example ke .env lalu isi kredensial Reddit kamu."
            )
        return praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )

    def fetch(
        self,
        subreddits: Optional[List[str]] = None,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """Kembalikan post terbaru sebagai list of dict."""
        subreddits = subreddits or self._parse_subreddits()
        reddit = self._client()
        posts: List[Dict[str, Any]] = []
        for name in subreddits:
            sub = reddit.subreddit(name)
            for submission in sub.new(limit=limit):
                posts.append(self._to_dict(submission))
        return posts

    def _parse_subreddits(self) -> List[str]:
        raw = os.getenv("REDDIT_SUBREDDITS", DEFAULT_SUBREDDITS)
        return [s.strip() for s in raw.split(",") if s.strip()]

    @staticmethod
    def _to_dict(submission) -> Dict[str, Any]:
        return {
            "post_id": submission.id,
            "subreddit": str(submission.subreddit),
            "title": submission.title,
            "selftext": submission.selftext,
            "author": str(submission.author) if submission.author else "[deleted]",
            "url": submission.url,
            "permalink": submission.permalink,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "created_utc": submission.created_utc,
            "flair": submission.link_flair_text or "",
        }
