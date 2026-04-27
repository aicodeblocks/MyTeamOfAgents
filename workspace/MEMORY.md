# MEMORY.md

## Standing preferences

- Mansoor wants future projects handled with a standard planning workflow by default: Mansoor gives the project idea, Olivia creates a project code, Olivia plus Atlas break it into epics/stories, Olivia tracks blockers and decisions, Forge executes only story-sized approved work, Daily MOM reports status, and twice-weekly scrum refines the backlog.
- Mansoor does not want repo/code work to begin on a project until he is happy with the whole-project story breakdown.
- Before updating MEMORY.md, Olivia should ask Mansoor first and take a backup of the current MEMORY.md file.
- In this environment, Olivia should use explicit agent IDs for delegation when spawning specialist work. Known local agent IDs are `main`, `scout`, `atlas`, `forge`, `ranger`, and `sentinel`.
- Mansoor likes the latest-news briefing format now in use. For daily briefings, Atlas should add `worth to watch` for videos and `worth to read` for news. Video sources should include `@thedeshbhakt`, `@ravishkumar.official`, and latest videos on AI, AI code, and top AI technology trends. Only include items from the last 24 hours, avoid repetition the next day, and if no new videos are found say `no video`.
- Mansoor does not want stale blocker language in MOM or briefing outputs. Scout is no longer to be described as simply blocked by the missing legacy script. Current truthful state: fallback tool-based media/news collection works, the legacy script is optional fallback only, and remaining issues should be described specifically, such as delivery reliability, tracked-source discovery gaps, non-repetition tracking, or thin evidence on some items.
- In briefings, `worth to read` items should include the article/news URL. If video judgments are based only on metadata rather than full transcript/subtitle/content review, say that in plain language. If no fresh qualifying item is found from a tracked channel in the last 24 hours, say that plainly instead of using internal wording.
- Going forward, when durable markdown files are updated, Olivia should route a sync audit/update to Forge so Forge can decide whether to push to an existing PR or open a new one. Daily MOM should include a `PR approvals pending` section with relevant PR URLs when applicable.
