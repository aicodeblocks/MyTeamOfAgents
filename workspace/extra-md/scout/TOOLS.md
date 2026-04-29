# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Scout tool usage policy

### Search priority

Use OpenClaw-configured search tools first for external discovery and current information.

- Search (SearXNG / Brave) for latest news, current events, comparisons, and discovering sources.
- RSS/feed parsing for media briefings, daily updates, and blog/feed summaries.
- `yt-dlp` first for YouTube/media metadata and subtitle availability checks.
- HTTP extraction before browser automation for normal webpages.
- Playwright only when simpler extraction is insufficient.

### Tool behavior rules

- For current events, always use search or RSS before answering.
- For YouTube tasks, use `yt-dlp` first before any other method.
- For webpages, try HTTP extraction before using Playwright.
- Use Playwright only when normal extraction is insufficient.
- If a tool fails, clearly report the failure and fallback if appropriate.
- When a real tool path exists, do not substitute model-only answering for collection.
- In Scout replies, explicitly identify the tool calls used and what information each fetched when practical.

### Media briefing script note

The script `/home/node/.openclaw/media-briefing.sh` is optional fallback, not primary.

Use it only if:
- explicitly requested
- all other tool paths are unavailable or failed

### Status wording for Scout outputs

When reporting status in briefings, MOMs, or blocker summaries:
- do not label Scout as blocked if tool-backed collection is currently working
- describe the legacy script as optional fallback only
- call out the real live issue precisely, such as delivery failure, tracked-source discovery gap, no new items in the last 24 hours, or thin evidence quality
- use plain user-facing wording instead of internal phrasing like recovered handoff or metadata-level only
- for metadata-only video judgments, say plainly that the judgment is based on title/description/metadata and not full transcript or content review

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
