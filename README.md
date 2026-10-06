# Simple Reddit Scraper

Script mandiri yang cukup simpel untuk mengambil post terbaru dari Reddit dan menyimpannya di SQLite lokal. Sangat cocok sebagai bukti _public repo_ untuk proses pengajuan API Reddit.

## Setup

1. Clone repo ini.
2. Buat _virtual environment_ dan install requirement:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy file environment:
   ```bash
   cp .env.example .env
   ```
   Lalu isi `REDDIT_CLIENT_ID` dan `REDDIT_CLIENT_SECRET` milik kamu.

## Penggunaan

Jalankan scraper melalui CLI:

```bash
# Menarik 25 post terbaru dari subreddit default (forex, wallstreetbets, dll)
python main.py

# Kustomisasi target subreddit, jumlah post, dan nama database:
python main.py --subreddits forex,economics --limit 50 --db data.db
```

Data akan tersimpan secara otomatis dalam bentuk tabel `posts` pada database SQLite yang ditentukan (`reddit_posts.db` secara default).
