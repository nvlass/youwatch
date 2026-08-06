import hashlib
from pathlib import Path

WATCH_LATER_DIR = Path.home() / ".local" / "share" / "youwatch" / "watch_later"


def resume_position(webpage_url: str) -> float | None:
    digest = hashlib.md5(webpage_url.encode("utf-8")).hexdigest()
    entry = None
    for candidate in (WATCH_LATER_DIR / digest, WATCH_LATER_DIR / digest.upper()):
        if candidate.exists():
            entry = candidate
            break
    if entry is None:
        return None
    try:
        for line in entry.read_text().splitlines():
            if line.startswith("start="):
                return float(line.removeprefix("start="))
    except (OSError, ValueError):
        return None
    return None
