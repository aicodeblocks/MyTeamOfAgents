# DSB Project Backlog

Project code: DSB
Project name: OpenClaw Dashboard / Command Center
Project state: Planning only
Implementation rule: No repo/code work starts until Mansoor reviews and is happy with the whole-project story breakdown.

## Project objective

Design and prepare a multi-agent command center that gives Mansoor and Olivia one place to manage:
- workflow state
- Olivia approvals
- agent ownership and status
- logs, failures, retries, and alerts
- future MOM/reporting inputs

## Working model for this project

- Olivia owns project coordination, backlog shape, blockers, and decisions.
- Atlas supports analysis and decomposition when deeper planning is needed.
- Forge should only execute once stories are approved.
- Sentinel should later review risk, hardening, and observability requirements.
- Ranger is not a primary owner for this project unless deployment/home-host concerns arise.

## Scrum recommendation for DSB

### Daily rhythm
- Use the existing 11 AM MOM update for project status.

### Backlog refinement rhythm
Recommended recurring review points:
- Tuesday 11:30 AM America/New_York
- Friday 11:30 AM America/New_York

Purpose of these sessions:
- break larger items into smaller stories
- reprioritize
- identify blockers
- decide what is ready for Forge
- capture open decisions for Mansoor

## Workflow columns for planning
- Backlog
- Ready for Breakdown
- Ready for Review
- Ready for Forge
- Blocked
- Waiting for Mansoor
- Done
- Deferred

## Epic map

### DSB-EPIC-01 Command center foundations
Goal: define the core project structure, data model, vocabulary, and operating rules.

### DSB-EPIC-02 Workflow board and work item lifecycle
Goal: model and later support the board, stage movement, audit history, tags, timers, and workflow rules.

### DSB-EPIC-03 Olivia approvals and decision control
Goal: support approval queue behavior, decision actions, reroutes, SLA/priority handling, and decision history.

### DSB-EPIC-04 Sentinel observability and operational visibility
Goal: represent agent health, logs, failures, retries, alerts, and operational trust.

### DSB-EPIC-05 Agent integration contracts
Goal: define how Scout, Atlas, Forge, Sentinel, and Olivia update the platform consistently.

### DSB-EPIC-06 Reporting, MOM, and operational summaries
Goal: make the system produce useful summaries for daily reporting and management visibility.

### DSB-EPIC-07 Governance, auth, and production controls
Goal: define permissions, audit integrity, retention, backup, and admin controls.

## First-pass stories

---

## DSB-01 Define project vocabulary and canonical workflow
Epic: DSB-EPIC-01
Owner: Olivia
Status: Ready for Review
Goal:
Create one canonical definition of agents, stages, states, approval states, and key terms so future planning and implementation do not drift.
Definition of done:
- canonical list of agent roles agreed
- canonical stage order agreed
- canonical status vocabulary defined
- approval-related terms defined
Dependencies:
- dashboard concept analysis
- dashboard phase-wise plan analysis
Needs Mansoor: Yes

## DSB-02 Define project success criteria
Epic: DSB-EPIC-01
Owner: Olivia
Status: Ready for Review
Goal:
Define what success looks like for phase 1, for the overall dashboard, and for later operational trust.
Definition of done:
- phase 1 success criteria listed
- phase 2+ success criteria summarized
- non-goals captured
Dependencies:
- DSB-01
Needs Mansoor: Yes

## DSB-03 Define the command-center data domains
Epic: DSB-EPIC-01
Owner: Atlas
Status: Backlog
Goal:
Break the dashboard into clean domains such as work items, approvals, agent status, logs, failures, artifacts, and reporting.
Definition of done:
- domain list documented
- responsibilities per domain written
- overlap/conflict notes captured
Dependencies:
- DSB-01
Needs Mansoor: No

## DSB-04 Decide the planning-first implementation boundaries
Epic: DSB-EPIC-01
Owner: Olivia
Status: Ready for Review
Goal:
Decide what must be fully designed before Forge writes any code.
Definition of done:
- planning gate checklist defined
- “ready for Forge” criteria defined
Dependencies:
- DSB-01
- DSB-02
Needs Mansoor: Yes

---

## DSB-05 Define workflow stages and allowed transitions
Epic: DSB-EPIC-02
Owner: Atlas
Status: Backlog
Goal:
Specify the default forward path, reroute rules, invalid jumps, and completion behavior.
Definition of done:
- stage transition matrix documented
- default path defined
- reroute authority defined
Dependencies:
- DSB-01
Needs Mansoor: Maybe

## DSB-06 Define work item schema at business level
Epic: DSB-EPIC-02
Owner: Atlas
Status: Backlog
Goal:
Define business fields for work items before technical schema implementation.
Definition of done:
- required fields listed
- optional fields listed
- field purpose explained
- business rules noted
Dependencies:
- DSB-03
Needs Mansoor: No

## DSB-07 Define stage history and audit requirements
Epic: DSB-EPIC-02
Owner: Olivia
Status: Backlog
Goal:
Ensure every movement and important action has a trustworthy audit model.
Definition of done:
- events requiring history are listed
- minimum audit fields defined
Dependencies:
- DSB-05
- DSB-06
Needs Mansoor: No

## DSB-08 Define board card information model
Epic: DSB-EPIC-02
Owner: Olivia
Status: Backlog
Goal:
Define exactly what each kanban card must display to be useful and not noisy.
Definition of done:
- card fields listed
- must-have vs nice-to-have separated
Dependencies:
- DSB-06
Needs Mansoor: Maybe

---

## DSB-09 Define approval queue lifecycle
Epic: DSB-EPIC-03
Owner: Atlas
Status: Backlog
Goal:
Define when items enter approval, what states the queue supports, and how items leave the queue.
Definition of done:
- queue lifecycle documented
- entry criteria defined
- exit criteria defined
Dependencies:
- DSB-01
- DSB-05
Needs Mansoor: No

## DSB-10 Define Olivia decision actions and effects
Epic: DSB-EPIC-03
Owner: Olivia
Status: Ready for Review
Goal:
Specify approve, reject, reroute, defer, and request-info behavior if used.
Definition of done:
- each action defined
- impact on workflow defined
- audit note requirements defined
Dependencies:
- DSB-09
Needs Mansoor: Yes

## DSB-11 Define SLA and priority behavior for approvals
Epic: DSB-EPIC-03
Owner: Atlas
Status: Backlog
Goal:
Define how urgency and aging should appear and when escalation happens.
Definition of done:
- priority rules documented
- SLA/aging logic outlined
Dependencies:
- DSB-09
Needs Mansoor: Maybe

---

## DSB-12 Define agent heartbeat/status contract
Epic: DSB-EPIC-04
Owner: Atlas
Status: Backlog
Goal:
Define the minimum payload each agent must report for trustworthy status display.
Definition of done:
- required status fields listed
- heartbeat timing assumptions listed
- offline threshold proposal included
Dependencies:
- DSB-03
Needs Mansoor: No

## DSB-13 Define logs/failures/retries visibility model
Epic: DSB-EPIC-04
Owner: Sentinel
Status: Backlog
Goal:
Define what operational data should appear in the right panel without becoming noisy.
Definition of done:
- log categories defined
- failure model defined
- retry model defined
- retention guidance proposed
Dependencies:
- DSB-03
Needs Mansoor: No

## DSB-14 Define alert severity and escalation model
Epic: DSB-EPIC-04
Owner: Sentinel
Status: Backlog
Goal:
Define how the system distinguishes info, warning, error, and urgent operator attention.
Definition of done:
- severity levels defined
- escalation triggers documented
Dependencies:
- DSB-13
Needs Mansoor: Maybe

---

## DSB-15 Define common agent integration payloads
Epic: DSB-EPIC-05
Owner: Atlas
Status: Backlog
Goal:
Standardize how each agent reports progress, results, and failures.
Definition of done:
- shared payload fields listed
- idempotency concerns noted
- per-agent variations noted
Dependencies:
- DSB-06
- DSB-12
- DSB-13
Needs Mansoor: No

## DSB-16 Define artifact/reference model
Epic: DSB-EPIC-05
Owner: Olivia
Status: Backlog
Goal:
Define how outputs like reports, links, PRs, files, and notes attach to work items.
Definition of done:
- artifact types listed
- required metadata listed
Dependencies:
- DSB-06
Needs Mansoor: No

## DSB-17 Define external integration boundary
Epic: DSB-EPIC-05
Owner: Olivia
Status: Backlog
Goal:
Decide what the dashboard must know about GitHub, cron, sessions, and future external systems.
Definition of done:
- integration list documented
- in-scope vs later split defined
Dependencies:
- DSB-15
- DSB-16
Needs Mansoor: Yes

---

## DSB-18 Define MOM/reporting outputs from dashboard state
Epic: DSB-EPIC-06
Owner: Olivia
Status: Backlog
Goal:
Define which summaries the dashboard should be able to generate for daily management reporting.
Definition of done:
- MOM summary fields listed
- daily report candidate outputs listed
Dependencies:
- DSB-06
- DSB-09
- DSB-13
Needs Mansoor: Maybe

## DSB-19 Define summary/report metrics
Epic: DSB-EPIC-06
Owner: Atlas
Status: Backlog
Goal:
Define useful management and operational metrics such as queue aging, stage time, retries, throughput, and approval load.
Definition of done:
- metric list documented
- metric purpose explained
Dependencies:
- DSB-18
Needs Mansoor: No

---

## DSB-20 Define permission and governance model
Epic: DSB-EPIC-07
Owner: Sentinel
Status: Backlog
Goal:
Define who can view, approve, reroute, administer, and audit the system.
Definition of done:
- roles defined
- action permissions mapped
Dependencies:
- DSB-10
- DSB-17
Needs Mansoor: Maybe

## DSB-21 Define data retention and audit integrity rules
Epic: DSB-EPIC-07
Owner: Sentinel
Status: Backlog
Goal:
Define how history, logs, and sensitive records should be retained and protected.
Definition of done:
- retention guidance documented
- audit integrity principles listed
Dependencies:
- DSB-13
- DSB-20
Needs Mansoor: No

## DSB-22 Define readiness gate for first implementation sprint
Epic: DSB-EPIC-07
Owner: Olivia
Status: Ready for Review
Goal:
Create the gate that says when DSB is ready for Forge to start implementation.
Definition of done:
- planning checklist complete
- mandatory approved stories identified
- first build slice identified
Dependencies:
- DSB-04
- DSB-05
- DSB-06
- DSB-09
- DSB-12
- DSB-13
Needs Mansoor: Yes

## Current blockers

### DSB-BLK-01 No final approved story set yet
Impact:
Forge should not start implementation yet.
Owner:
Olivia

### DSB-BLK-02 Workflow and approval vocabulary may still drift
Impact:
Could create rework if implementation starts too early.
Owner:
Olivia

### DSB-BLK-03 Underlying real-world integrations are not yet stable
Examples:
- Scout media ingestion still blocked by missing script
- Forge reviewer automation still incomplete
Impact:
Dashboard credibility depends on truthful operational feeds.
Owner:
Olivia

### DSB-BLK-04 Source of truth for agent status is not yet formalized
Impact:
System visibility could become cosmetic instead of trustworthy.
Owner:
Atlas

## Current decisions

### DSB-DEC-01 Planning-first rule
Decision:
No repo/code starts until Mansoor is happy with the whole-project story breakdown.
Owner:
Mansoor
Status:
Approved

### DSB-DEC-02 Dashboard is a command center, not just a task board
Decision:
The system must combine workflow state and operational state.
Owner:
Mansoor + Olivia
Status:
Approved

### DSB-DEC-03 Olivia is the coordination and approval authority
Decision:
Olivia owns backlog shape, approvals model, blockers, and decision tracking.
Owner:
Mansoor
Status:
Approved

### DSB-DEC-04 Default future project process is standardized
Decision:
Future projects will follow the same pattern: project code, epic/story breakdown, blockers/decisions tracking, story-sized execution, MOM reporting, and twice-weekly scrum refinement.
Owner:
Mansoor
Status:
Approved

## Suggested first review set for Mansoor

Review these first before deeper decomposition:
- DSB-01 Define project vocabulary and canonical workflow
- DSB-02 Define project success criteria
- DSB-04 Decide planning-first implementation boundaries
- DSB-10 Define Olivia decision actions and effects
- DSB-22 Define readiness gate for first implementation sprint

## Suggested first stories that could later become Forge-ready earliest

These are the best candidates for earliest future implementation once approved:
- DSB-05 Define workflow stages and allowed transitions
- DSB-06 Define work item schema at business level
- DSB-09 Define approval queue lifecycle
- DSB-12 Define agent heartbeat/status contract
- DSB-13 Define logs/failures/retries visibility model

## Short executive summary

DSB is now shaped as a planning-first project with:
- 7 epics
- 22 first-pass stories
- 4 active blockers
- 4 explicit decisions

No code should begin until Mansoor reviews the story map and approves the implementation gate.
