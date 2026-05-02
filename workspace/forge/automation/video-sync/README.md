# Home video sync for YoutubeDL-Material

- Source scan root: `/home/mahmed`
- Target library: `/portainer/Files/AppData/Youtube/Video`
- YoutubeDL-Material DB: `/portainer/Files/AppData/Config/YTDLM/local_db.json`
- Schedule: `*/10 * * * *`

## What it does

- Finds local `.mp4` files under `/home/mahmed`, excluding cache/trash/workspace paths and Chromium extension payloads
- Also remuxes `.mov` and `.m4v` to `.mp4`
- Copies sidecar thumbnails and `.info.json` metadata when present
- If a source filename ends with ` [digits]` before the extension, imports it under the clean base name instead
- Generates fallback `.info.json` metadata when absent
- Tracks the last successful source `mtime` watermark in `state/state.json` and only reconsiders files newer than that watermark
- Holds the watermark behind files touched in the last 2 minutes, so partially copied files are deferred until they have been stable long enough
- Registers new files in YoutubeDL-Material's local DB
- Restarts the `youtubedl-material` container only when DB records changed
- Never moves or deletes source files

## State file

`state/state.json` now keeps:

- `files`: per-source sync metadata
- `last_successful_scan_mtime`: the newest source `mtime` fully covered by a successful run
- `stable_age_seconds`: the minimum age before a source file is eligible for import

The watermark only advances after an error-free run. If a run fails, the next run will retry the same eligible window instead of skipping past it.

## Installed files

- `sync_home_videos.py`
- `install-cron.sh`
- `state/state.json`
- `logs/cron.log`
