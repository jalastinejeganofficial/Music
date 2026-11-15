# 🎵 Music - Web Player & Importer

A full-stack web scraper and music player built with Python FastAPI and modern JavaScript, targeting **https://music.youtube.com/**. Scrapes song titles, artists, albums, playlists, high-resolution artwork (`maxresdefault`), direct audio playback streams, and live synchronized karaoke lyrics directly from YouTube Music.

---

## 🚀 Features

- **YouTube Music Web Scraper Engine (`scraper.py`):**
  - Target: `https://music.youtube.com/` (InnerTube `WEB_REMIX` client + yt-dlp).
  - **Tracks:** Scrapes title, artist(s), view counts, duration, high-resolution images (`maxresdefault.jpg`, `hqdefault.jpg`, `mqdefault.jpg`), and direct playable audio stream (`googlevideo.com`).
  - **Playlists:** Scrapes complete YouTube Music playlists (e.g. *Top 100 Music Videos Global*, *Top Hits*, or custom playlist links).
  - **Audio Extraction:** Direct extraction of high-quality audio streaming URLs for seamless web playback.

- **Dual Lyrics Engine (`lyrics.py`):**
  - Scrapes official lyrics directly from YouTube Music's InnerTube browse tabs.
  - Combines with LRCLIB for millisecond-precision synchronized karaoke lyrics (`[mm:ss.xx]`).
  - Interactive karaoke display highlights and smoothly scrolls to the active line in real-time.
  - Click any lyric line to jump the audio directly to that timestamp.

- **Universal Search Engine (`search.py`):**
  - Real-time search across `https://music.youtube.com/youtubei/v1/search`.
  - Returns instant song matches with HD artwork, artist info, and playable audio streams.

- **YouTube Music-Inspired Dark UI:**
  - Sleek dark theme with YouTube Red glow accents (`#FF0000` / `#FF0033`).
  - List View and Album Card Grid View toggle.
  - Bottom sticky audio player with play/pause, seek scrubber, volume control, shuffle, and repeat.
  - **Scraped Metadata Inspector Modal:** View & download extracted images (HD), direct audio stream URL, lyrics JSON, and full raw scraped JSON.

---

## 🛠️ How to Run

1. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python server.py
   ```

3. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

---

## 📋 API Endpoints

- `GET /api/curated` - Featured YouTube Music playlists.
- `POST /api/scrape` - Scrapes any YouTube Music track or playlist URL.
  ```json
  { "url": "https://music.youtube.com/watch?v=JGwWNGJdvx8" }
  ```
- `GET /api/search?q={query}` - Search songs on YouTube Music.
- `GET /api/stream?video_id={id}` - Extract direct playable audio stream.
- `POST /api/import_spotify` - Scrapes Spotify playlist & matches songs for instant playback.
- `GET /api/spotify_presets` - Popular Spotify playlists for 1-click import.
- `GET /api/lyrics?video_id={id}&title={title}&artist={artist}` - Fetch lyrics.
- `GET /api/playlist/{playlist_id}` - Scrape playlist by ID.
- `GET /api/track/{track_id}` - Scrape track by Video ID.

---

## ☁️ Deploy to Render

1. Create a new **Web Service** on [Render](https://render.com/).
2. Connect your GitHub repository: `jalastinejeganofficial/Music`.
3. Render will auto-detect `render.yaml`, or use:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Click **Deploy Web Service**!
