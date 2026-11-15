"""
YouTube Music Search Module (https://music.youtube.com/)
Performs real-time music searches against YouTube Music's InnerTube API.
"""
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

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

_SEARCH_CACHE: Dict[str, List[Dict[str, Any]]] = {}

def search_ytm(query: str, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Searches YouTube Music for songs matching query.
    Returns list of song objects with:
    id, title, artists, artist_display, album, duration_str,
    cover_image, cover_image_large, audio_url, ytm_url, source
    """
    if not query or not query.strip():
        return []

    q_key = query.strip().lower()
    if q_key in _SEARCH_CACHE:
        return _SEARCH_CACHE[q_key][:limit]

    url = 'https://music.youtube.com/youtubei/v1/search'
    body = {
        'context': {'client': YTM_CLIENT},
        'query': query.strip()
    }

    results = []

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode('utf-8'),
            headers=HEADERS
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        tabs = data.get('contents', {}).get('tabbedSearchResultsRenderer', {}).get('tabs', [])
        if not tabs:
            return []

        contents = tabs[0].get('tabRenderer', {}).get('content', {})\
            .get('sectionListRenderer', {}).get('contents', [])

        # 1. Check Top result card if present
        if contents:
            card = contents[0].get('musicCardShelfRenderer')
            if card:
                title = "".join(r.get('text', '') for r in card.get('title', {}).get('runs', []))
                sub = "".join(r.get('text', '') for r in card.get('subtitle', {}).get('runs', []))
                nav = card.get('onTap', {}).get('watchEndpoint', {}) or \
                      card.get('title', {}).get('runs', [{}])[0].get('navigationEndpoint', {}).get('watchEndpoint', {})
                vid = nav.get('videoId')
                if vid:
                    results.append({
                        "id": vid,
                        "title": title,
                        "artist_display": sub,
                        "artists": [sub.split('•')[0].strip()] if sub else ["YouTube Music"],
                        "album": "YouTube Music Top Match",
                        "duration_str": "3:30",
                        "audio_url": "",  # Resolved lazily on playback
                        "cover_image": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                        "cover_image_large": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
                        "ytm_url": f"https://music.youtube.com/watch?v={vid}",
                        "source": "YouTube Music"
                    })

        # 2. Extract itemSectionRenderer songs
        for sec in contents[1:]:
            items = sec.get('itemSectionRenderer', {}).get('contents', [])
            for item in items:
                renderer = item.get('musicResponsiveListItemRenderer')
                if not renderer:
                    continue

                flex_cols = renderer.get('flexColumns', [])
                if not flex_cols:
                    continue

                track_title = "".join(r.get('text', '') for r in flex_cols[0].get('musicResponsiveListItemFlexColumnRenderer', {}).get('text', {}).get('runs', []))
                artist_sub = "".join(r.get('text', '') for r in flex_cols[1].get('musicResponsiveListItemFlexColumnRenderer', {}).get('text', {}).get('runs', [])) if len(flex_cols) > 1 else ''

                # Filter out pure channel or artist pages without videoId
                nav = renderer.get('overlay', {}).get('musicItemThumbnailOverlayRenderer', {})\
                    .get('content', {}).get('musicPlayButtonRenderer', {})\
                    .get('playNavigationEndpoint', {}).get('watchEndpoint', {})
                vid = nav.get('videoId')
                if not vid:
                    runs = flex_cols[0].get('musicResponsiveListItemFlexColumnRenderer', {}).get('text', {}).get('runs', [])
                    if runs and 'navigationEndpoint' in runs[0]:
                        vid = runs[0]['navigationEndpoint'].get('watchEndpoint', {}).get('videoId')

                if not vid:
                    continue

                thumbs = renderer.get('thumbnail', {}).get('musicThumbnailRenderer', {}).get('thumbnail', {}).get('thumbnails', [])
                thumb = thumbs[-1]['url'] if thumbs else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

                results.append({
                    "id": vid,
                    "title": track_title,
                    "artist_display": artist_sub,
                    "artists": [artist_sub.split('•')[0].strip()] if artist_sub else ["YouTube Music"],
                    "album": "YouTube Music",
                    "duration_str": "3:30",
                    "audio_url": "",
                    "cover_image": thumb,
                    "cover_image_large": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
                    "ytm_url": f"https://music.youtube.com/watch?v={vid}",
                    "source": "YouTube Music"
                })

                if len(results) >= limit:
                    break

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"Error searching YouTube Music: {e}")

    if results:
        _SEARCH_CACHE[q_key] = results

    return results

if __name__ == "__main__":
    test_res = search_ytm("The Weeknd Blinding Lights", limit=5)
    print(f"YouTube Music search returned {len(test_res)} items:")
    for r in test_res:
        print(f" - {r['title']} | {r['artist_display']} | id: {r['id']}")
