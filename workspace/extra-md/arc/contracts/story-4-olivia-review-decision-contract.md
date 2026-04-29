# Story 4. Olivia Review Context Contract and Olivia Decision Contract

**Status:** Redraft, not frozen  
**Owner:** Olivia review surface / decision layer  
**Purpose:** Define both the minimum review context Olivia must receive and the canonical decision artifact Olivia produces for a specific Atlas recommendation version.

### Part A. Olivia Review Context Contract

**Purpose**  
Before Olivia can review a recommendation, she must receive a minimum normalized review context tied to one exact Atlas recommendation version.

**Required fields**
- `review_context_id`
- `recommendation_id`
- `recommendation_version`
- `recommendation_snapshot`
- `rationale_summary`
- `recommended_action`
- `source_references`
- `recommendation_status`
- `review_outcome`
- `execution_state`
- `presented_at`

**Minimum review context Olivia receives**
1. exact `recommendation_id`
2. exact `recommendation_version`
3. rationale summary
4. structured recommended action
5. relevant provenance/source references
6. current values of:
   - `recommendation_status`
   - `review_outcome`
   - `execution_state`

**Normative rules**
1. Review context must reference one exact recommendation version.
2. Review context must contain enough information for Olivia to make a decision without ambiguity about which version is being reviewed.
3. Review context is read-only and should be treated as the decision input snapshot.
4. A later Atlas version requires a new review context and a new decision unless policy explicitly states otherwise.

**Canonical JSON example, review context**
```json
{
  "review_context_id": "rctx_01JQZ8T4K2G5M7N9P1R3S6U8V0",
  "recommendation_id": "rec_01JQZ8KQ7V6M2A4X9N3P1C5D8E",
  "recommendation_version": 3,
  "recommendation_snapshot": {
    "recommendation_id": "rec_01JQZ8KQ7V6M2A4X9N3P1C5D8E",
    "recommendation_version": 3,
    "rationale_summary": "Rollback is recommended because the current release correlates with a material error-rate increase and degraded payment completion.",
    "recommended_action": {
      "action_type": "rollback_deployment",
      "parameters": {
        "service": "payments-api",
        "target_version": "2026.04.18.3"
      }
    },
    "source_references": [
      {
        "source_type": "incident_report",
        "source_id": "inc_7841"
      },
      {
        "source_type": "dashboard",
        "source_uri": "grafana://payments/error-rate?from=2026-04-19T04:00:00Z"
      }
    ],
    "recommendation_status": "active",
    "review_outcome": "pending",
    "execution_state": "not_started"
  },
  "rationale_summary": "Rollback is recommended because the current release correlates with a material error-rate increase and degraded payment completion.",
  "recommended_action": {
    "action_type": "rollback_deployment",
    "parameters": {
      "service": "payments-api",
      "target_version": "2026.04.18.3"
    }
  },
  "source_references": [
    {
      "source_type": "incident_report",
      "source_id": "inc_7841"
    },
    {
      "source_type": "dashboard",
      "source_uri": "grafana://payments/error-rate?from=2026-04-19T04:00:00Z"
    }
  ],
  "recommendation_status": "active",
  "review_outcome": "pending",
  "execution_state": "not_started",
  "presented_at": "2026-04-19T06:10:00Z"
}
```

### Part B. Olivia Decision Contract

**Purpose**  
The Olivia decision contract records Olivia’s normalized review decision for one exact Atlas recommendation version.

**Required fields**
- `decision_id`
- `decision_version`
- `recommendation_id`
- `recommendation_version`
- `review_context_id`
- `decision_outcome`
- `conditions`
- `rationale`
- `annotations`
- `reviewer`
- `decided_at`

**Normalized decision outcome**
Allowed normalized outcomes:
- `approved`
- `rejected`
- `needs_revision`

**Rule:** Conditional approval is represented as:
- `decision_outcome = "approved"`
- plus non-empty structured `conditions`

There is no separate top-level outcome value for conditional approval.

**Structured conditions**
When Olivia approves with conditions, each condition should support:
- `condition_id`
- `type`
- `description`
- optional `must_be_satisfied_before`
- optional `verification_method`

**Reviewer metadata**
`reviewer` must include:
- `reviewer_id`
- `reviewer_role`
- optional `reviewer_display_name`

**Normative rules**
1. Every decision must reference one exact `recommendation_id` and `recommendation_version`.
2. Every decision must link to the `review_context_id` used during review.
3. `decision_outcome` must be normalized.
4. If approval is conditional, it must be encoded as `approved` plus structured `conditions`.
5. Free-text rationale does not replace structured decision fields.
6. A new recommendation version requires a separate decision record if reviewed.

**Canonical JSON example, unconditional approval**
```json
{
  "decision_id": "dec_01JQZ93J4M6N8P2R5T7V1X3Y9A",
  "decision_version": 1,
  "review_context_id": "rctx_01JQZ8T4K2G5M7N9P1R3S6U8V0",
  "recommendation_id": "rec_01JQZ8KQ7V6M2A4X9N3P1C5D8E",
  "recommendation_version": 3,
  "decision_outcome": "approved",
  "conditions": [],
  "rationale": "The rollback recommendation is supported by the incident evidence and should proceed immediately.",
  "annotations": [
    {
      "type": "priority",
      "value": "high"
    }
  ],
  "reviewer": {
    "reviewer_id": "olivia",
    "reviewer_role": "chief_of_staff",
    "reviewer_display_name": "Olivia"
  },
  "decided_at": "2026-04-19T06:14:00Z"
}
```

**Canonical JSON example, approval with structured conditions**
```json
{
  "decision_id": "dec_01JQZ94Q8A1C3E5G7J9L2N4P6R",
  "decision_version": 1,
  "review_context_id": "rctx_01JQZ8T4K2G5M7N9P1R3S6U8V0",
  "recommendation_id": "rec_01JQZ8KQ7V6M2A4X9N3P1C5D8E",
  "recommendation_version": 3,
  "decision_outcome": "approved",
  "conditions": [
    {
      "condition_id": "cond_001",
      "type": "verification",
      "description": "Confirm rollback plan with on-call engineer before execution.",
      "must_be_satisfied_before": "execution_start",
      "verification_method": "engineer_ack"
    }
  ],
  "rationale": "Approval is granted provided execution coordination is confirmed first.",
  "annotations": [],
  "reviewer": {
    "reviewer_id": "olivia",
    "reviewer_role": "chief_of_staff"
  },
  "decided_at": "2026-04-19T06:16:00Z"
}
```