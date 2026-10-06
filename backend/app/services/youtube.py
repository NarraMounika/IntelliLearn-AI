import os, re, requests
from youtube_transcript_api import YouTubeTranscriptApi

def video_id(url):
    for pattern in [r"(?:v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})"]:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def transcript(url):
    vid = video_id(url)
    if not vid:
        raise ValueError("Invalid YouTube URL")
    fetched = YouTubeTranscriptApi().fetch(vid, languages=["en", "en-US", "en-GB"])
    parts = [getattr(item, "text", "") or (item.get("text", "") if isinstance(item, dict) else "") for item in fetched]
    text = " ".join(parts).strip()
    if not text:
        raise RuntimeError("No accessible transcript was found for this video.")
    return vid, text

def search(query):
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        return []
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={"part":"snippet", "q":query, "type":"video", "maxResults":8, "key":key},
        timeout=15,
    )
    response.raise_for_status()
    output = []
    for item in response.json().get("items", []):
        snippet = item["snippet"]
        vid = item["id"]["videoId"]
        output.append({
            "videoId": vid,
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "description": snippet.get("description", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })
    return output
