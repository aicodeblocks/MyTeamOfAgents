# Durable briefing storage

Store any generated briefing twice so a missed delivery can be recovered without redoing collection work.

## Layout

- `raw/YYYY/YYYY-MM-DD.md` stores the source-rich working draft or assembled notes.
- `formatted/YYYY/YYYY-MM-DD.md` stores the final user-facing briefing text.

## Usage

1. When a briefing is assembled, save the raw draft first.
2. Save the final formatted delivery separately, even if it is very similar.
3. If delivery fails, resend from `formatted/...` and only revisit `raw/...` if edits are needed.
4. Keep filenames date-based unless a second delivery is needed that day, then append `-v2`, `-v3`, etc.

## Live daily briefing path

The active 10:00 AM America/New_York OpenClaw cron job now instructs the daily briefing run to save both artifacts before any Telegram delivery attempt. The cron config lives at:

- `~/.openclaw/cron/jobs.json`

The live job payload is the runtime enforcement point for save-before-deliver behavior.
