# Waiting Concurrent Check Guard

Status: completed

## Problem

Each waiting-screen refresh schedules a delayed backend request without tracking
whether an earlier check is still pending. Repeated taps can therefore create
overlapping requests, and multiple successful responses can each perform the
match segue.

## Scope

- Allow only one delayed waiting check or backend request at a time.
- Keep future checks disabled after a successful match begins navigation.
- Release the in-flight guard after missing identity, transport failure,
  malformed responses, and ordinary unmatched responses.
- Preserve the existing delay, request parameters, loading-state behavior, and
  successful match destination.
- Extend the dependency-free checker and project guidance with exact contracts.

## Implementation

1. Add explicit in-flight and matched state to `WaitingViewController`.
2. Guard `check()` before mutating the loading UI or scheduling delayed work.
3. Clear only the in-flight state in the common completion helper and mark the
   terminal matched state before performing the segue.
4. Add method-scoped, ordering-sensitive static checks plus maintenance notes.

## Validation

- Run checker compilation and all four Make gates from the checkout, then run
  the canonical gate through the absolute Makefile path externally.
- Verify isolated mutations that remove either state guard, move matched-state
  assignment after navigation, fail to release the in-flight state, remove
  guidance, or leave this plan incomplete are rejected.
- Run `git diff --check` and exact intended-path, generated-artifact,
  secret-pattern, conflict-marker, binary, and large-file audits.
- Record that Xcode and simulator execution are unavailable on this Linux host.

## Risks

- Guard state is confined to the main-thread UI and Alamofire callback path;
  future callback-queue changes must preserve serialized access.
- The stacked base pull request must remain available and merge first.

## Work Completed

- Added in-flight and terminal-match state to the waiting controller.
- Rejected refreshes before loading UI mutation when a check is already pending
  or a successful match has begun navigation.
- Released in-flight state through the existing completion helper and marked a
  successful match before performing the segue.
- Added ordering-sensitive static contracts and maintenance guidance.

## Verification Completed

- All four Make gates passed from the checkout, and the canonical check passed
  from an external directory through the absolute Makefile path.
- Six isolated hostile mutations were rejected: missing in-flight guard,
  missing terminal-match guard, matched state after navigation, missing
  in-flight release, missing maintenance guidance, and stale plan status.
- Checker compilation and `git diff --check` passed. Exact intended-path,
  generated-artifact, secret-pattern, conflict-marker, binary, and large-file
  audits found no issues.
- `xcodebuild` is unavailable on this Linux host, so no simulator, device,
  Digits session, backend response, or UI lifecycle execution is claimed.
