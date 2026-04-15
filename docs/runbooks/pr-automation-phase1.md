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
- `infra/scripts/gh-enable-pr-automerge.sh`
  - Manual helper for Forge to enable auto-merge on a PR.
- `infra/scripts/refresh-pr-branch-from-main.sh`
  - Manual helper to refresh one PR branch by merging `origin/main` into it.

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

## Recommended next step for review comment awareness

Best path: use an event-driven GitHub webhook (or a lightweight GitHub App webhook) that sends `pull_request_review` and `pull_request_review_comment` events into Forge.

Why this is the best fit:

- immediate notification when a reviewer leaves feedback
- no polling lag or GitHub API churn
- full event payload, including PR number, reviewer, comment body, and thread context
- easier to extend later if you also want `issue_comment` events for general PR discussion

Fallback options are weaker here:

- GitHub Actions can relay events, but they still need a destination and add workflow complexity
- scheduled `gh` polling is simplest to start, but it is slower, noisier, and more fragile around deduping

Practical implementation target:

1. Expose a small Forge ingress endpoint or plugin handler for GitHub webhook deliveries.
2. Verify the webhook signature with a shared secret.
3. Normalize `pull_request_review` and `pull_request_review_comment` into one internal "pr review feedback received" event.
4. Let Forge attach that event to the right repo/PR task and notify the right agent or user only when needed.
