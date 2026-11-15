"""
Spotify Playlist Importer and Analyzer.
Scrapes Spotify playlists and analyzes/matches each song on YouTube Music for playback.
"""
import urllib.request
import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
from search import search_ytm

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

SPOTIFY_PRESETS = [
    {
        "title": "Today's Top Hits",
        "url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
        "tag": "Trending Global"
    },
    {
        "title": "Global Top 50",
        "url": "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF",
        "tag": "Daily Charts"
    },
    {
        "title": "All Out 2010s",
        "url": "https://open.spotify.com/playlist/37i9dQZF1DX5Ejj0EkURtP",
        "tag": "2010s Hits"
    },
    {
        "title": "Rock Classics",
        "url": "https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U",
        "tag": "Rock Anthems"
    },
    {
        "title": "Chill Hits",
        "url": "https://open.spotify.com/playlist/37i9dQZF1DX4WYpdgoIcn6",
        "tag": "Mellow Vibes"
    }
]

def extract_spotify_playlist_id(url_or_id: str) -> str:
    """Extracts the 22-character Spotify playlist ID."""
    clean = url_or_id.strip()
    match = re.search(r'playlist/([a-zA-Z0-9]+)', clean)
    if match:
        return match.group(1)
    uri_match = re.search(r'spotify:playlist:([a-zA-Z0-9]+)', clean)
    if uri_match:
        return uri_match.group(1)
    return clean

def scrape_spotify_playlist_data(url_or_id: str) -> Optional[Dict[str, Any]]:
    """
    Scrapes the playlist title, description, cover image, and track items
    directly from Spotify's web embed.
    """
    pid = extract_spotify_playlist_id(url_or_id)
    embed_url = f"https://open.spotify.com/embed/playlist/{pid}"

    req = urllib.request.Request(embed_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        print(f"Error requesting Spotify embed ({embed_url}): {e}")
        return None

    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not match:
        print("No __NEXT_DATA__ found in Spotify playlist embed.")
        return None

    try:
        data = json.loads(match.group(1))
        entity = data.get('props', {}).get('pageProps', {}).get('state', {}).get('data', {}).get('entity', {})
        
        title = entity.get('title') or entity.get('name') or "Imported Spotify Playlist"
        desc = entity.get('subtitle') or "Imported from Spotify"
        
        # Cover image
        cover_sources = entity.get('coverArt', {}).get('sources', [])
        cover_url = ""
        if cover_sources:
            cover_url = cover_sources[0].get('url', '')
            
        raw_tracks = entity.get('trackList', [])
        parsed_tracks = []
        for t in raw_tracks:
            parsed_tracks.append({
                "title": t.get('title', 'Unknown Title'),
                "artist": t.get('subtitle', '').replace('\xa0', ' '),
                "duration_ms": t.get('duration', 0)
            })

        return {
            "title": title,
            "description": desc,
            "cover": cover_url,
            "total_tracks": len(parsed_tracks),
            "tracks": parsed_tracks
        }
    except Exception as e:
        print(f"Error parsing Spotify JSON data: {e}")
        return None

def match_track_on_ytm(track: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Searches YouTube Music for the Spotify song title and artist.
    Returns a unified track object with playable ID, artwork, and duration.
    """
    title = track.get('title', '')
    artist = track.get('artist', '')
    query = f"{title} {artist}".strip()
    
    try:
        matches = search_ytm(query, limit=1)
        if matches:
            top_match = matches[0]
            return {
                "id": top_match["id"],
                "title": title, # Keep clean Spotify title
                "artist_display": artist or top_match.get("artist_display", ""),
                "artists": [artist] if artist else top_match.get("artists", []),
                "album": "Spotify Import",
                "duration_str": top_match.get("duration_str", "3:30"),
                "audio_url": "", # Lazy loaded when played
                "cover_image": top_match.get("cover_image", ""),
                "cover_image_large": top_match.get("cover_image_large", ""),
                "ytm_url": top_match.get("ytm_url", f"https://music.youtube.com/watch?v={top_match['id']}"),
                "source": "Spotify Import"
            }
    except Exception as e:
        print(f"Error matching track '{query}': {e}")
    return None

def import_and_match_spotify_playlist(url_or_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Main function:
    1. Scrapes the Spotify playlist title, cover, and songs.
    2. Uses ThreadPoolExecutor to match tracks on YouTube Music in parallel.
    3. Returns the complete ready-to-save playlist.
    """
    data = scrape_spotify_playlist_data(url_or_id)
    if not data:
        raise ValueError("Could not scrape Spotify playlist. Please check the URL or ID.")

    raw_tracks = data.get("tracks", [])[:limit]
    
    # Match in parallel with 6 workers
    with ThreadPoolExecutor(max_workers=6) as executor:
        matched = list(executor.map(match_track_on_ytm, raw_tracks))

    valid_tracks = [t for t in matched if t is not None]

    # Use first track's cover if playlist cover was empty
    cover = data.get("cover")
    if not cover and valid_tracks:
        cover = valid_tracks[0].get("cover_image_large")

    return {
        "success": True,
        "playlist_name": data.get("title"),
        "description": data.get("description"),
        "cover": cover,
        "total_scraped": len(raw_tracks),
        "total_matched": len(valid_tracks),
        "tracks": valid_tracks
    }

if __name__ == "__main__":
    print("Testing Spotify Playlist Importer...")
    test_res = import_and_match_spotify_playlist("37i9dQZF1DXcBWIGoYBM5M", limit=5)
    print("Result:", test_res["playlist_name"], f"({test_res['total_matched']} songs matched)")
    for t in test_res["tracks"]:
        print(f" - {t['title']} by {t['artist_display']} -> YTM ID: {t['id']}")
