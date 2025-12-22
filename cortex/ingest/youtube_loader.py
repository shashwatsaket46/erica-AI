import re
from youtube_transcript_api import YouTubeTranscriptApi


# ==========================================
# YOUTUBE LOADER
# This module provides functions to extract video IDs from YouTube URLs
# and to load transcripts from YouTube videos.
# ==========================================
def extract_video_id(url: str):
    match = re.search(r"(v=|youtu.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(2) if match else None

# ==========================================
# LOAD YOUTUBE TRANSCRIPT
# This function fetches the transcript of a YouTube video given its URL.
# ==========================================
def load_youtube(url: str) -> str:
    vid = extract_video_id(url)
    if not vid:
        print(f"[ERROR] Invalid YouTube URL: {url}")
        return ""

    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid)
    except Exception as e:
        print(f"[ERROR] Transcript unavailable for {url}: {e}")
        return ""

    lines = [f"[{seg['start']:.2f}] {seg['text']}" for seg in transcript]
    return "\n".join(lines)
