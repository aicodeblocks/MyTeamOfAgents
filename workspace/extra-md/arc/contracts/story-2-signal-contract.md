# Story 2 Signal Contract

## Overview
Story 2 defines the canonical ARC signal contract generated from one or more accepted Story 1 events. It consumes Story 1 base semantics and Story 5 ordering, confidence, and reconciliation rules without redefining them.

## Scope and non-goals
**Scope**
- Canonical signal schema
- Signal lifecycle/status vocabulary
- Required linkage back to source event(s)
- Canonical signal example for downstream implementation

**Non-goals**
- Ownership of shared enums `reason_code`, `severity`, `decision_mode` (Story 1)
- Ownership of confidence score, band mapping, or thresholds (Story 5)
- Ownership of ordering, dedup, reconciliation, or transition rules (Story 5)

## Schema
### Required fields
| Field | Type | Description | Owning story |
| --- | --- | --- | --- |
| `schema_version` | string | Contract version for the signal payload | Story 2 |
| `signal_id` | string | Immutable canonical signal identifier | Story 2 |
| `signal_type` | string | Canonical ARC signal type name, example `"arc.signal.risk"` | Story 2 |
| `created_at` | string (RFC 3339 UTC) | Time the canonical signal was created | Story 2 |
| `updated_at` | string (RFC 3339 UTC) | Last material update timestamp for the signal | Story 2 |
| `status` | string enum | Current signal lifecycle state | Story 2 |
| `subject` | object | Canonical subject carried forward from Story 1 | Story 1 |
| `reason_code` | string enum | Primary normalized reason code | Story 1 |
| `severity` | string enum | Normalized severity classification | Story 1 |
| `decision_mode` | string enum | How the signal was created or promoted | Story 1 |
| `correlation` | object | Shared correlation object | Story 1 |
| `source_event_ids` | array of string | Event identifiers that materially contributed to this signal | Story 2 |
| `summary` | object | Human and machine-readable signal summary | Story 2 |
| `confidence` | object | Confidence block, semantics owned by Story 5 | Story 5 |

### Optional fields
| Field | Type | Description | Owning story |
| --- | --- | --- | --- |
| `primary_event_id` | string | Main originating event when one source event is dominant | Story 2 |
| `tenant_id` | string | Tenant or workspace identifier | Story 1 |
| `assigned_queue` | string | Workflow or routing queue | Story 2 |
| `status_reason` | string | Free-text explanation for the current signal status | Story 2 |
| `related_signal_ids` | array of string | Related canonical signals for cross-linking | Story 2 |
| `annotations` | array of object | Human or automated annotations attached to the signal | Story 2 |
| `metadata` | object | Non-authoritative implementation metadata | Story 2 |

### Required nested objects
**`summary`**
- `title` string
- `description` string

Optional:
- `recommended_action` string

**`confidence`**
- `confidence_score` number from 0.0 to 1.0, owned by Story 5
- `confidence_band` string enum, owned by Story 5

Optional:
- `explanation` string

## Enums
### Shared enums consumed from Story 1
- `reason_code`
- `severity`
- `decision_mode`

Story 2 must not redefine the allowed values.

### `status` (owned by Story 2, transitions constrained by Story 5)
- `open`
- `triaged`
- `escalated`
- `resolved`
- `suppressed`
- `superseded`

## Lifecycle / statuses
- `open`: signal exists and requires review or downstream handling
- `triaged`: signal has been reviewed and categorized
- `escalated`: signal was promoted for higher-priority action
- `resolved`: signal outcome was completed
- `suppressed`: signal is intentionally hidden from action queues
- `superseded`: signal remains for traceability but is replaced by another signal

Transition rules are owned by Story 5. Story 2 freezes the allowed vocabulary only.

## Ordering guarantees and non-guarantees
**Guarantees**
- Story 2 inherits Story 5 ordering boundaries and does not define its own.

**Non-guarantees**
- `source_event_ids` order is not authoritative unless Story 5 explicitly marks a boundary.
- `updated_at` must not be used as a proxy for causal ordering across different signals.
- Consumers must tolerate replay, late arrival, and supersession.

## Confidence model (if applicable)
Confidence is required on the signal contract, but the model is owned by Story 5.
- `confidence.confidence_score` is a normalized numeric score from `0.0` to `1.0` inclusive.
- `confidence.confidence_band` is the mapped qualitative band.
- Mapping rules and thresholds are defined only in Story 5.

## Correlation and identifiers
- `signal_id` is immutable and unique per canonical signal.
- `source_event_ids` must contain at least one accepted Story 1 `event_id`.
- `primary_event_id`, if present, must also exist in `source_event_ids`.
- `correlation.trace_id`, `correlation.correlation_id`, and `correlation.causation_id` reuse Story 1 semantics.
- `correlation.dedup_key` participates in Story 5 reconciliation and dedup processing.

## Dependencies (explicit ownership mapping)
| Item | Owner | Notes |
| --- | --- | --- |
| Signal-specific required fields | Story 2 | `signal_id`, `signal_type`, timestamps, summary, source links |
| Signal status vocabulary | Story 2 | Story 5 owns transitions |
| Shared subject and correlation model | Story 1 | Consumed directly |
| Shared enums | Story 1 | Consumed directly |
| Confidence model (`confidence_score`, `confidence_band`) | Story 5 | Required on Story 2, not defined here |
| Ordering guarantees and boundaries | Story 5 | Inherited |
| Reconciliation and dedup rules | Story 5 | Inherited |

## Canonical JSON example(s)
```json
{
  "schema_version": "1.0",
  "signal_id": "sig_01JARCB1D7Y0W7SGR6R6A3D3KT",
  "signal_type": "arc.signal.risk",
  "created_at": "2026-04-19T04:55:20Z",
  "updated_at": "2026-04-19T04:56:01Z",
  "tenant_id": "tenant_ops_east",
  "status": "open",
  "subject": {
    "subject_type": "service",
    "subject_id": "svc.arc-gateway",
    "subject_ref": "gateway/arc-gateway"
  },
  "reason_code": "token_threshold",
  "severity": "high",
  "decision_mode": "auto",
  "correlation": {
    "trace_id": "trc_01JARC9M4Y7W5Y7XJ2N0CK6A6N",
    "correlation_id": "cor_01JARC9M5W1VC4NGX6XQK3VHP4",
    "causation_id": "evt_01JARC9M6S93M7E9W7K6P2V4TQ",
    "dedup_key": "svc.arc-gateway:token_threshold:2026-04-19T04:55",
    "group_key": "case_gateway_health"
  },
  "source_event_ids": [
    "evt_01JARC9M6S93M7E9W7K6P2V4TQ"
  ],
  "primary_event_id": "evt_01JARC9M6S93M7E9W7K6P2V4TQ",
  "summary": {
    "title": "Gateway context pressure exceeded threshold",
    "description": "ARC promoted the accepted token threshold event into an actionable risk signal for the gateway service.",
    "recommended_action": "Review recent activity and reduce context load if token pressure remains above threshold for 10 minutes."
  },
  "confidence": {
    "confidence_score": 0.87,
    "confidence_band": "high",
    "explanation": "Mapped by Story 5 confidence thresholds."
  },
  "assigned_queue": "ops-triage",
  "metadata": {
    "producer": "arc-signal-service"
  }
}
```