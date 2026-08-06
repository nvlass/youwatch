from dataclasses import dataclass
from urllib.parse import urlparse

import yt_dlp


@dataclass
class VideoResult:
    id: str
    title: str
    uploader: str
    duration: int | None
    thumbnail_url: str | None
    webpage_url: str


def _entry_to_result(entry: dict) -> VideoResult:
    video_id = entry.get("id", "")
    webpage_url = entry.get("webpage_url") or entry.get("url") or ""
    if webpage_url and not webpage_url.startswith("http"):
        webpage_url = f"https://www.youtube.com/watch?v={video_id}"
    thumbnail_url = entry.get("thumbnail")
    if not thumbnail_url:
        thumbnails = entry.get("thumbnails") or []
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
    return VideoResult(
        id=video_id,
        title=entry.get("title") or "(untitled)",
        uploader=entry.get("uploader") or entry.get("channel") or "",
        duration=entry.get("duration"),
        thumbnail_url=thumbnail_url,
        webpage_url=webpage_url,
    )


def _extract(target: str, limit: int) -> list[VideoResult]:
    opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "playlistend": limit,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(target, download=False)
    entries = info.get("entries") if info else None
    if entries is None:
        entries = [info] if info else []
    return [_entry_to_result(e) for e in entries if e]


def search(query: str, limit: int = 20) -> list[VideoResult]:
    return _extract(f"ytsearch{limit}:{query}", limit)


def is_youtube_url(text: str) -> bool:
    parsed = urlparse(text.strip())
    if parsed.scheme not in ("http", "https"):
        return False
    return "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc


def list_channel(url: str, limit: int = 50) -> list[VideoResult]:
    return _extract(url, limit)
