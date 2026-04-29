# OpenClaw Dashboard Phase-wise Plan Analysis

Purpose: capture a reusable planning analysis of Mansoor's dashboard implementation guide so the work can be referenced later without spending extra live tokens to reconstruct the same conclusions.

## Source summary

Mansoor provided a phase-wise implementation plan for an OpenClaw command center/dashboard.

Artifacts received:
- PDF version
- Markdown version

The markdown version is the better working source because it is already structured and editable.

## What the plan is trying to achieve

This is a command center, not just a task board.

Core ideas:
- Olivia owns approvals and high-level control
- work moves through Scout -> Atlas -> Forge -> Sentinel -> Olivia
- the UI combines workflow state with operational visibility
- approvals, logs, failures, retries, and agent status live in one place

This aligns strongly with the multi-agent operating model already being established.

## Strong points of the plan

### 1. Clear operating model
The document maps the team into a visible workflow:
- Scout collects
- Atlas analyzes
- Forge executes
- Sentinel validates/monitors
- Olivia approves/reroutes

That is a strong fit for the current role definitions.

### 2. Good phased delivery structure
The phases are practical and progressive:
- foundation and static board
- stage transitions
- Olivia approval layer
- Sentinel observability layer
- agent integration contracts
- realtime UX
- security/governance hardening

This is better than trying to build everything at once.

### 3. Useful schema-first thinking
The proposed MySQL schema is detailed enough to make implementation concrete:
- work items
- workflow stages
- stage history
- approval queue
- agent status
- logs
- failures
- comments
- artifacts

That is valuable because it turns the dashboard from a UI dream into a backend plan.

### 4. Good auditability emphasis
The plan repeatedly favors:
- append-only stage history
- explicit approval decisions
- failure/retry tracking
- audit trail

That is the right instinct for a system that mixes automation and human approvals.

## Architectural assessment

### Recommended stack in the plan
- Backend: ASP.NET Core Web API
- UI: ASP.NET Core MVC / Razor first
- Database: MySQL
- Realtime: SignalR later
- Background: hosted services / workers

### Is this reasonable?
Yes, if the repo direction is already .NET-oriented and Forge is expected to build in C#.

### Why this is sensible
- server-rendered dashboard first is cheaper than a heavier SPA
- ASP.NET Core is fine for workflow APIs and background services
- MySQL is acceptable for structured workflow/approval state
- SignalR later is a sane incremental step

### Caveat on MySQL
The plan is reasonable for workflow state, but raw logs should be bounded.
The document itself hints at this correctly.

Recommendation:
- use MySQL for structured workflow state and summarized logs
- do not treat MySQL as an unlimited raw event dump forever

## Biggest implementation dependencies

This dashboard depends on several upstream workstreams becoming real, not just documented:

### 1. Work item lifecycle source of truth
Right now agent work is still spread across:
- chat/session activity
- repo PRs
- cron jobs
- local notes

For the dashboard to be truthful, there must be a real structured work item model.

### 2. Approval event plumbing
Olivia approval actions need real backing logic, not just UI buttons.
That means:
- queue creation rules
- approval/reroute APIs
- decision audit trail
- state transitions

### 3. Agent telemetry
The right panel depends on agents producing consistent:
- heartbeats
- status updates
- failure signals
- retry counts
- current work item references

### 4. PR/review/repo integration
If Forge and PR automation are part of the operating model, their state should feed the work item/approval system eventually.

### 5. Media/news and review automation maturity
The dashboard will look credible only if underlying flows are reliable.
Current known gaps still matter:
- Scout media briefing path/script gap
- Forge reviewer automation not fully end-to-end yet

## Best interpretation of the phases

### Phase 1 should stay simple
The phase-one board should be a real but mostly static operational shell.
That means:
- seeded data or lightweight real records
- no heavy realtime assumptions
- clear board layout
- Olivia queue summary
- right-panel summary widgets

This is good because it creates a visible product quickly.

### Phase 2 and 3 are where truth starts
Once transitions and approvals work, the dashboard stops being mostly presentation and becomes a real command surface.

### Phase 4 is crucial
The Sentinel/observability layer is what makes the dashboard operationally trustworthy.
Without that, it becomes mostly workflow theater.

## Risks in the current plan

### Risk 1: dashboard before data integrity
If UI gets built faster than the real workflow state model, the system may show impressive screens that are not operationally trustworthy.

Mitigation:
- build schema and state transitions first
- only surface fields that are actually backed by data

### Risk 2: overloading MySQL with raw logs
If everything is inserted as raw logs forever, this becomes noisy and harder to maintain.

Mitigation:
- keep logs bounded
- summarize where possible
- separate workflow facts from noisy event streams

### Risk 3: too many concepts in one release
There is a temptation to build:
- board
- approvals
- logs
- failures
- heartbeats
- realtime
- auth
all at once.

Mitigation:
- keep phase boundaries real
- do not pull SignalR/realtime too early

### Risk 4: unclear source of agent truth
The dashboard assumes each agent can reliably report status.
That is not fully true yet in the current operating environment.

Mitigation:
- define minimal agent status contracts early
- require only a small heartbeat/status payload first

## What I would recommend as the practical first build

### First milestone
Build only these things first:
1. MySQL schema and seed data
2. Board query and board UI
3. Olivia queue query and basic approval actions
4. Agent status summary widget
5. Failure/retry summary widget

Do not build full realtime or broad integration first.

### Why
Because this gives a usable dashboard shell and validates the data model quickly.

## Suggested dependency order

### Before or alongside dashboard phase 1
- finalize work item schema and state transitions
- define minimal agent heartbeat payload
- define approval queue behavior

### Before dashboard feels truly real
- make Forge PR workflow emit structured events eventually
- make Scout collection flows reliable
- improve unresolved-gap tracking and MOM generation linkage

## How this ties to token efficiency

This plan is useful for token/cost control if implemented well.

Why:
- status moves from chat reconstruction into durable structured records
- approvals become explicit items instead of conversational state
- MOM updates can pull from state instead of long reasoning every time
- Olivia can summarize from a dashboard backend rather than recreating context repeatedly

So this dashboard is not only a UI initiative. It can become part of the token-efficiency strategy.

## Fit with the memory implementation guide

The memory guide and dashboard guide complement each other.

### Memory guide gives:
- per-agent memory stores
- retrieval/reflection/token ledger
- learning and prompt compaction

### Dashboard guide gives:
- operational surface
- work item flow
- approval management
- status and failures visibility

Together they imply a stronger future architecture:
- memory layer for learning and efficient context
- command center layer for operational control and visibility

## Suggested backlog framing

This should be tracked as a major roadmap item with substreams:

1. Command center data model
2. Dashboard phase 1 shell
3. Approval system
4. Sentinel observability feed
5. Agent integration contracts
6. Realtime updates
7. Governance/auth hardening

## Recommended next actions

1. Keep this phase-wise dashboard plan in the backlog.
2. Treat the markdown file as the canonical editable implementation guide.
3. Ask Forge to convert this into repo-side roadmap docs and technical tasks when ready.
4. Ensure the dashboard work depends on real workflow data, not just UI mock state.
5. Pair this roadmap with the memory implementation roadmap, because together they create the strongest long-term system.

## Short conclusion

This is a strong implementation blueprint.

It is credible because it includes:
- a real data model
- phased delivery
- role-aligned workflow
- auditability
- operational visibility

The best way to proceed is not to build the whole dashboard immediately, but to preserve this as a structured roadmap and later have Forge implement phase 1 only after current foundational gaps are tightened.
