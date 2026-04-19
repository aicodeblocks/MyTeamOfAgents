# Delegation fix, 2026-04-14

This note captures the delegation issue Olivia hit, what fixed it, and what must remain true so the setup keeps working.

## Summary

Delegation was initially failing because OpenClaw's runtime policy blocks worker-agent delegation by default unless those agents are explicitly allowlisted in the live config. Olivia's routing instructions were correct, but the runtime still refused the handoff.

The fix was to:

1. add the worker-agent allowlist in the live OpenClaw config
2. restart the gateway so the runtime picked up the change
3. run a live delegation test and confirm the delegated task completed end to end

After that, Olivia could remain coordinator-only while Scout and Atlas handled the specialist work.

## What the blocker was

The blocker was not Olivia's prompt logic. The blocker was the default runtime delegation policy.

Until the live config explicitly allowed worker agents, Olivia could not actually hand work to them even when her routing docs said she should. In practice, delegation was blocked by policy until these workers were allowlisted:

- scout
- atlas
- forge
- sentinel
- ranger

## What changed

The live OpenClaw config was updated so Olivia could delegate to the approved worker agents above.

That config change only became active after restarting the gateway:

```bash
openclaw gateway restart
openclaw gateway status
```

## Why media and news delegation worked after the fix

Media/news requests started working because the runtime could finally execute the routing design that was already intended:

- Olivia stays in coordinator mode
- Scout does collection work like YouTube, RSS, and web fetches
- Atlas does analysis, ranking, and synthesis on what Scout collected

So once the allowlist was enabled and the gateway restarted, a request like "get me the news" or "get me the latest AI videos" could flow correctly:

1. Olivia interprets the request and routes it automatically
2. Scout collects the raw items
3. Atlas analyzes what is worth surfacing
4. Olivia returns the coordinated result

## What must stay in place

These are the non-negotiables for keeping delegation healthy.

### 1) Worker allowlist must remain enabled

Olivia needs runtime permission to delegate to the workers she is supposed to use:

- scout
- atlas
- forge
- sentinel
- ranger

If that allowlist is removed or narrowed incorrectly, delegation will fail again.

### 2) Restart after config changes

Routing or delegation config changes are not safely assumed to be live until the gateway is restarted and checked.

Use:

```bash
openclaw gateway restart
openclaw gateway status
```

Then run a real delegation test.

### 3) Olivia must remain coordinator-only

Olivia should triage, route, and coordinate. She should not do Scout or Atlas work herself.

Current routing policy:

- collection/fetching -> Scout
- analysis/ranking -> Atlas
- final coordination/response -> Olivia

### 4) Scout remains the collection layer

Scout should keep handling raw collection steps such as:

- YouTube fetches
- RSS pulls
- web scraping / source gathering
- media briefing collection

### 5) Atlas remains the analysis layer

Atlas should keep handling:

- deep research
- synthesis
- ranking
- recommendations
- worth-watching / what-matters analysis

### 6) Auto-route on "get me ..."

Olivia should continue auto-routing requests phrased like "get me ..." instead of waiting for the user to explicitly name a worker.

That behavior matters especially for daily media/news briefings, where the intended path is:

- Olivia decides the route
- Scout collects
- Atlas analyzes
- Olivia delivers

## Verification checklist

Use this after any future routing/delegation change:

1. confirm the worker allowlist is present in live config
2. restart the gateway
3. verify gateway health
4. run one real delegation test
5. confirm the subtask starts cleanly and returns normally

## Related repo files

- `workspace/TOOLS.md`
- `workspace/ROUTING.md`
- `workspace/extra-md/olivia-routing.md`
- `workspace/extra-md/forge/SETUP-2026-04-14.md`
- `workspace/extra-md/memory/2026-04-14.md`
