#!/usr/bin/env bash
set -euo pipefail
SCRIPT="/home/mahmed/.openclaw/workspace/forge/automation/video-sync/sync_home_videos.py"
LOG="/home/mahmed/.openclaw/workspace/forge/automation/video-sync/logs/cron.log"
mkdir -p "$(dirname "$LOG")"
chmod +x "$SCRIPT"
line="*/10 * * * * $SCRIPT >> $LOG 2>&1"
current="$(crontab -l 2>/dev/null || true)"
filtered="$(printf '%s
' "$current" | grep -Fv "$SCRIPT" || true)"
printf '%s
%s
' "$filtered" "$line" | sed '/^$/N;/^\n$/D' | crontab -
echo "Installed cron: $line"
