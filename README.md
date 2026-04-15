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

```text
MyTeamOfAgents/
├── agents/                          # Per-agent source-of-truth files
│   ├── olivia/
│   │   ├── AGENTS.md
│   │   ├── IDENTITY.md
│   │   ├── ROLE.md
│   │   ├── HANDOFFS.md
│   │   ├── FEEDBACK.md
│   │   └── MEMORY-SUMMARY.md
│   ├── scout/
│   │   ├── AGENTS.md
│   │   ├── IDENTITY.md
│   │   ├── ROLE.md
│   │   ├── TOOLS.md
│   │   ├── SOURCES.md
│   │   ├── FEEDBACK.md
│   │   └── MEMORY-SUMMARY.md
│   ├── atlas/
│   │   ├── AGENTS.md
│   │   ├── IDENTITY.md
│   │   ├── ROLE.md
│   │   ├── ANALYSIS-RULES.md
│   │   ├── FEEDBACK.md
│   │   └── MEMORY-SUMMARY.md
│   ├── forge/
│   │   ├── AGENTS.md
│   │   ├── IDENTITY.md
│   │   ├── ROLE.md
│   │   ├── BUILD-RULES.md
│   │   ├── FEEDBACK.md
│   │   └── MEMORY-SUMMARY.md
│   ├── sentinel/
│   │   ├── AGENTS.md
│   │   ├── IDENTITY.md
│   │   ├── ROLE.md
│   │   ├── CHECKS.md
│   │   ├── FEEDBACK.md
│   │   └── MEMORY-SUMMARY.md
│   └── ranger/
│       ├── AGENTS.md
│       ├── IDENTITY.md
│       ├── ROLE.md
│       ├── PI-CONTROL.md
│       ├── FEEDBACK.md
│       └── MEMORY-SUMMARY.md
├── brain/                           # Durable shared intelligence
│   ├── SOUL.md
│   ├── constitution/
│   │   ├── principles.md
│   │   ├── delegation-rules.md
│   │   └── safety-rules.md
│   ├── memory/
│   │   ├── preferences/
│   │   ├── patterns/
│   │   ├── reflections/
│   │   ├── project-lessons/
│   │   └── promoted-rules/
│   └── surprise/
│       ├── proactive-ideas.md
│       └── delight-rules.md
├── workspace/                       # Files meant to sync into the live OpenClaw workspace
│   ├── AGENTS.md
│   ├── IDENTITY.md
│   ├── TOOLS.md
│   ├── USER.md
│   ├── ROUTING.md
│   └── MEMORY.md
├── plugins/                         # Structured tool wrappers and adapters
│   ├── README.md
│   ├── search/
│   │   ├── searxng/
│   │   ├── brave/
│   │   └── fallback/
│   ├── media/
│   │   ├── youtube_latest_videos/
│   │   ├── rss_fetch/
│   │   └── transcript_fetch/
│   ├── web/
│   │   ├── web_scrape/
│   │   ├── article_extract/
│   │   └── browser_fetch/
│   └── social/
│       └── x_recent_posts/
├── skills/                          # Agent-callable skills, prompts, and shell helpers
│   ├── scout_media/
│   ├── scout_search/
│   ├── atlas_research/
│   ├── forge_code/
│   ├── forge_ops/
│   ├── sentinel_watch/
│   └── ranger_pi/
├── research/                        # Atlas outputs and decision memos
│   ├── briefs/
│   ├── comparisons/
│   ├── hardware/
│   └── ai-engineering/
├── docs/
│   ├── architecture/
│   ├── setup-guides/
│   ├── runbooks/
│   └── decisions/
├── infra/                           # Optional infrastructure
│   ├── docker/
│   ├── db/
│   ├── systemd/
│   ├── scripts/
│   └── env/
├── sync/                            # Safe sync layer between repo and live Pi workspace
│   ├── export-to-openclaw.sh
│   ├── import-from-openclaw.sh
│   ├── validate-sync.sh
│   ├── manifest.txt
│   └── denylist.txt
├── data/                            # Local generated data, usually gitignored except samples
│   ├── samples/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── README.md
├── setup-repo.sh
└── OPENCLAW_DESIGN.md
```

## Notes for Olivia

- `agents/` is the authoring layer for agent personality, role, feedback, and memory summaries.
- `workspace/` is the deployment layer that maps into the live OpenClaw workspace.
- `brain/` holds shared intelligence, promoted memory, and proactive behavior rules.
- `plugins/` contains structured adapters for search, media, web, and social sources.
- `skills/` contains agent-callable skills and helper logic.
- `sync/` is the safe bridge between the Git repo and the live Pi workspace.
- `infra/` is optional and should not block the Pi-native setup.

