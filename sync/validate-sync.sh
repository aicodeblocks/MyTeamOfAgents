#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_ROOT="${OPENCLAW_HOME:-$HOME/.openclaw}"
SOURCE_WORKSPACE="${OPENCLAW_WORKSPACE:-$SOURCE_ROOT/workspace}"
MANIFEST="$SCRIPT_DIR/manifest.txt"
status=0

while IFS='|' read -r source_rel dest_rel; do
  [[ -z "$source_rel" || "$source_rel" =~ ^# ]] && continue
  src="$SOURCE_WORKSPACE/$source_rel"
  dst="$REPO_ROOT/$dest_rel"
  if [[ ! -f "$src" ]]; then
    echo "warning: missing source: $src"
    continue
  fi
  if [[ ! -f "$dst" ]]; then
    echo "missing repo file: $dst"
    status=1
    continue
  fi
  if ! cmp -s "$src" "$dst"; then
    echo "differs: $source_rel <-> $dest_rel"
    status=1
  fi
done < "$MANIFEST"

exit "$status"
