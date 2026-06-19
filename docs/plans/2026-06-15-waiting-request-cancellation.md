# Waiting Request Cancellation

Status: completed

## Problem

The waiting controller makes stale callbacks inert with activity and appearance
generation guards, but it does not cancel an Alamofire request when the view
disappears. The obsolete request continues consuming transport and callback
work. A canceled callback can also arrive after a new appearance starts, so any
request reference cleanup must be bound to the exact request instance.

## Approach

- Retain the current Alamofire `Request` only after the delayed and Digits
  session guards allow network work to start.
- Cancel and clear that request in `viewWillDisappear` before releasing the
  existing waiting-check UI state.
- Bind response handling to the exact retained request before clearing request
  state or evaluating activity, generation, error, and match data.
- Preserve the delayed start, one-check guard, normalized identity, backend
  parameters, appearance generation, stable stale-response behavior, and
  successful navigation.

## Files

- `WhineLocation/WaitingViewController.swift`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-waiting-request-cancellation.md`

## Verification

- Add mutation-sensitive static contracts for request retention, cancellation
  ordering, identity-bound callback cleanup, guidance, and completed evidence.
- Run all repository and external-directory Make gates available on Linux.
- Reject isolated cancellation, clearing, identity, ordering, guidance, and
  plan-status mutations.
- Audit the exact diff, project-file drift, generated artifacts, modes,
  credentials, conflict markers, and whitespace.

## Scope Boundaries

- Do not change backend URLs, request parameters, the two-second delay, Digits
  session rules, match parsing, segue behavior, dependencies, or the Xcode
  project.
- Linux cannot compile or execute this legacy iOS app; record that limitation
  and require hosted baseline evidence for the exact pushed head.
- Do not merge or close stacked pull requests without explicit authorization.

## Success Criteria

- Disappearance cancels and clears the current transport request before waiting
  UI state is released.
- A callback from a canceled prior request cannot clear or complete a newer
  request after controller re-entry.
- Existing generation and activity checks remain independently enforced.

## Work Completed

- Retained the exact Alamofire waiting request after delayed and session guards
  allow transport to start.
- Cancelled and cleared retained transport during disappearance before releasing
  the existing waiting-check UI state.
- Identity-bound response cleanup before generation checks and current request
  state changes so callbacks from canceled requests cannot affect re-entry.
- Added portable source, ordering, guidance, and completed-plan contracts.

## Verification Completed

- All four Make gates passed from the repository root and an external directory.
- Seven isolated hostile mutations were rejected across request retention,
  cancellation, disappearance ordering, callback identity, guidance, and plan
  completion evidence.
- Exact seven-path diff, project-file drift, generated-artifact, mode,
  credential-pattern, conflict-marker, and whitespace audits passed.
- Xcode is unavailable on Linux; no simulator, device, Digits session, backend
  request, cancellation callback, or UI lifecycle behavior was executed locally.
