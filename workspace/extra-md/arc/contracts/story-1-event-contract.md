# Story 1 Event Contract

## Overview
Story 1 defines the canonical ARC event envelope. It owns the base event fields, identifier model, correlation model, and shared enums consumed by downstream stories.

## Scope and non-goals
**Scope**
- Canonical event schema for ARC event emission and storage
- Shared enum ownership for `reason_code`, `severity`, and `decision_mode`
- Base identifiers and correlation semantics used by Story 2 and later stories
- Event lifecycle/status values

**Non-goals**
- Signal scoring semantics, confidence bands, or mapping logic (owned by Story 5)
- Ordering guarantees or reconciliation rules beyond explicit references to Story 5 ownership
- Downstream signal-specific fields

## Schema
### Required fields
| Field | Type | Description | Owning story |
| --- | --- | --- | --- |
| `schema_version` | string | Contract version for the event payload, example `"1.0"` | Story 1 |
| `event_id` | string | Globally unique identifier for this event instance | Story 1 |
| `event_type` | string | Canonical ARC event type name, example `"arc.event.detected"` | Story 1 |
| `occurred_at` | string (RFC 3339 UTC) | Time the source system says the event occurred | Story 1 |
| `emitted_at` | string (RFC 3339 UTC) | Time the ARC pipeline emitted the envelope | Story 1 |
| `source` | object | Source system metadata block | Story 1 |
| `subject` | object | Canonical subject of the event | Story 1 |
| `reason_code` | string enum | Primary normalized reason for the event | Story 1 |
| `severity` | string enum | Normalized severity classification | Story 1 |
| `decision_mode` | string enum | How the upstream decision was made | Story 1 |
| `status` | string enum | Current event lifecycle state | Story 1 |
| `correlation` | object | Correlation and trace identifiers | Story 1 |
| `payload` | object | Event-type-specific details carried inside the canonical envelope | Story 1 |

### Optional fields
| Field | Type | Description | Owning story |
| --- | --- | --- | --- |
| `tenant_id` | string | Tenant or workspace identifier when multitenant | Story 1 |
| `source_event_id` | string | Original identifier from the source system | Story 1 |
| `source_parent_event_id` | string | Parent event identifier from the source if present | Story 1 |
| `actor` | object | Actor that triggered the event, user or system | Story 1 |
| `status_reason` | string | Free-text explanation for the current event status | Story 1 |
| `tags` | array of string | Non-authoritative labels for indexing or diagnostics | Story 1 |
| `metadata` | object | Additional source metadata that does not change semantics | Story 1 |

### Required nested objects
**`source`**
- `system` string
- `kind` string

Optional:
- `region` string
- `environment` string

**`subject`**
- `subject_type` string
- `subject_id` string

Optional:
- `subject_ref` string

**`correlation`**
- `trace_id` string
- `correlation_id` string
- `causation_id` string

Optional:
- `dedup_key` string, consumed by Story 5 reconciliation rules
- `group_key` string

## Enums
### `reason_code` (owned by Story 1)
- `token_threshold`
- `message_volume`
- `session_age`
- `checkpoint_interval`
- `manual_request`
- `error_recovery`
- `state_transition`
- `context_pressure`
- `archive_policy`
- `integrity_guard`

### `severity` (owned by Story 1)
- `low`
- `medium`
- `high`
- `critical`

### `decision_mode` (owned by Story 1)
- `manual`
- `auto`

### `status` (owned by Story 1, transitions constrained by Story 5)
- `observed`
- `accepted`
- `rejected`
- `superseded`
- `archived`

## Lifecycle / statuses
- `observed`: event entered the canonical ARC pipeline
- `accepted`: event passed validation and is retained as an active canonical event
- `rejected`: event failed validation or was intentionally dropped
- `superseded`: event is retained for traceability but replaced by a newer canonical event
- `archived`: event is inactive and retained only for history

State transition rules are owned by Story 5. Story 1 only freezes the allowed status vocabulary.

## Ordering guarantees and non-guarantees
**Guarantees**
- None are defined by Story 1. Ordering ownership is delegated to Story 5.

**Non-guarantees**
- Consumers must not assume arrival order equals occurrence order.
- Consumers must not assume contiguous sequencing within a correlation group.
- Replays may produce older events after newer ones.

## Confidence model (if applicable)
Not applicable for the event contract. Confidence scoring and banding are owned by Story 5 and consumed by Story 2.

## Correlation and identifiers
- `event_id` is immutable and unique per canonical event envelope.
- `source_event_id` preserves the upstream source identifier when available.
- `trace_id` identifies end-to-end processing across systems.
- `correlation_id` groups related events and signals for the same ARC workflow or case.
- `causation_id` points to the immediately preceding event or command that caused this event.
- `dedup_key` is an optional stable key used by Story 5 reconciliation and dedup logic.
- `group_key` is an optional grouping helper for UI and aggregation, with no ordering semantics by itself.

## Dependencies (explicit ownership mapping)
| Item | Owner | Notes |
| --- | --- | --- |
| Base event fields | Story 1 | Source of truth for downstream contracts |
| Identifier definitions | Story 1 | Shared semantics |
| Correlation model | Story 1 | Shared semantics |
| `reason_code` enum | Story 1 | Shared by Story 2 |
| `severity` enum | Story 1 | Shared by Story 2 |
| `decision_mode` enum | Story 1 | Shared by Story 2 |
| Event status vocabulary | Story 1 | Story 5 owns transitions |
| Ordering rules | Story 5 | Referenced, not redefined |
| Dedup and reconciliation rules | Story 5 | Referenced by `dedup_key` |
| Confidence model | Story 5 | Not present on Story 1 event payload |

## Canonical JSON example(s)
```json
{
  "schema_version": "1.0",
  "event_id": "evt_01JARC9M6S93M7E9W7K6P2V4TQ",
  "event_type": "arc.event.detected",
  "occurred_at": "2026-04-19T04:55:12Z",
  "emitted_at": "2026-04-19T04:55:14Z",
  "tenant_id": "tenant_ops_east",
  "source_event_id": "src_884421",
  "source": {
    "system": "ops-monitor",
    "kind": "detector",
    "region": "us-east-1",
    "environment": "prod"
  },
  "subject": {
    "subject_type": "service",
    "subject_id": "svc.arc-gateway",
    "subject_ref": "gateway/arc-gateway"
  },
  "reason_code": "token_threshold",
  "severity": "high",
  "decision_mode": "auto",
  "status": "accepted",
  "correlation": {
    "trace_id": "trc_01JARC9M4Y7W5Y7XJ2N0CK6A6N",
    "correlation_id": "cor_01JARC9M5W1VC4NGX6XQK3VHP4",
    "causation_id": "cmd_01JARC9M3M0BQK0N2P1Q1M6YXD",
    "dedup_key": "svc.arc-gateway:token_threshold:2026-04-19T04:55",
    "group_key": "case_gateway_health"
  },
  "payload": {
    "metric": "context_window_usage",
    "current_value": 0.82,
    "threshold": 0.8,
    "unit": "ratio"
  },
  "tags": ["gateway", "health"],
  "metadata": {
    "detector_version": "2026.04.18.2"
  }
}
```