# MyTeamOfAgents

Bootstrap repository for a multi-agent OpenClaw setup.

## Structure

- `agents/`: per-agent source-of-truth docs.
- `brain/`: shared rules, memory, and proactive behavior docs.
- `workspace/`: repo-managed copies of files meant to deploy into `~/.openclaw/workspace`.
- `plugins/`, `skills/`, `research/`, `docs/`, `infra/`: organized extension areas.
- `sync/`: safe import/export scripts plus manifest and denylist.

## Usage

```bash
./setup-repo.sh
./sync/import-from-openclaw.sh
./sync/validate-sync.sh
# optional
./sync/export-to-openclaw.sh
```

## Sync assumptions

- Import/export uses `sync/manifest.txt` for canonical workspace file mappings.
- `import-from-openclaw.sh` also copies additional markdown files from `~/.openclaw/workspace` into `workspace/extra-md/` unless blocked by `sync/denylist.txt`.
- This repo does not move or delete anything in the live OpenClaw workspace.
- Agent authoring files under `agents/` are scaffolded, but left intentionally blank for later curation.
