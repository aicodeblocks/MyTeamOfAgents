# Story 3. Atlas Recommendation Contract

**Status:** Redraft, not frozen  
**Owner:** Atlas  
**Purpose:** Define the canonical contract for an Atlas recommendation artifact so recommendations can be versioned, reviewed, superseded, and executed without conflating recommendation state, review outcome, and execution state.

## Contract goals

The Atlas recommendation contract must:

1. represent a recommendation as a first-class versioned artifact
2. preserve provenance and rationale
3. support independent review by Olivia
4. support downstream execution tracking
5. explicitly separate:
   - **recommendation status**
   - **review outcome**
   - **execution state**

## Canonical entity

An Atlas recommendation is a versioned record produced by Atlas that proposes a specific action and can be reviewed, approved, rejected, superseded, or executed.

## Required fields

### Identity and versioning
- `recommendation_id`: stable identifier for the recommendation across versions
- `recommendation_version`: monotonically increasing version for that recommendation
- `version_created_at`: timestamp for creation of the specific version
- `supersedes_recommendation_version`: optional prior version number replaced by this version
- `superseded_by_recommendation_version`: optional later version number that replaces this version

### Provenance
- `source_references`: non-empty array of source/provenance references used by Atlas
- each source reference should support:
  - `source_type`
  - `source_id` or `source_uri`
  - optional `excerpt` or `locator`
  - optional `captured_at`

### Recommendation content
- `rationale_summary`: concise explanation of why Atlas is making the recommendation
- `recommended_action`: structured description of the action Atlas recommends
- `recommended_action.action_type`: normalized action category
- `recommended_action.parameters`: structured parameters for execution or implementation
- `recommended_action.expected_outcome`: optional intended result

### Status separation
The contract must maintain independent fields for the following three state dimensions:

1. **Recommendation status**: lifecycle of the recommendation artifact itself
   - field: `recommendation_status`
   - examples: `draft`, `active`, `superseded`, `withdrawn`, `archived`

2. **Review outcome**: latest review result from Olivia or another authorized reviewer
   - field: `review_outcome`
   - examples: `pending`, `approved`, `approved_with_conditions`, `rejected`, `needs_revision`

3. **Execution state**: implementation status of the recommended action
   - field: `execution_state`
   - examples: `not_started`, `queued`, `in_progress`, `completed`, `failed`, `canceled`

These fields are independent and must not be collapsed into one combined status.

### Review linkage
- `current_review_id`: optional identifier of latest linked review/decision record
- `reviewed_recommendation_version`: optional exact version reviewed, when review exists

### Timestamps
- `created_at`: timestamp for initial recommendation creation
- `updated_at`: timestamp for any mutation to this version record
- `reviewed_at`: optional timestamp of latest review outcome
- `execution_updated_at`: optional timestamp of latest execution-state change

## Normative rules

1. `recommendation_id` must remain stable across versions of the same recommendation.
2. `recommendation_version` must increment for each revised recommendation version.
3. Each review must reference an exact `recommendation_id` plus `recommendation_version`.
4. If a version replaces a prior version, supersession must be explicitly represented.
5. `recommendation_status`, `review_outcome`, and `execution_state` must be stored separately and interpreted independently.
6. A recommendation may be:
   - `active` while `review_outcome = pending`
   - `active` while `review_outcome = approved`
   - `superseded` even if `execution_state = completed`
7. `recommended_action` must be structured enough for downstream systems to interpret without relying on free text alone.
8. `source_references` must be sufficient for auditability.
9. `rationale_summary` must be human-readable and concise, but not replace structured provenance.

## Canonical JSON example

```json
{
  "recommendation_id": "rec_01JQZ8KQ7V6M2A4X9N3P1C5D8E",
  "recommendation_version": 3,
  "created_at": "2026-04-19T05:40:00Z",
  "updated_at": "2026-04-19T06:05:00Z",
  "version_created_at": "2026-04-19T06:05:00Z",
  "supersedes_recommendation_version": 2,
  "superseded_by_recommendation_version": null,
  "source_references": [
    {
      "source_type": "incident_report",
      "source_id": "inc_7841",
      "locator": "section:summary",
      "excerpt": "Error rate increased 18% after deployment.",
      "captured_at": "2026-04-19T05:35:12Z"
    },
    {
      "source_type": "dashboard",
      "source_uri": "grafana://payments/error-rate?from=2026-04-19T04:00:00Z",
      "locator": "panel:7",
      "captured_at": "2026-04-19T05:36:10Z"
    }
  ],
  "rationale_summary": "Rollback is recommended because the current release correlates with a material error-rate increase and degraded payment completion.",
  "recommended_action": {
    "action_type": "rollback_deployment",
    "parameters": {
      "service": "payments-api",
      "target_version": "2026.04.18.3"
    },
    "expected_outcome": "Restore pre-deployment error rate and stabilize payment processing."
  },
  "recommendation_status": "active",
  "review_outcome": "pending",
  "execution_state": "not_started",
  "current_review_id": null,
  "reviewed_recommendation_version": null,
  "reviewed_at": null,
  "execution_updated_at": null
}
```