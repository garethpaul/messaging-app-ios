# Waiting Active Check Entry Guard

Status: completed

## Problem

`WaitingViewController.check()` can start while the view is inactive. It then
sets `isChecking`, mutates loading UI, and schedules delayed work that exits as
stale without releasing that newly-created guard. The next appearance can
therefore skip its automatic check indefinitely.

## Scope

- Require the current waiting view appearance to be active before changing
  request or loading state.
- Preserve the appearance-generation, one-request, session, request, response,
  and successful-navigation behavior.
- Add mutation-sensitive static contracts and maintained guidance.

## Verification

- Prove inactive entry is rejected before `isChecking` and UI mutations.
- Run every Make gate from the repository and the canonical check from an
  external directory with explicit timeouts.
- Reject source-order, regression-contract, guidance, and plan-status
  mutations.
- Audit the exact diff, generated artifacts, project integrity, binaries,
  modes, and credential-shaped additions.

## Non-Goals

- Do not cancel transport work or change the backend request contract.
- Do not merge or close stacked pull requests without owner authorization.

## Work Completed

- Added the active-view predicate to the first `check()` guard before
  `isChecking`, appearance-generation capture, and loading UI mutation.
- Preserved the existing concurrent, matched, session, generation, response,
  and navigation boundaries.
- Extended dependency-free baseline contracts and maintained guidance for the
  active-entry ordering.

## Verification Completed

- All four Make gates passed from the repository and the canonical check passed
  from an external directory.
- The baseline checker compiled and passed; Linux reported the existing
  `xcodebuild` limitation without claiming executable iOS behavior.
- Five isolated hostile mutations were rejected for inactive-entry removal,
  guard reordering, source-contract weakening, missing guidance, and stale plan
  status.
- Exact diff, generated-artifact, project-integrity, binary, file-mode,
  conflict-marker, and credential-shaped addition audits passed.
- No live Digits, backend, location, or messaging service was contacted.
