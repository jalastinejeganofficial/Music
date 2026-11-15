"""
YouTube Music Web Scraper & Music Player - FastAPI Server.
Includes Spotify Playlist Importer and Analyzer.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn

from scraper import (
    scrape_any_ytm,
    scrape_track,
    scrape_playlist,
    get_audio_stream_url,
    CURATED_PLAYLISTS
)
from search import search_ytm
from spotify_importer import (
    import_and_match_spotify_playlist,
    SPOTIFY_PRESETS
)

app = FastAPI(title="YouTube Music Web Scraper & Player API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str

class SpotifyImportRequest(BaseModel):
    url: str
    limit: int = 50

# In-memory cache for home music
_HOME_CACHE = []

@app.get("/api/home")
async def get_home_music():
    """Returns a rich set of top songs for the Home view."""
    global _HOME_CACHE
    if _HOME_CACHE:
        return {"success": True, "tracks": _HOME_CACHE}
    
    try:
        pl = scrape_playlist("PL4fGSI1pDJn6puJdseH2Rt9sMvt9E2M4i")
        tracks = pl.get("tracks", [])
        if tracks:
            _HOME_CACHE = tracks[:50]
            return {"success": True, "tracks": _HOME_CACHE}
    except Exception as e:
        print(f"Error loading home playlist: {e}")

    try:
        results = search_ytm("Top Hits 2024", limit=30)
        _HOME_CACHE = results
        return {"success": True, "tracks": results}
    except Exception as e:
        return {"success": False, "tracks": [], "error": str(e)}

@app.get("/api/search")
async def search_endpoint(q: str = Query(..., min_length=1)):
    """Search for music on https://music.youtube.com/ with live query."""
    try:
        results = search_ytm(q, limit=25)
        return {"success": True, "query": q, "count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream")
async def stream_endpoint(video_id: str = Query(...)):
    """Extract direct playable audio streaming URL for a YouTube Music track."""
    try:
        stream_url = get_audio_stream_url(video_id)
        if stream_url:
            return {"success": True, "audio_url": stream_url}
        else:
            return {"success": False, "audio_url": "", "error": "Stream not found"}
    except Exception as e:
        return {"success": False, "audio_url": "", "error": str(e)}

@app.get("/api/spotify_presets")
async def get_spotify_presets():
    """Returns popular Spotify playlists available for instant 1-click import."""
    return {"presets": SPOTIFY_PRESETS}

@app.post("/api/import_spotify")
async def import_spotify_endpoint(req: SpotifyImportRequest):
    """
    Scrapes a Spotify playlist (by URL or ID), analyzes all song names,
    matches them to YouTube Music streams in parallel, and returns the playlist.
    """
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="Spotify playlist URL or ID is required")
        
    try:
        result = import_and_match_spotify_playlist(req.url.strip(), limit=req.limit)
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "message": "Failed to import Spotify playlist"}
        )

# Static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "YouTube Music Scraper Server running."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
