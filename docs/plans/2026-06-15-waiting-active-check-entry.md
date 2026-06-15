# Waiting Active Check Entry Guard

Status: planned

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
