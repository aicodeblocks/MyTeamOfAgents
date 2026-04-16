#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 1
fi

PR_INPUT="${1:-}"
BASE_BRANCH="${2:-main}"
REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"

if [[ -z "$PR_INPUT" ]]; then
  echo "Usage: $0 <pr-number-or-url> [base-branch]" >&2
  exit 1
fi

pr_json="$(gh pr view "$PR_INPUT" --repo "$REPO" --json number,url,headRefName,headRepositoryOwner,headRepository,baseRefName,isCrossRepository,mergeable)"
pr_number="$(jq -r '.number' <<<"$pr_json")"
pr_url="$(jq -r '.url' <<<"$pr_json")"
head_ref="$(jq -r '.headRefName' <<<"$pr_json")"
base_ref="$(jq -r '.baseRefName' <<<"$pr_json")"
is_cross_repo="$(jq -r '.isCrossRepository' <<<"$pr_json")"
head_repo_full="$(jq -r '.headRepository.owner.login + "/" + .headRepository.name' <<<"$pr_json")"

if [[ "$base_ref" != "$BASE_BRANCH" ]]; then
  echo "PR #$pr_number targets $base_ref, not $BASE_BRANCH: $pr_url" >&2
  exit 1
fi

if [[ "$is_cross_repo" == "true" ]]; then
  echo "Skipping cross-repo PR #$pr_number for safety: $pr_url" >&2
  exit 1
fi

workdir="$(mktemp -d)"
cleanup() {
  rm -rf "$workdir"
}
trap cleanup EXIT

pushd "$workdir" >/dev/null

git init -q

origin_url="https://github.com/$REPO.git"
if [[ -n "${GH_TOKEN:-}" ]]; then
  origin_url="https://x-access-token:${GH_TOKEN}@github.com/$REPO.git"
fi

git remote add origin "$origin_url"
git fetch --no-tags --depth=50 origin "$BASE_BRANCH" "$head_ref"

git checkout -q -b "$head_ref" "origin/$head_ref"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

if git merge --no-ff --no-edit "origin/$BASE_BRANCH"; then
  git push origin "HEAD:$head_ref"
  echo "Refreshed PR #$pr_number by merging $BASE_BRANCH into $head_ref"
else
  git merge --abort || true
  echo "Conflict while refreshing PR #$pr_number: $pr_url" >&2
  exit 2
fi

popd >/dev/null
