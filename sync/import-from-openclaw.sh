#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_ROOT="${OPENCLAW_HOME:-$HOME/.openclaw}"
SOURCE_WORKSPACE="${OPENCLAW_WORKSPACE:-$SOURCE_ROOT/workspace}"
MANIFEST="$SCRIPT_DIR/manifest.txt"

if [[ ! -d "$SOURCE_WORKSPACE" ]]; then
  echo "OpenClaw workspace not found: $SOURCE_WORKSPACE" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/workspace"

is_denied() {
  local path="$1"
  case "$path" in
    .git/*|.openclaw/*|state/*|MyTeamOfAgents/*|atlas/.git/*|atlas/.openclaw/*|forge/.git/*|forge/.openclaw/*|scout/.git/*|scout/.openclaw/*|memory/.dreams/*) return 0 ;;
    *) return 1 ;;
  esac
}

while IFS='|' read -r source_rel dest_rel; do
  [[ -z "$source_rel" || "$source_rel" =~ ^# ]] && continue
  src="$SOURCE_WORKSPACE/$source_rel"
  dst="$REPO_ROOT/$dest_rel"
  if [[ ! -f "$src" ]]; then
    echo "skip missing: $src"
    continue
  fi
  if is_denied "$source_rel"; then
    echo "denylisted: $source_rel"
    continue
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  echo "imported: $source_rel -> $dest_rel"
done < "$MANIFEST"

rm -rf "$REPO_ROOT/workspace/extra-md"
mkdir -p "$REPO_ROOT/workspace/extra-md"

while IFS= read -r -d '' file; do
  rel="${file#"$SOURCE_WORKSPACE/"}"
  is_denied "$rel" && continue
  target="$REPO_ROOT/workspace/extra-md/$rel"
  mkdir -p "$(dirname "$target")"
  cp "$file" "$target"
done < <(find "$SOURCE_WORKSPACE" -type f -name '*.md' -print0)

echo "Import complete."
