# Waiting Appearance Generation Guard

Status: completed

## Problem

The waiting controller only records whether the view is currently active. If
one request starts, the view disappears, and the same controller appears again
before that request completes, the old callback sees the active flag restored
and can mutate state or navigate during the new appearance. The initial check
also starts in `viewDidLoad`, before the appearance lifecycle marks the view
active, and later appearances do not automatically retry.

## Scope

- Start the automatic waiting check only after each appearance becomes active.
- Assign each appearance a monotonically increasing generation.
- Require delayed work and backend responses to belong to the current active
  generation before requesting, updating UI, mutating match state, or navigating.
- Preserve the delay, manual refresh, one-request guard, session validation,
  request parameters, loading UI, and successful current-appearance segue.
- Add dependency-free, mutation-sensitive static contracts and maintenance
  guidance.

## Implementation

1. Replace the `viewDidLoad` check with an appearance generation increment and
   automatic `check()` call in `viewWillAppear`.
2. Capture the current generation when a check begins and require it at both
   asynchronous boundaries alongside the active-view guard.
3. Increment the generation when the view disappears so all earlier callbacks
   become permanently stale, even if the controller appears again.
4. Extend the baseline checker and project guidance for the generation rule.

## Verification

- Run checker compilation and every Make gate from the repository plus the
  canonical gate from an external directory with explicit timeouts.
- Reject isolated mutations that restore `viewDidLoad` scheduling, remove the
  appearance increment, remove either generation comparison, omit invalidation
  on disappearance, remove guidance, or leave this plan incomplete.
- Audit the exact diff, generated artifacts, credential patterns, project-file
  integrity, conflict markers, binaries, large files, and intended paths.

## Risks

- In-flight transport work is not cancelled; stale callbacks are made inert by
  their captured generation.
- `Int` generation overflow is not material for a controller appearance count.
- The stacked base pull request must remain available and merge first.

## Work Completed

- Moved automatic match checking from `viewDidLoad` into the active appearance
  lifecycle so initial and later appearances follow the same ordering.
- Added a monotonically increasing appearance generation, captured it when each
  check starts, and invalidated it when the view disappears.
- Required both delayed work and backend responses to belong to the current
  active generation before they can request, update state, or navigate.
- Made stale callback exits side-effect free so they cannot release a newer
  appearance's in-flight request guard.
- Added dependency-free contracts and project guidance for controller re-entry.

## Verification Completed

- All four Make gates passed from the repository and the canonical check passed
  from an external directory through the absolute Makefile path.
- The baseline checker compiled and passed; local Linux reported the existing
  `xcodebuild` limitation and completed the static iOS baseline.
- Eight isolated hostile mutations were rejected: restored `viewDidLoad`
  scheduling, missing appearance generation increment, missing delayed-work
  generation comparison, missing response generation comparison, missing
  disappearance invalidation, stale-callback request-state release, missing
  guidance, and stale plan status.
- `git diff --check`, exact intended-path, generated-artifact,
  credential-pattern, project-file integrity, conflict-marker, binary, and
  large-file audits passed.
- No live Digits, backend, location, or messaging service was contacted.
