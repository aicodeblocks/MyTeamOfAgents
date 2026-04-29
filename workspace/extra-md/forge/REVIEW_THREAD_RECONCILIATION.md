# Review thread reconciliation requirement

This workspace does not currently contain the active Forge reviewer-awareness implementation, so this file captures the added requirement and the safest supported GitHub behavior for the main implementation/PR to absorb.

## Requirement to add

When Forge determines that review feedback has been addressed by later code changes, it should also reconcile the related GitHub review threads where possible.

## Safest supported GitHub mechanism

GitHub supports resolving pull request review **threads** (not individual review comments) via GraphQL.

Use GraphQL review-thread operations, not REST review-comment endpoints, for completion state:

- query unresolved `PullRequestReviewThread` nodes for the PR
- compare each unresolved thread against the updated diff / addressed-comment mapping already produced by reviewer-awareness logic
- resolve only threads that are confidently matched as addressed
- leave unmatched or ambiguous threads unresolved and report them clearly

Relevant GraphQL primitives to use in the implementation:

- `PullRequest.reviewThreads`
- `PullRequestReviewThread.isResolved`
- `PullRequestReviewThread.isOutdated`
- `PullRequestReviewThread.path`
- `PullRequestReviewThread.line` / original-line metadata when available
- `resolveReviewThread`
- `unresolveReviewThread` only if Forge explicitly supports rollback/reconciliation corrections

## Important limitations

1. GitHub does **not** provide a safe REST equivalent for marking a review thread complete. REST review-comment APIs can list/update comments, but thread resolution state is a GraphQL concern.
2. Resolution applies to the **thread**, not to each individual comment.
3. Not every comment can be auto-resolved safely. General discussion, ambiguous feedback, or comments whose referenced code moved substantially should stay unresolved unless Forge has a high-confidence match.
4. Review threads can become outdated after new commits. Outdated does not automatically mean addressed, so Forge should not resolve purely because a thread is outdated.
5. Resolution may fail based on token scope or actor permissions. Forge should surface this as a non-fatal warning, not treat it as analysis failure.

## Recommended implementation behavior

### Default behavior

After Forge posts or updates its “addressed reviewer comments” analysis:

1. fetch unresolved review threads for the PR
2. map Forge’s addressed findings to candidate GitHub thread IDs
3. split into:
   - `safe_to_resolve`
   - `ambiguous_do_not_resolve`
   - `cannot_resolve_due_to_permissions_or_api_errors`
4. call `resolveReviewThread` only for `safe_to_resolve`
5. include a summary in Forge output, for example:
   - resolved automatically: 3
   - addressed but left unresolved as ambiguous: 2
   - failed to resolve due to permissions/API: 1

### Matching rules

Prefer a conservative match strategy, in roughly this order:

1. explicit stored thread node ID from prior scan
2. exact thread/comment node ID already linked to the addressed finding
3. same PR + same file path + same line/original line + same reviewer comment id
4. same PR + same file path + high-confidence semantic/body match, only if the implementation already uses a robust confidence threshold

If Forge cannot match a finding to a single thread confidently, it should report the thread for manual follow-up instead of resolving it.

## Suggested wording for user-facing output

- "Forge resolved N GitHub review threads that were confidently matched to addressed feedback."
- "M additional addressed comments were detected, but Forge left their threads unresolved because the GitHub thread match was ambiguous or unavailable."
- "K thread resolutions failed due to GitHub permissions or API limits; manual resolution may still be needed in the PR UI."

## Fallback if implementation time is tight

If the active PR cannot safely implement GraphQL thread resolution right now, at minimum it should:

1. document that GitHub thread completion is GraphQL-only
2. emit a per-thread/manual-action section listing the threads Forge believes are addressed
3. explain that maintainers can resolve those threads in the PR UI

That is the safest fallback if automatic reconciliation cannot be shipped in the same change.
