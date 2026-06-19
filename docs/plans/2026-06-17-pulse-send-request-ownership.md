---
title: "fix: Bind pulse send UI to request completion"
type: fix
status: completed
date: 2026-06-17
execution: code
---

# Bind Pulse Send UI to Request Completion

## Summary

Make pulse-message submission own and observe its Alamofire request. Keep the
draft and retry state intact when delivery fails, clear and refresh only after
the exact current request succeeds, and cancel obsolete sends when the view
disappears.

## Problem Frame

`PulseViewController.sendMsg` currently fires a request without retaining or
observing it, clears the text field immediately, and refreshes the pulse list
after a fixed one-second delay. Network or server failures therefore look like
successful sends, user text is lost, and a delayed refresh can run after the
view has disappeared. Existing list-request ownership does not cover this
separate write request.

## Requirements

- R1. Retain the active pulse-send request and reject callbacks from any older
  or cancelled request by exact identity.
- R2. Keep repeat sends disabled until the current request completes or is
  cancelled; restore the button state on every owned completion path.
- R3. Clear the submitted draft and refresh pulse data only when the owned send
  callback reports success.
- R4. Preserve the draft and avoid a list refresh when the owned send fails.
- R5. Cancel and clear an active send before releasing send UI state when the
  view disappears.
- R6. Preserve the existing guarded Digits session, normalized user ID,
  endpoint, and request payload.
- R7. Add mutation-sensitive portable contracts and completed verification
  evidence without claiming Linux-native UIKit or Alamofire execution.

## Key Technical Decisions

- KTD1. Replace the time-based cooldown with request completion. The network
  callback is the authoritative delivery boundary; an arbitrary delay cannot
  distinguish success from failure.
- KTD2. Track pulse-list and pulse-send requests separately. They have distinct
  cancellation and publication semantics and must not overwrite each other's
  ownership.
- KTD3. Centralize send completion in a helper that revalidates exact request
  identity on the main queue before changing the draft, button, throttle, or
  list refresh.

## Scope Boundaries

- Do not change backend endpoints, payload keys, Digits authentication, or the
  pulse-list response parser.
- Do not add retries, alerts, optimistic rows, or new visual design.
- Do not merge or close any stacked pull request without explicit owner
  authorization.

## Implementation Units

### U1. Own pulse-send request lifecycle

- **Goal:** Retain the active request, observe completion, and cancel it during
  disappearance.
- **Files:** `WhineLocation/PulseViewController.swift`
- **Requirements:** R1, R2, R5, R6
- **Verification:** Ordering contracts prove cancellation precedes clearing and
  exact identity precedes every completion-side UI mutation.

### U2. Publish success and failure states correctly

- **Goal:** Clear and refresh only on success while preserving retryable input
  on failure.
- **Files:** `WhineLocation/PulseViewController.swift`,
  `scripts/check-baseline.py`
- **Requirements:** R2, R3, R4, R7
- **Verification:** Static scenarios reject immediate draft clearing, delayed
  unconditional refresh, missing identity, and failure-path draft loss.

### U3. Synchronize project evidence

- **Goal:** Record the request-owned send boundary and actual validation.
- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
  `docs/plans/2026-06-17-pulse-send-request-ownership.md`
- **Requirements:** R3, R4, R5, R7

## Risks and Dependencies

- The archived Alamofire/Digits stack cannot be compiled or exercised on this
  Linux host; hosted project parsing and mutation-sensitive source contracts
  remain the portable evidence.
- A successful callback proves only the client's request completion, not
  downstream push delivery or durable backend processing.
- Cancelling on disappearance may race a callback, so exact request identity is
  required even after cancellation.

## Acceptance Examples

- AE1. Tapping send with a valid session retains one request and disables
  further sends until that request completes.
- AE2. A successful owned callback clears the submitted draft, restores the
  button/throttle, and starts one pulse-list refresh.
- AE3. A failed owned callback keeps the draft, restores the button/throttle,
  and does not refresh the pulse list.
- AE4. Disappearance cancels and clears the send request before restoring send
  UI state; a later callback performs no mutation.
- AE5. A callback from an older request cannot clear a newer draft, restore a
  newer request's throttle, or trigger a refresh.

## Verification Plan

- Run the canonical root and external-directory Make gates.
- Compile the Python checker and parse maintained project metadata.
- Reject isolated hostile mutations for retention, identity, success-only
  clearing, failure preservation, disappearance cancellation, guidance, and
  completed plan evidence.
- Audit the exact diff, generated artifacts, credentials, conflict markers,
  binaries, large files, and protected project/workflow paths.

## Work Completed

- Added a distinct retained `pulseSendRequest` and bound completion to exact
  request identity on the main queue.
- Replaced the fixed delayed refresh with observed response completion, clearing
  the draft and refreshing the pulse list only after success.
- Preserved the draft on failure while restoring the send throttle, button, and
  text-field state on every owned completion.
- Cancelled and cleared obsolete send requests before releasing send UI state
  when the controller disappears.
- Added ordering-sensitive static contracts and synchronized maintenance
  guidance.

## Verification Completed

- All four Make gates passed from the repository root and through the absolute
  Makefile path from an external directory.
- The Python checker compiled, all maintained plist, XML, JSON, image, project,
  workflow, source, and documentation contracts passed, and `git diff --check`
  passed.
- Eight isolated hostile mutations were rejected for retention, exact identity,
  success-only publication, observed response completion, cancellation, UI
  locking, guidance, and completed plan status.
- The exact intended diff passed generated-artifact, credential-pattern,
  conflict-marker, binary, large-file, mode, and protected-path audits.
- Xcode is unavailable on Linux; static iOS baseline only, with no claim of
  native UIKit, Alamofire, Digits, simulator, device, or backend execution.
