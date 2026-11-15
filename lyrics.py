"""
Lyrics scraper module using LRCLIB API.
Extracts synced (timestamped LRC) and plain text lyrics.
"""
import urllib.request
import urllib.parse
import json
import re

HEADERS = {
    'User-Agent': 'SpotifyWebScraper/1.0 (Windows NT 10.0; Win64; x64)'
}

def clean_title_for_lyrics(title: str) -> str:
    """Clean track title by removing extra info like '(feat. ...)', '(Remastered)', etc."""
    # Remove features and remasters
    title = re.sub(r'\(feat\..*?\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\[feat\..*?\]', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\(with.*?\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\(.*?remaster.*?\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'- .*?remaster.*?', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\(.*?live.*?\)', '', title, flags=re.IGNORECASE)
    return title.strip()

def parse_synced_lyrics(lrc_text: str):
    """
    Parses LRC format into a structured list of:
    [{ "time": seconds, "time_str": "01:23.45", "text": "Lyric text" }]
    """
    if not lrc_text:
        return []
    
    lines = []
    pattern = re.compile(r'\[(\d{2}):(\d{2}(?:\.\d{1,3})?)\](.*)')
    
    for raw_line in lrc_text.splitlines():
        match = pattern.match(raw_line.strip())
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            total_seconds = minutes * 60 + seconds
            text = match.group(3).strip()
            lines.append({
                "time": round(total_seconds, 2),
                "time_str": f"{minutes:02d}:{int(seconds):02d}",
                "text": text
            })
    return lines

def get_lyrics(track_name: str, artist_name: str = "", duration_seconds: int = 0):
    """
    Fetches lyrics from LRCLIB API.
    Returns:
    {
        "track_name": str,
        "artist_name": str,
        "plain_lyrics": str,
        "synced_lyrics_raw": str,
        "synced_lyrics": list of { "time": float, "time_str": str, "text": str },
        "has_lyrics": bool,
        "is_synced": bool
    }
    """
    clean_track = clean_title_for_lyrics(track_name)
    primary_artist = artist_name.split(',')[0].strip() if artist_name else ""
    
    # Strategy 1: Exact match endpoint /api/get
    params = {
        'track_name': clean_track
    }
    if primary_artist:
        params['artist_name'] = primary_artist
    if duration_seconds > 0:
        params['duration'] = int(duration_seconds)
        
    url = f"https://lrclib.net/api/get?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and (data.get('plainLyrics') or data.get('syncedLyrics')):
                synced_raw = data.get('syncedLyrics') or ""
                return {
                    "track_name": data.get('trackName') or track_name,
                    "artist_name": data.get('artistName') or artist_name,
                    "plain_lyrics": data.get('plainLyrics') or "",
                    "synced_lyrics_raw": synced_raw,
                    "synced_lyrics": parse_synced_lyrics(synced_raw),
                    "has_lyrics": True,
                    "is_synced": bool(synced_raw)
                }
    except Exception:
        pass

    # Strategy 2: Search endpoint /api/search?q=...
    query = f"{clean_track} {primary_artist}".strip()
    search_url = f"https://lrclib.net/api/search?{urllib.parse.urlencode({'q': query})}"
    
    try:
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            results = json.loads(resp.read().decode('utf-8'))
            if results and isinstance(results, list):
                # Pick the best result with syncedLyrics preferred
                best_item = None
                for item in results:
                    if item.get('syncedLyrics'):
                        best_item = item
                        break
                if not best_item:
                    best_item = results[0]
                
                synced_raw = best_item.get('syncedLyrics') or ""
                return {
                    "track_name": best_item.get('trackName') or track_name,
                    "artist_name": best_item.get('artistName') or artist_name,
                    "plain_lyrics": best_item.get('plainLyrics') or "",
                    "synced_lyrics_raw": synced_raw,
                    "synced_lyrics": parse_synced_lyrics(synced_raw),
                    "has_lyrics": bool(best_item.get('plainLyrics') or synced_raw),
                    "is_synced": bool(synced_raw)
                }
    except Exception:
        pass

    return {
        "track_name": track_name,
        "artist_name": artist_name,
        "plain_lyrics": "Lyrics not found for this track.",
        "synced_lyrics_raw": "",
        "synced_lyrics": [],
        "has_lyrics": False,
        "is_synced": False
    }

if __name__ == "__main__":
    test = get_lyrics("Shape of You", "Ed Sheeran")
    print("Found lyrics:", test["has_lyrics"], "Synced:", test["is_synced"])
    print("Total parsed lines:", len(test["synced_lyrics"]))
    if test["synced_lyrics"]:
        print("First 3 lines:", test["synced_lyrics"][:3])
