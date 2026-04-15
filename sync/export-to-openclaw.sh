#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_ROOT="${OPENCLAW_HOME:-$HOME/.openclaw}"
TARGET_WORKSPACE="${OPENCLAW_WORKSPACE:-$TARGET_ROOT/workspace}"
MANIFEST="$SCRIPT_DIR/manifest.txt"

mkdir -p "$TARGET_WORKSPACE"

while IFS='|' read -r source_rel dest_rel; do
  [[ -z "$source_rel" || "$source_rel" =~ ^# ]] && continue
  src="$REPO_ROOT/$dest_rel"
  dst="$TARGET_WORKSPACE/$source_rel"
  if [[ ! -f "$src" ]]; then
    echo "skip missing: $src"
    continue
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  echo "exported: $dest_rel -> $source_rel"
done < "$MANIFEST"

echo "Export complete."
