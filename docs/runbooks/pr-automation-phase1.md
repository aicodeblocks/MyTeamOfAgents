# PR automation, phase 1

This repo uses a conservative workflow for pull requests:

1. A contributor opens a PR to `main`.
2. CI / required checks run.
3. Mansoor approves the PR.
4. Forge enables GitHub auto-merge for that PR.
5. GitHub merges the PR only after all required checks are green.
6. After `main` moves, Forge can safely merge `main` into still-open PR branches when it is conflict-free.

The automation is intentionally cautious:

- It does **not** guess through merge conflicts.
- It does **not** rebase contributor branches.
- It prefers merging `main` into open PR branches.
- It can report conflicts on the PR, then stop.

## What gets added

- `.github/workflows/pr-auto-merge-on-approval.yml`
  - When an approval review is submitted on a PR to `main`, Forge checks the configured approver login list and enables auto-merge only when the approval came from an allowed reviewer.
  - Auto-merge waits for required checks and branch protection rules.
- `.github/workflows/refresh-open-pr-branches.yml`
  - When `main` receives a push, Forge attempts to merge the updated `main` into open PR branches targeting `main`.
  - If the refresh is clean, it pushes a merge commit to the PR branch.
  - If there is a conflict, it comments on the PR and leaves the branch unchanged.
- `.github/workflows/forge-pr-review-signals.yml`
  - Watches for `pull_request.review_requested` and `pull_request_review.submitted` events.
  - Labels PRs when Forge is explicitly requested, when review feedback lands, and when changes are requested.
  - Uploads a normalized event summary artifact for each handled event.
  - Optionally forwards that normalized event payload to an external Forge webhook if repo secrets are configured.
- `infra/scripts/gh-enable-pr-automerge.sh`
  - Manual helper for Forge to enable auto-merge on a PR.
- `infra/scripts/refresh-pr-branch-from-main.sh`
  - Manual helper to refresh one PR branch by merging `origin/main` into it.
- `infra/scripts/forge-pr-review-event.sh`
  - Normalizes GitHub PR review events, manages labels/comments, and can forward a JSON payload to Forge.

## Required GitHub settings

These settings cannot be fully enforced from repo files alone.

### Repository settings

Enable:

- **Allow auto-merge**
- **Allow merge commits** (recommended for this phase-one workflow)

Recommended:

- Disable or discourage rebase merges if you want operations to stay consistent with the documented workflow.

### Branch protection for `main`

Recommended branch protection rules:

- Require a pull request before merging
- Require at least 1 approval
- Require review from Code Owners if you use CODEOWNERS later
- Require status checks to pass before merging
- Require branches to be up to date before merging, if you want the refresh workflow to matter operationally
- Restrict direct pushes to `main`

### Actions permissions

The workflows need enough permission to:

- read pull requests
- write pull requests
- write repository contents
- comment on pull requests

If your organization restricts the default `GITHUB_TOKEN`, allow these workflow permissions or provide an equivalent token.

## Reviewer identity configuration

The allowed approver logins come from a local env file.

Template:

- `.env.example`

Create a local config file at:

- `.env`

Expected variable:

```bash
PR_AUTOMATION_APPROVER_LOGINS=codeahmed,CodeAhmed
```

Notes:

- Use a comma-separated list of GitHub login names.
- Spaces are tolerated, but the exact login text still needs to match GitHub usernames.
- `.env` is gitignored so each environment can set its own reviewer list.
- If the local env file is missing, the helper script falls back to `codeahmed,CodeAhmed`.
- For backward compatibility, the helper also still reads `infra/env/pr-automation.env` if that older file already exists in someone's local checkout.

## Forge review awareness, phase one

When someone requests **Forge** as a reviewer on a PR, phase one now does three useful things entirely from inside the repo:

1. adds a `forge-review-requested` label so the PR becomes visibly queued for Forge
2. posts an acknowledgement comment explaining the phase-one path
3. writes a normalized JSON summary artifact, and forwards it to Forge if a webhook is configured

When a review is later submitted:

- `changes_requested` adds `forge-changes-requested`
- `commented` adds `forge-review-feedback`
- `approved` adds `forge-review-complete` and clears the review-request label

This is enough to make reviewer assignment and review feedback visible and machine-readable now, even before the full external runtime wiring is finished.

### Repo variable and secret expectations

Optional GitHub configuration for the relay workflow:

- **Repository variable** `FORGE_REVIEWER_LOGIN`
  - GitHub login that should be treated as Forge, for example `forge`
- **Repository secret** `FORGE_PR_WEBHOOK_URL`
  - HTTPS endpoint that accepts normalized Forge PR review event payloads
- **Repository secret** `FORGE_PR_WEBHOOK_BEARER_TOKEN`
  - Optional bearer token added as `Authorization: Bearer ...`

If the webhook secret is not set, the workflow still labels the PR, comments when useful, and uploads the normalized artifact in Actions.

### Normalized event payload shape

The relay helper writes a compact JSON document like this:

```json
{
  "event_name": "pull_request_review",
  "action": "submitted",
  "repo": "owner/repo",
  "pull_request": {
    "number": 123,
    "url": "https://github.com/owner/repo/pull/123",
    "title": "Add reviewer automation",
    "author": "contributor",
    "base_ref": "main",
    "head_ref": "feature/branch"
  },
  "review": {
    "state": "changes_requested",
    "reviewer_login": "forge",
    "body": "Please split this helper and add tests"
  }
}
```

That is the payload the external Forge ingress should expect in phase one.

## Normal operating flow

### Contributor

```bash
git checkout -b feature/my-change
# make changes
git push -u origin feature/my-change
gh pr create --base main --fill
```

### Mansoor

- Review the PR in GitHub
- Approve it from a GitHub login listed in `PR_AUTOMATION_APPROVER_LOGINS`

### Forge

Normally no manual step is needed after approval if the workflow fires successfully.

Manual fallback:

```bash
infra/scripts/gh-enable-pr-automerge.sh 123
```

That enables auto-merge for PR `#123` using merge commits.

Before using the helper in a new environment, copy the template and set the reviewer logins you want to trust:

```bash
cp .env.example .env
```

## Branch refresh flow after `main` moves

Automatic path:

- A push to `main` triggers the refresh workflow.
- Each same-repo open PR targeting `main` is checked.
- If `main` merges cleanly into the PR branch, Forge pushes the merge commit.
- If not, the workflow comments with a conflict notice.

Manual fallback:

```bash
infra/scripts/refresh-pr-branch-from-main.sh 123
```

## Conflict behavior

When the refresh workflow hits conflicts:

- it aborts the merge
- it leaves the PR branch unchanged
- it comments on the PR so a human can resolve it

This is deliberate. The workflow does not attempt automatic conflict resolution.

## Suggested Forge usage

For a just-approved PR:

```bash
infra/scripts/gh-enable-pr-automerge.sh <pr-number>
```

For a stale branch:

```bash
infra/scripts/refresh-pr-branch-from-main.sh <pr-number>
```

## Notes and limitations

- Auto-merge only completes if GitHub branch protection rules and required checks permit it.
- Refresh automation only updates same-repo branches. Fork PR branches are skipped for safety.
- The refresh job uses merge commits, not rebases.
- This is intentionally a phase-one workflow: simple, visible, and easy to debug.

## What still needs external wiring

This repo now provides the event source, normalized payload, labels, comments, and an optional webhook POST. The remaining gap is on the Forge runtime side.

Recommended next step:

1. Expose a small Forge ingress endpoint or plugin handler for GitHub PR review events.
2. Store `FORGE_PR_WEBHOOK_URL` and optional `FORGE_PR_WEBHOOK_BEARER_TOKEN` in repo secrets.
3. Verify auth on the Forge side and map the normalized payload onto a repo/PR-specific review task.
4. Teach Forge how to fetch the PR diff, inspect changed files, and reply through GitHub when review feedback is needed.
5. Optionally expand coverage to `pull_request_review_comment` and `issue_comment` if threaded inline feedback should also wake Forge.

Why this split is practical:

- reviewer assignment and feedback are visible immediately in GitHub now
- Actions artifacts preserve a compact payload for debugging
- forwarding can be enabled later without changing the repo contract again
