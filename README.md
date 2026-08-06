# youwatch

A small desktop app for searching YouTube and streaming results — old theatre
recordings, audiobooks, whatever a channel's back catalog has — without ads
and without downloading anything to disk.

## How it works

- Search or channel/playlist listing is done via `yt-dlp` (as a Python
  library, `extract_flat=True`) — fast, metadata-only.
- Playback is handed off to `mpv`, which has a built-in `yt-dlp` hook that
  resolves a YouTube URL straight to its underlying media stream. This
  bypasses YouTube's ad-injecting web player entirely, so no ads ever load,
  and mpv only streams/buffers — nothing is saved to disk.
- mpv opens in its own native window (not embedded in the app), so you get
  its normal seek/pause/fullscreen/volume controls for free.

## Requirements

- Python 3.11 (pinned via `.tool-versions`, managed with `asdf`)
- [`mpv`](https://mpv.io) and [`deno`](https://deno.com) on `PATH`
  (`brew install mpv deno`) — `deno` is required by recent `yt-dlp` to solve
  YouTube's JS challenge (SABR) during stream resolution.

## Setup

```sh
asdf install                 # picks up python 3.11.14 from .tool-versions
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Running

```sh
.venv/bin/python -m youwatch.main
```

or, after activating the venv (`source .venv/bin/activate`), just `youwatch`.

## Usage

Type a search query, or paste a channel/playlist URL, and press Enter.
Double-click a result to play it — mpv opens in a separate window and starts
streaming.

## Maintenance

- `yt-dlp` needs frequent updates to keep working against YouTube's changes:
  `.venv/bin/pip install -U yt-dlp`.
- If a video fails to resolve (age-restricted / region-locked), the fallback
  is passing `--cookies-from-browser safari` to mpv in `player.py` — not
  wired up by default.
