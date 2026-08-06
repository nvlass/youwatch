import shutil
import subprocess
import sys
from pathlib import Path

_VENV_YT_DLP = Path(sys.executable).parent / "yt-dlp"


def _ytdl_path() -> str:
    if _VENV_YT_DLP.exists():
        return str(_VENV_YT_DLP)
    found = shutil.which("yt-dlp")
    if found:
        return found
    raise RuntimeError("yt-dlp not found; install it into the project venv")


def play(webpage_url: str) -> subprocess.Popen:
    mpv = shutil.which("mpv")
    if not mpv:
        raise RuntimeError("mpv not found on PATH; install it with `brew install mpv`")
    return subprocess.Popen(
        [
            mpv,
            webpage_url,
            f"--script-opts=ytdl_hook-ytdl_path={_ytdl_path()}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
