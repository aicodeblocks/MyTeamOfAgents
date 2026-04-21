# Story 5 Rules Mapping

## Overview
This is the early Story 5 output required to unblock Story 1 and Story 2 review. It defines ownership mapping, ordering boundaries, the approved confidence model, transition-rule ownership, and unresolved edge cases. It is intentionally not a full schema.

## Scope and non-goals
**Scope**
- Ownership mapping for enums, required fields, statuses, and rules
- Ordering boundary definition
- Approved confidence model definition for downstream contracts
- State transition and reconciliation ownership summary
- Unresolved edge case list

**Non-goals**
- Full standalone event or signal schema
- Redefinition of Story 1 or Story 2 field shapes
- UI or transport implementation details

## Schema
### Required fields
| Field | Type | Description | Owning story |
| --- | --- | --- | --- |
| `ownership_mapping` | object | Source-of-truth ownership map for enums, fields, statuses, and rules | Story 5 |
| `ordering_boundary` | object | Authoritative ordering guarantees and non-guarantees | Story 5 |
| `confidence_model` | object | Approved confidence score and band model | Story 5 |
| `transition_rule_ownership` | object | Ownership summary for event and signal transition rules | Story 5 |
| `unresolved_edge_cases` | array of string | Open questions requiring joint review | Story 5 |

### Optional fields
Not applicable.

## Enums
### Ownership mapping: enum -> owning story
| Enum | Owner | Consumers |
| --- | --- | --- |
| `reason_code` | Story 1 | Story 2 and downstream |
| `severity` | Story 1 | Story 2 and downstream |
| `decision_mode` | Story 1 | Story 2 and downstream |
| `confidence_band` | Story 5 | Story 2 and downstream |

### `confidence_band` values (owned by Story 5)
- `low`
- `medium`
- `high`

## Lifecycle / statuses
### Ownership mapping: status -> owning story
| Status set | Owner | Notes |
| --- | --- | --- |
| Event statuses `observed`, `accepted`, `rejected`, `superseded`, `archived` | Story 1 vocabulary, Story 5 transition rules | Story 5 owns allowable transitions and terminal-state behavior |
| Signal statuses `open`, `triaged`, `escalated`, `resolved`, `suppressed`, `superseded` | Story 2 vocabulary, Story 5 transition rules | Story 5 owns allowable transitions and terminal-state behavior |

### Transition rule ownership
Story 5 owns:
- valid status transitions
- terminal state behavior
- supersession semantics
- reopening rules
- reconciliation-triggered status updates

## Ordering guarantees and non-guarantees
### Ordering boundary definition
1. **Authoritative time fields**
   - `occurred_at` is the authoritative business-event time for events.
   - `created_at` is the authoritative creation time for signals.
   - `emitted_at` and `updated_at` are processing timestamps only.

2. **Guaranteed ordering boundary**
   - Within a single `correlation.correlation_id`, consumers may order events by `occurred_at` and use `event_id` as a deterministic tie-breaker only for display or stable processing.
   - Within a single signal record, `updated_at` is monotonic for that record.

3. **Explicit non-guarantees**
   - No global total ordering across different `correlation_id` values.
   - No guarantee that ingest order equals `occurred_at` order.
   - No guarantee that `source_event_ids` array order carries causal meaning.
   - No guarantee that replayed or reconciled records arrive after earlier versions.

4. **Late-arrival boundary**
   - Late events may be attached to an existing signal if reconciliation rules judge them materially relevant.
   - Consumers must tolerate older `occurred_at` values arriving after newer accepted records.

## Confidence model (if applicable)
### Confidence model definition
Story 5 owns the confidence model used by Story 2 and later contracts.

**Fields**
- `confidence_score` is a numeric value from `0.0` to `1.0` inclusive.
- `confidence_band` is a derived enum with approved values `low`, `medium`, `high`.

**Band mapping**
| Score range | Band |
| --- | --- |
| `0.00–0.39` | `low` |
| `0.40–0.74` | `medium` |
| `0.75–1.00` | `high` |

**Rules**
- `confidence_band` is derived from `confidence_score`, never independently authored.
- If `confidence_score` changes enough to cross a band threshold, the signal is materially updated.
- Story 2 must carry both `confidence_score` and `confidence_band` but must not redefine thresholds.

## Correlation and identifiers
Story 5 consumes Story 1 identifier semantics and adds rule ownership for how they are used.
- `dedup_key` is the primary hook for reconciliation and dedup evaluation.
- `correlation_id` is the primary grouping boundary for ordering and cross-record linkage.
- `causation_id` is used to trace direct lineage but does not itself define sort order.

## Dependencies (explicit ownership mapping)
### Required field -> owning story
| Required field or rule artifact | Owner |
| --- | --- |
| Event envelope required fields | Story 1 |
| Signal record required fields | Story 2 |
| `confidence_score` | Story 5 |
| `confidence_band` | Story 5 |
| Ordering boundary rules | Story 5 |
| Transition rules | Story 5 |
| Reconciliation and dedup rules | Story 5 |

### Rule -> owning story
| Rule | Owner |
| --- | --- |
| Shared enum vocabulary | Story 1 |
| Shared field and identifier semantics | Story 1 |
| Event status vocabulary | Story 1 |
| Signal status vocabulary | Story 2 |
| Event and signal transition legality | Story 5 |
| Ordering guarantees and non-guarantees | Story 5 |
| Confidence score normalization and band mapping | Story 5 |
| Dedup and reconciliation behavior | Story 5 |

## Canonical JSON example(s)
```json
{
  "story": 5,
  "rule_artifacts": {
    "ownership_mapping": {
      "enums": {
        "reason_code": "story-1",
        "severity": "story-1",
        "decision_mode": "story-1",
        "confidence_band": "story-5"
      },
      "required_fields": {
        "event.schema_version": "story-1",
        "event.event_id": "story-1",
        "signal.signal_id": "story-2",
        "signal.confidence.confidence_score": "story-5",
        "signal.confidence.confidence_band": "story-5"
      },
      "statuses": {
        "event": "story-1 vocabulary + story-5 transitions",
        "signal": "story-2 vocabulary + story-5 transitions"
      },
      "rules": {
        "ordering": "story-5",
        "confidence_mapping": "story-5",
        "reconciliation": "story-5"
      }
    },
    "ordering_boundary": {
      "within_correlation_id": "order by occurred_at, tie-break by event_id for stable processing only",
      "global_ordering": "not guaranteed",
      "late_arrival": "allowed"
    },
    "confidence_model": {
      "confidence_score_range": [0.0, 1.0],
      "confidence_band_mapping": {
        "low": [0.0, 0.39],
        "medium": [0.4, 0.74],
        "high": [0.75, 1.0]
      }
    }
  }
}
```

## Unresolved edge cases
- Whether `accepted -> rejected` is ever legal after delayed validation, or if rejection must create a superseding event instead
- Whether a late-arriving event may reopen a `resolved` signal, or must always create a new `superseded` replacement signal
- Whether identical `dedup_key` values across tenants are always isolated by `tenant_id`
- Whether empty `source_event_ids` is forbidden at transport-validation time or only at business-validation time
- How to handle equal `occurred_at` timestamps when `event_id` generation source differs across emitters
- Whether confidence band changes without status changes should trigger notification downstream
