#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required" >&2
  exit 1
fi

PR_INPUT="${1:-}"
REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
APPROVER_REGEX='^(codeahmed|CodeAhmed)$'

if [[ -z "$PR_INPUT" ]]; then
  echo "Usage: $0 <pr-number-or-url>" >&2
  exit 1
fi

pr_json="$(gh pr view "$PR_INPUT" --repo "$REPO" --json number,isDraft,mergeable,reviewDecision,reviews,url)"
pr_number="$(jq -r '.number' <<<"$pr_json")"
pr_url="$(jq -r '.url' <<<"$pr_json")"
is_draft="$(jq -r '.isDraft' <<<"$pr_json")"
mergeable="$(jq -r '.mergeable' <<<"$pr_json")"

if [[ "$is_draft" == "true" ]]; then
  echo "PR #$pr_number is still a draft: $pr_url" >&2
  exit 1
fi

if [[ "$mergeable" == "CONFLICTING" ]]; then
  echo "PR #$pr_number has merge conflicts: $pr_url" >&2
  exit 1
fi

approved_by_required_reviewer="$({
  jq -r '.reviews[] | select(.state == "APPROVED") | .author.login' <<<"$pr_json" || true
} | grep -E "$APPROVER_REGEX" | tail -n1 || true)"

if [[ -z "$approved_by_required_reviewer" ]]; then
  echo "PR #$pr_number does not yet have approval from codeahmed/CodeAhmed: $pr_url" >&2
  exit 1
fi

echo "Enabling auto-merge for PR #$pr_number after approval by $approved_by_required_reviewer"
gh pr merge "$pr_number" --repo "$REPO" --auto --merge
