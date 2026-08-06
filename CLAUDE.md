# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
# setup (python pinned to 3.11.14 via asdf/.tool-versions)
python3 -m venv .venv
.venv/bin/pip install -e .

# run
.venv/bin/python -m youwatch.main        # or `youwatch` once venv is activated

# keep yt-dlp current — needs frequent updates to keep working against YouTube's changes
.venv/bin/pip install -U yt-dlp
```

No test suite, linter, or build step exists yet.

System dependencies (not pip-installable): `mpv` and `deno`, both via
`brew install mpv deno`. `deno` is required by `yt-dlp` to solve YouTube's
JS challenge (SABR) during stream resolution — without it, resolution
fails with 403s.

## Architecture

The core design idea: **mpv does the ad-bypassing, not this app's code.**
`player.py`'s `play()` spawns `mpv <youtube-url>` as a subprocess. mpv has a
built-in `ytdl_hook.lua` that shells out to `yt-dlp` to resolve the URL
directly to the underlying CDN media stream, which bypasses YouTube's
ad-injecting JS web player entirely — ads never load, and mpv only
streams/buffers, nothing is written to disk. mpv opens in its own native
window rather than being embedded in the app (libmpv embedding on macOS is
unreliable — dylib packaging issues, black-video failures); this trades a
second window for a large reduction in complexity/fragility.

`player.py` pins mpv's `ytdl_hook-ytdl_path` script-opt to the venv's own
`yt-dlp` binary (`Path(sys.executable).parent / "yt-dlp"`), so there is
exactly one yt-dlp install/version in play rather than mpv silently using a
different system-wide copy.

Data flow:
- `search.py` wraps `yt_dlp.YoutubeDL(extract_flat=True)` for two cases:
  `search()` (via the `ytsearchN:<query>` pseudo-URL) and `list_channel()`
  (any channel/playlist URL) — both fast, metadata-only, no format
  resolution. `is_youtube_url()` decides which path the GUI takes for a
  given input string. Both return `VideoResult` dataclasses.
- `ui/main_window.py`'s `SearchThread` (a `QThread`) runs the blocking
  `search.py` calls off the UI thread and emits `succeeded`/`failed`
  signals back to `MainWindow`.
- `ui/results_model.py`'s `ResultsModel` (`QAbstractListModel`) holds the
  `VideoResult` list and lazily fetches thumbnails asynchronously via
  `QNetworkAccessManager`, emitting `dataChanged` per row as each thumbnail
  arrives. The video's playable URL is exposed to the view via a custom
  `WEBPAGE_URL_ROLE`.
- Double-clicking a result in `MainWindow` reads `WEBPAGE_URL_ROLE` off the
  model and calls `player.play()`.

Known caveat baked into `search.py`: `extract_flat` channel listings can
return `duration: None` for some entries (shown as "—" in the UI) — this is
a yt-dlp limitation, not a bug to fix here.

If videos fail to resolve (age-restricted/region-locked), the documented
fallback is adding `--cookies-from-browser safari` to the mpv invocation in
`player.py` — not wired up by default.
