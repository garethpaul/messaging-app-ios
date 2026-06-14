# Waiting Session And Response Guard

Status: planned

## Problem

The waiting-for-match refresh dereferences the Digits session twice after its
delay and force-unwraps response JSON. A signed-out or expired session can crash
before the request, malformed or missing JSON can crash after it, and the
loading state is currently cleared immediately after starting the request
instead of when the request completes.

## Scope

- Resolve one Digits session and normalized user ID before posting the waiting
  request.
- Return without a request when the session or normalized identity is absent.
- Guard transport failure and missing response JSON before parsing match data.
- Restore the waiting UI when a guarded early return occurs and when the
  response callback completes.
- Preserve the two-second delay, request endpoint, phone-number parameter,
  match comparison, and successful navigation.
- Extend the maintained static baseline and project guidance.

## Implementation

1. Add one helper that restores the spinner and waiting-image state.
2. Guard a single Digits session and normalized user ID inside the delayed
   closure, reuse the session phone number, and restore UI before returning.
3. Move ordinary loading-state completion into the response callback and guard
   both the error and optional JSON value before constructing `JSON`.
4. Add method-scoped, ordering-sensitive contracts in
   `scripts/check-baseline.py` plus README, security, vision, and changelog
   guidance.

## Validation

- Run checker compilation and all four Make gates from the checkout plus the
  canonical gate from an external directory.
- Verify isolated mutations that restore direct session dereferences, bypass
  identity normalization, restore `JSON(json!)`, move UI completion before the
  response callback, remove maintenance guidance, or leave this plan
  incomplete are rejected.
- Run `git diff --check` and exact intended-path, generated-artifact,
  secret-pattern, conflict-marker, binary, and large-file audits.
- Record that Xcode and simulator execution are unavailable on this Linux host;
  rely on the existing macOS hosted project-parsing gate.

## Risks

- The legacy callback remains asynchronous; UI restoration must stay on its
  existing main-queue callback path.
- The stacked base PR must remain available and merge before this change.

## Work Completed

Pending implementation.

## Verification Completed

Pending validation.
