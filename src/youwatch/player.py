import shutil
import subprocess
import sys
from pathlib import Path

from youwatch.progress import WATCH_LATER_DIR

_VENV_YT_DLP = Path(sys.executable).parent / "yt-dlp"


def _ytdl_path() -> str:
    if _VENV_YT_DLP.exists():
        return str(_VENV_YT_DLP)
    found = shutil.which("yt-dlp")
    if found:
        return found
    raise RuntimeError("yt-dlp not found; install it into the project venv")


def play(webpage_url: str, start_seconds: float | None = None) -> subprocess.Popen:
    mpv = shutil.which("mpv")
    if not mpv:
        raise RuntimeError("mpv not found on PATH; install it with `brew install mpv`")
    args = [
        mpv,
        webpage_url,
        f"--script-opts=ytdl_hook-ytdl_path={_ytdl_path()}",
        "--save-position-on-quit",
        f"--watch-later-directory={WATCH_LATER_DIR}",
    ]
    if start_seconds is not None:
        args.append(f"--start={start_seconds}")
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
