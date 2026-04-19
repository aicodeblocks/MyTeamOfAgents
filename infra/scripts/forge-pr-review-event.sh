#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required" >&2
  exit 1
fi

EVENT_NAME="${1:-${GITHUB_EVENT_NAME:-}}"
EVENT_PATH="${2:-${GITHUB_EVENT_PATH:-}}"
TARGET_LOGIN_RAW="${FORGE_REVIEWER_LOGIN:-forge}"
TARGET_LOGIN="${TARGET_LOGIN_RAW#@}"
TARGET_LOGIN_LC="$(tr '[:upper:]' '[:lower:]' <<<"$TARGET_LOGIN")"
REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"

if [[ -z "$EVENT_NAME" || -z "$EVENT_PATH" ]]; then
  echo "Usage: $0 <event-name> <event-json-path>" >&2
  exit 1
fi

if [[ ! -f "$EVENT_PATH" ]]; then
  echo "Event payload not found: $EVENT_PATH" >&2
  exit 1
fi

action="$(jq -r '.action // empty' "$EVENT_PATH")"
pr_number="$(jq -r '.pull_request.number // empty' "$EVENT_PATH")"
pr_url="$(jq -r '.pull_request.html_url // empty' "$EVENT_PATH")"
pr_title="$(jq -r '.pull_request.title // empty' "$EVENT_PATH")"
pr_author="$(jq -r '.pull_request.user.login // empty' "$EVENT_PATH")"
base_ref="$(jq -r '.pull_request.base.ref // empty' "$EVENT_PATH")"
head_ref="$(jq -r '.pull_request.head.ref // empty' "$EVENT_PATH")"

if [[ -z "$pr_number" ]]; then
  echo "No pull request found in event payload" >&2
  exit 1
fi

summary_json="$(jq -n \
  --arg event_name "$EVENT_NAME" \
  --arg action "$action" \
  --arg repo "$REPO" \
  --argjson pr_number "$pr_number" \
  --arg pr_url "$pr_url" \
  --arg pr_title "$pr_title" \
  --arg pr_author "$pr_author" \
  --arg base_ref "$base_ref" \
  --arg head_ref "$head_ref" \
  '{event_name:$event_name,action:$action,repo:$repo,pull_request:{number:$pr_number,url:$pr_url,title:$pr_title,author:$pr_author,base_ref:$base_ref,head_ref:$head_ref}}')"

comment_body=''
label_add=''
label_remove=''
needs_forward='false'

ensure_label() {
  local label_name="$1"
  local color="$2"
  local description="$3"

  gh api "repos/$REPO/labels/$label_name" >/dev/null 2>&1 && return 0
  gh api "repos/$REPO/labels" \
    --method POST \
    -f name="$label_name" \
    -f color="$color" \
    -f description="$description" >/dev/null
}

case "$EVENT_NAME:$action" in
  pull_request:review_requested)
    requested_reviewers_lc="$({ jq -r '.requested_reviewer.login?, .pull_request.requested_reviewers[]?.login?' "$EVENT_PATH" 2>/dev/null || true; } | tr '[:upper:]' '[:lower:]')"

    if grep -Fxq "$TARGET_LOGIN_LC" <<<"$requested_reviewers_lc"; then
      label_add='forge-review-requested'
      label_remove='forge-review-complete'
      needs_forward='true'
      comment_body=$(cat <<EOF
Forge review request acknowledged for @$TARGET_LOGIN.

Phase one behavior in this repo:
- GitHub marks this PR for Forge with labels.
- The workflow captures a normalized event summary artifact.
- If the optional \
\`FORGE_PR_WEBHOOK_URL\` secret is configured, the event is also forwarded to Forge's webhook ingress.

PR: #$pr_number
Title: $pr_title
Base: $base_ref
Head: $head_ref
EOF
)
    else
      echo "Requested reviewer does not match @$TARGET_LOGIN, nothing to do."
      exit 0
    fi
    ;;
  pull_request_review:submitted)
    review_state="$(jq -r '.review.state // empty' "$EVENT_PATH" | tr '[:upper:]' '[:lower:]')"
    reviewer_login="$(jq -r '.review.user.login // empty' "$EVENT_PATH")"
    review_body="$(jq -r '.review.body // empty' "$EVENT_PATH")"

    summary_json="$(jq \
      --arg review_state "$review_state" \
      --arg reviewer_login "$reviewer_login" \
      --arg review_body "$review_body" \
      '. + {review:{state:$review_state,reviewer_login:$reviewer_login,body:$review_body}}' <<<"$summary_json")"

    case "$review_state" in
      changes_requested)
        label_add='forge-changes-requested'
        label_remove='forge-review-requested'
        needs_forward='true'
        comment_body=$(cat <<EOF
Forge captured a GitHub review with **changes requested** by @$reviewer_login.

This is the phase-one signal that Forge should inspect the PR feedback and respond through the external webhook or operator workflow.
EOF
)
        ;;
      approved)
        label_add='forge-review-complete'
        label_remove='forge-review-requested,forge-changes-requested'
        ;;
      commented)
        label_add='forge-review-feedback'
        needs_forward='true'
        ;;
      *)
        echo "Review state $review_state does not require action."
        ;;
    esac
    ;;
  *)
    echo "Unsupported event: $EVENT_NAME:$action"
    exit 0
    ;;
esac

if [[ -n "$label_add" ]]; then
  IFS=',' read -r -a labels_to_add <<<"$label_add"
  for label in "${labels_to_add[@]}"; do
    [[ -z "$label" ]] && continue
    case "$label" in
      forge-review-requested) ensure_label "$label" '1d76db' 'Forge was requested to review this PR' ;;
      forge-review-complete) ensure_label "$label" '0e8a16' 'Forge review activity is complete for now' ;;
      forge-changes-requested) ensure_label "$label" 'd93f0b' 'GitHub review feedback requested changes' ;;
      forge-review-feedback) ensure_label "$label" '5319e7' 'GitHub review feedback was captured for Forge' ;;
      *) ensure_label "$label" 'ededed' 'Label managed by Forge PR review automation' ;;
    esac
    gh pr edit "$pr_number" --repo "$REPO" --add-label "$label"
  done
fi

if [[ -n "$label_remove" ]]; then
  IFS=',' read -r -a labels_to_remove <<<"$label_remove"
  for label in "${labels_to_remove[@]}"; do
    [[ -z "$label" ]] && continue
    gh pr edit "$pr_number" --repo "$REPO" --remove-label "$label" || true
  done
fi

if [[ -n "$comment_body" ]]; then
  gh pr comment "$pr_number" --repo "$REPO" --body "$comment_body"
fi

printf '%s\n' "$summary_json" > forge-pr-event-summary.json

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  echo "summary_path=forge-pr-event-summary.json" >> "$GITHUB_OUTPUT"
  echo "needs_forward=$needs_forward" >> "$GITHUB_OUTPUT"
fi

if [[ -n "${FORGE_PR_WEBHOOK_URL:-}" && "$needs_forward" == "true" ]]; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl is required to forward Forge PR events" >&2
    exit 1
  fi

  auth_header=()
  if [[ -n "${FORGE_PR_WEBHOOK_BEARER_TOKEN:-}" ]]; then
    auth_header=(-H "Authorization: Bearer ${FORGE_PR_WEBHOOK_BEARER_TOKEN}")
  fi

  curl --fail --show-error --silent \
    -X POST \
    -H 'Content-Type: application/json' \
    "${auth_header[@]}" \
    --data @forge-pr-event-summary.json \
    "$FORGE_PR_WEBHOOK_URL"
fi

echo "Processed $EVENT_NAME:$action for PR #$pr_number"
