"""
YouTube Music Web Scraper Engine (https://music.youtube.com/)
Scrapes titles, artists, albums, playlists, high-resolution cover images,
direct audio playback streams, and lyrics directly from YouTube Music.
"""
import urllib.request
import urllib.parse
import json
import re
from typing import Dict, Any, Optional, List
import yt_dlp
from lyrics import get_lyrics, parse_synced_lyrics

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://music.youtube.com',
    'Referer': 'https://music.youtube.com/'
}

YTM_CLIENT = {
    'clientName': 'WEB_REMIX',
    'clientVersion': '1.20240101.01.00',
    'hl': 'en',
    'gl': 'US'
}

CURATED_PLAYLISTS = [
    {
        "id": "PL4fGSI1pDJn6puJdseH2Rt9sMvt9E2M4i",
        "title": "Top 100 Music Videos Global",
        "description": "The most popular music videos trending globally on YouTube Music.",
        "cover": "https://i.ytimg.com/vi/JGwWNGJdvx8/hqdefault.jpg",
        "tag": "Global Charts"
    },
    {
        "id": "PLFPg_IUxhnZNT9h_Fj1w16_oK0eDqf4a3",
        "title": "Top Hits 2024 - 2025",
        "description": "Chart-topping international hits and trending tracks.",
        "cover": "https://i.ytimg.com/vi/4NRXx6U8ABQ/hqdefault.jpg",
        "tag": "Trending"
    },
    {
        "id": "PLDIoUOhQQPlX30PeEbVMY1r6mWYbVsbG6",
        "title": "Pop Hits Today",
        "description": "The best mainstream pop releases and viral hits.",
        "cover": "https://i.ytimg.com/vi/kffacxfA7G4/hqdefault.jpg",
        "tag": "Pop"
    },
    {
        "id": "PLhSz9COb3TZ4yQ7q51v5K4fXG6a43H2B4",
        "title": "Acoustic & Chill Vibes",
        "description": "Relaxing, acoustic and lo-fi melodies to unwind.",
        "cover": "https://i.ytimg.com/vi/2Vv-BfVoq4g/hqdefault.jpg",
        "tag": "Chill"
    }
]

# Audio Stream URL Cache to avoid repeated yt-dlp calls
_STREAM_CACHE: Dict[str, Dict[str, Any]] = {}

def format_duration(seconds: int) -> str:
    """Format duration in seconds to MM:SS."""
    if not seconds:
        return "3:00"
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"

def parse_ytm_url(input_str: str) -> Dict[str, str]:
    """
    Parses various YouTube Music or standard YouTube URLs/IDs.
    Supports:
    - https://music.youtube.com/watch?v=4NRXx6U8ABQ
    - https://music.youtube.com/playlist?list=PL4fGSI1pDJn6puJdseH2Rt9sMvt9E2M4i
    - https://www.youtube.com/watch?v=...
    - youtu.be/...
    - Bare 11-char video ID or playlist ID
    """
    clean_str = input_str.strip()
    
    # 1. Check for playlist URL
    pl_match = re.search(r'[?&]list=([a-zA-Z0-9_\-]+)', clean_str)
    if pl_match:
        return {"type": "playlist", "id": pl_match.group(1)}
        
    # 2. Check for watch URL with video ID
    vid_match = re.search(r'(?:v=|youtu\.be/|embed/|watch/)([a-zA-Z0-9_\-]{11})', clean_str)
    if vid_match:
        return {"type": "track", "id": vid_match.group(1)}
        
    # 3. Check if input is a playlist ID (typically starts with PL, RD, VL)
    if clean_str.startswith('PL') or clean_str.startswith('RD') or clean_str.startswith('VL'):
        return {"type": "playlist", "id": clean_str}

    # 4. Check if bare 11-character video ID
    if re.fullmatch(r'[a-zA-Z0-9_\-]{11}', clean_str):
        return {"type": "track", "id": clean_str}
        
    return {"type": "unknown", "id": clean_str}

def call_innertube(endpoint: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to query YouTube Music InnerTube endpoints."""
    url = f"https://music.youtube.com/youtubei/v1/{endpoint}"
    full_body = {
        'context': {'client': YTM_CLIENT},
        **body
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(full_body).encode('utf-8'),
        headers=HEADERS
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_audio_stream_url(video_id: str) -> str:
    """
    Extracts direct playable audio streaming URL for a YouTube Music track.
    Cached for fast repeated access.
    """
    if video_id in _STREAM_CACHE:
        return _STREAM_CACHE[video_id].get("stream_url", "")

    url = f"https://music.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'js_runtimes': {'node': {}},
        'noplaylist': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info.get('url', '')
            if stream_url:
                _STREAM_CACHE[video_id] = {
                    "stream_url": stream_url,
                    "title": info.get('title'),
                    "duration": info.get('duration')
                }
                return stream_url
    except Exception as e:
        print(f"Error extracting audio stream for {video_id}: {e}")

    return ""

def scrape_ytm_lyrics(video_id: str, title: str = "", artist: str = "") -> Dict[str, Any]:
    """
    Extracts lyrics for a YouTube Music song.
    Checks YouTube Music official lyrics endpoint first, with synchronized LRCLIB fallback.
    """
    official_lyrics = ""
    try:
        next_data = call_innertube('next', {'videoId': video_id})
        tabs = next_data.get('contents', {}).get('singleColumnMusicWatchNextResultsRenderer', {})\
            .get('tabbedRenderer', {}).get('watchNextTabbedResultsRenderer', {}).get('tabs', [])
        
        lyrics_browse_id = None
        for t in tabs:
            tab_renderer = t.get('tabRenderer', {})
            if tab_renderer.get('title') == 'Lyrics':
                lyrics_browse_id = tab_renderer.get('endpoint', {}).get('browseEndpoint', {}).get('browseId')
                break
                
        if lyrics_browse_id:
            browse_data = call_innertube('browse', {'browseId': lyrics_browse_id})
            sec = browse_data.get('contents', {}).get('sectionListRenderer', {}).get('contents', [])
            if sec:
                runs = sec[0].get('musicDescriptionShelfRenderer', {}).get('description', {}).get('runs', [])
                official_lyrics = "".join(r.get('text', '') for r in runs).strip()
    except Exception as e:
        print(f"Error fetching YouTube Music native lyrics for {video_id}: {e}")

    # Synchronized lyrics from LRCLIB
    clean_title = re.sub(r'\(.*?\)', '', title).replace('Official Music Video', '').replace('Official Video', '').strip()
    sync_data = get_lyrics(clean_title or title, artist)
    
    return {
        "official_lyrics": official_lyrics,
        "plain_lyrics": sync_data.get('plain_lyrics') or official_lyrics or "Lyrics not available.",
        "synced_lyrics": sync_data.get('synced_lyrics', []),
        "has_lyrics": bool(official_lyrics or sync_data.get('has_lyrics')),
        "is_synced": bool(sync_data.get('is_synced')),
        "source": "YouTube Music & LRCLIB"
    }

def scrape_track(video_id: str, resolve_stream: bool = True) -> Dict[str, Any]:
    """
    Scrapes full song details from https://music.youtube.com/watch?v={video_id}:
    Title, artists, album, duration, high-res images, direct audio stream, lyrics.
    """
    title = ""
    artist = ""
    album = ""
    duration_sec = 0

    try:
        next_data = call_innertube('next', {'videoId': video_id})
        up_next = next_data.get('contents', {}).get('singleColumnMusicWatchNextResultsRenderer', {})\
            .get('tabbedRenderer', {}).get('watchNextTabbedResultsRenderer', {}).get('tabs', [])
        if up_next:
            tab_content = up_next[0].get('tabRenderer', {}).get('content', {})
            queue_items = tab_content.get('musicQueueRenderer', {}).get('content', {})\
                .get('playlistPanelRenderer', {}).get('contents', [])
            if queue_items:
                first_item = queue_items[0].get('playlistPanelVideoRenderer', {})
                title = "".join(r.get('text', '') for r in first_item.get('title', {}).get('runs', []))
                sub_runs = first_item.get('longBylineText', {}).get('runs', [])
                artist = "".join(r.get('text', '') for r in sub_runs)
                duration_text = first_item.get('lengthText', {}).get('runs', [{}])[0].get('text', '')
                if ':' in duration_text:
                    parts = duration_text.split(':')
                    duration_sec = int(parts[0]) * 60 + int(parts[1])
    except Exception as e:
        print(f"InnerTube track info fallback for {video_id}: {e}")

    if not title:
        try:
            ydl_opts = {'quiet': True, 'extract_flat': True, 'js_runtimes': {'node': {}}}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://music.youtube.com/watch?v={video_id}", download=False)
                title = info.get('title', 'Unknown Title')
                artist = info.get('uploader') or info.get('artist') or 'Unknown Artist'
                duration_sec = info.get('duration', 0)
        except Exception:
            title = f"YouTube Music Track ({video_id})"
            artist = "YouTube Music"

    images = {
        "large": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        "medium": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
    }

    stream_url = ""
    if resolve_stream:
        stream_url = get_audio_stream_url(video_id)

    lyrics_data = scrape_ytm_lyrics(video_id, title, artist)

    return {
        "id": video_id,
        "type": "track",
        "title": title,
        "artist_display": artist,
        "artists": [a.strip() for a in artist.split('•')[0].split(',') if a.strip()] if artist else [artist],
        "album": album or "YouTube Music Release",
        "duration_ms": duration_sec * 1000,
        "duration_str": format_duration(duration_sec),
        "duration_seconds": duration_sec,
        "ytm_url": f"https://music.youtube.com/watch?v={video_id}",
        "audio_url": stream_url,
        "has_audio": bool(stream_url),
        "cover_images": images,
        "cover_image_large": images["large"],
        "cover_image_medium": images["medium"],
        "cover_image_small": images["thumbnail"],
        "lyrics": lyrics_data
    }

def scrape_playlist(playlist_id: str) -> Dict[str, Any]:
    """
    Scrapes full playlist from https://music.youtube.com/playlist?list={playlist_id}:
    Playlist title, description, cover image, and all track items.
    """
    browse_id = playlist_id if playlist_id.startswith('VL') else f"VL{playlist_id}"
    data = call_innertube('browse', {'browseId': browse_id})

    header = data.get('header', {}).get('musicDetailHeaderRenderer') or \
             data.get('header', {}).get('musicResponsiveHeaderRenderer') or {}
             
    title = "".join(r.get('text', '') for r in header.get('title', {}).get('runs', [])) or "YouTube Music Playlist"
    subtitle = "".join(r.get('text', '') for r in header.get('subtitle', {}).get('runs', []))
    desc = "".join(r.get('text', '') for r in header.get('description', {}).get('musicDescriptionShelfRenderer', {}).get('description', {}).get('runs', []))
    
    thumbs = header.get('thumbnail', {}).get('croppedSquareThumbnailRenderer', {}).get('thumbnail', {}).get('thumbnails', [])
    if not thumbs:
        thumbs = header.get('thumbnail', {}).get('musicThumbnailRenderer', {}).get('thumbnail', {}).get('thumbnails', [])
    cover_large = thumbs[-1].get('url', '') if thumbs else "https://i.ytimg.com/vi/JGwWNGJdvx8/maxresdefault.jpg"

    parsed_tracks = []
    sec = data.get('contents', {}).get('twoColumnBrowseResultsRenderer') or \
          data.get('contents', {}).get('singleColumnBrowseResultsRenderer') or {}
          
    shelf_contents = []
    if 'secondaryContents' in sec:
        shelves = sec['secondaryContents'].get('sectionListRenderer', {}).get('contents', [])
        for s in shelves:
            if 'musicPlaylistShelfRenderer' in s:
                shelf_contents = s['musicPlaylistShelfRenderer'].get('contents', [])
                break
    elif 'tabs' in sec:
        tabs = sec.get('tabs', [])
        if tabs:
            content = tabs[0].get('tabRenderer', {}).get('content', {})
            shelves = content.get('sectionListRenderer', {}).get('contents', [])
            for s in shelves:
                if 'musicPlaylistShelfRenderer' in s:
                    shelf_contents = s['musicPlaylistShelfRenderer'].get('contents', [])
                    break

    for item in shelf_contents:
        renderer = item.get('musicResponsiveListItemRenderer')
        if not renderer:
            continue

        flex_cols = renderer.get('flexColumns', [])
        track_title = "".join(r.get('text', '') for r in flex_cols[0].get('musicResponsiveListItemFlexColumnRenderer', {}).get('text', {}).get('runs', [])) if flex_cols else 'Unknown Track'
        artist_sub = "".join(r.get('text', '') for r in flex_cols[1].get('musicResponsiveListItemFlexColumnRenderer', {}).get('text', {}).get('runs', [])) if len(flex_cols) > 1 else ''

        nav = renderer.get('overlay', {}).get('musicItemThumbnailOverlayRenderer', {})\
            .get('content', {}).get('musicPlayButtonRenderer', {})\
            .get('playNavigationEndpoint', {}).get('watchEndpoint', {})
        vid = nav.get('videoId')
        if not vid and flex_cols:
            runs = flex_cols[0].get('musicResponsiveListItemFlexColumnRenderer', {}).get('text', {}).get('runs', [])
            if runs and 'navigationEndpoint' in runs[0]:
                vid = runs[0]['navigationEndpoint'].get('watchEndpoint', {}).get('videoId')

        if not vid:
            continue

        item_thumbs = renderer.get('thumbnail', {}).get('musicThumbnailRenderer', {}).get('thumbnail', {}).get('thumbnails', [])
        thumb = item_thumbs[-1]['url'] if item_thumbs else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

        parsed_tracks.append({
            "id": vid,
            "title": track_title,
            "artist_display": artist_sub,
            "artists": [artist_sub.split('•')[0].strip()] if artist_sub else ["YouTube Music"],
            "duration_str": "3:30",
            "audio_url": "",
            "ytm_url": f"https://music.youtube.com/watch?v={vid}",
            "cover_image": thumb,
            "cover_image_large": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg"
        })

    return {
        "id": playlist_id,
        "type": "playlist",
        "title": title,
        "description": desc or subtitle or "Extracted from https://music.youtube.com/",
        "owner": "YouTube Music",
        "track_count": len(parsed_tracks),
        "cover_images": {
            "large": cover_large,
            "medium": cover_large,
            "thumbnail": cover_large
        },
        "cover_image_large": cover_large,
        "tracks": parsed_tracks,
        "ytm_url": f"https://music.youtube.com/playlist?list={playlist_id}"
    }

def scrape_any_ytm(url_or_input: str) -> Dict[str, Any]:
    """
    Universal entrypoint for scraping YouTube Music links or search queries.
    """
    parsed = parse_ytm_url(url_or_input)
    if parsed["type"] == "track":
        return scrape_track(parsed["id"])
    elif parsed["type"] == "playlist":
        return scrape_playlist(parsed["id"])
    else:
        try:
            return scrape_track(parsed["id"])
        except Exception:
            return scrape_playlist(parsed["id"])

if __name__ == "__main__":
    print("Testing YouTube Music Track scraping...")
    t = scrape_track("JGwWNGJdvx8", resolve_stream=False)
    print("Scraped Track:", t["title"], "by", t["artist_display"])
    print("Large Image:", t["cover_image_large"])
    print("Has lyrics:", t["lyrics"]["has_lyrics"])
