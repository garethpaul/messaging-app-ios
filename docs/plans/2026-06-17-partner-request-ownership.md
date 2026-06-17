---
title: "fix: Bind partner navigation to request ownership"
type: fix
status: completed
date: 2026-06-17
execution: code
---

# Bind Partner Navigation to Request Ownership

## Summary

Make partner lookup own its Alamofire request so repeated taps supersede older
work and only the current visible appearance can navigate to the waiting view.

## Problem Frame

`NewPartnerViewController.findPartnerBtn` currently starts an unretained request
for every tap and performs its segue from any successful callback. Overlapping
responses can navigate more than once, and a response can navigate after the
controller has disappeared. The existing waiting and pulse request guards do
not cover this separate partner-creation request.

## Requirements

- R1. Retain the active partner request and reject callbacks from any older or
  cancelled request by exact identity.
- R2. Cancel and replace an existing request before starting a new valid lookup.
- R3. Track view activity and a monotonic appearance generation so a callback
  from an earlier appearance cannot navigate after leave-and-return.
- R4. Cancel and clear the active request when disappearance begins.
- R5. Perform the waiting segue only after the current owned request succeeds
  while the same appearance remains active.
- R6. Clear owned request state on both success and failure without navigating
  on failure.
- R7. Preserve partner-number normalization, Digits session/user validation,
  endpoint, payload, keyboard behavior, and segue identifier.
- R8. Add mutation-sensitive static contracts and completed verification
  evidence without claiming Linux-native UIKit or Alamofire execution.

## Key Technical Decisions

- KTD1. Use exact `Request` identity as the completion ownership boundary,
  matching the maintained pulse and waiting request patterns.
- KTD2. Capture the appearance generation at request creation and require both
  generation equality and active visibility before navigation.
- KTD3. Cancel a superseded request rather than rejecting repeat taps so the
  latest normalized input is authoritative.

## Scope Boundaries

- Do not change backend endpoints, payload keys, partner-number formatting,
  authentication, waiting-screen behavior, alerts, retries, or visual design.
- Do not merge or close any stacked pull request without explicit owner
  authorization.

## Implementation Units

### U1. Own partner request lifecycle

- **Files:** `WhineLocation/NewPartnerViewController.swift`
- Retain requests, track visibility/generation, cancel on replacement and
  disappearance, and clear only the matching request.

### U2. Protect navigation ordering

- **Files:** `WhineLocation/NewPartnerViewController.swift`,
  `scripts/check-baseline.py`
- Require exact identity, current appearance, and success before the waiting
  segue; reject isolated weakening of each boundary.

### U3. Synchronize project evidence

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan
- Record the partner-request ownership contract and actual bounded validation.

## Verification Plan

- Run all four canonical Make aliases from the repository root and the absolute
  Makefile gate from `/tmp`.
- Compile the Python checker and reject isolated hostile mutations to request
  retention, replacement cancellation, disappearance cancellation, identity,
  activity, generation, success-only navigation, guidance, and plan status.
- Audit the exact intended diff, generated artifacts, credentials, conflict
  markers, binaries, large files, modes, and protected paths before commit.

## Work Completed

- Retained the active partner request and cancelled superseded requests before
  starting the latest valid lookup.
- Added visible-appearance state and a monotonic generation, invalidating and
  cancelling ownership when disappearance begins.
- Required exact request identity, active visibility, matching generation, and
  success on the main queue before navigating to the waiting flow.
- Extended the maintained checker and project guidance with ordering-sensitive
  partner request ownership contracts.

## Verification Completed

- All four Make gates passed from a no-hardlink isolated clone, and the absolute
  Makefile gate passed from an external directory.
- All four Make gates and the external-directory gate also passed against the
  finalized worktree.
- Nine isolated hostile mutations were rejected for request retention,
  replacement cancellation, disappearance cancellation, exact identity,
  activity, generation, success-only navigation, guidance, and plan status.
- Python checker syntax and `git diff --check` passed before final worktree
  validation.
- Xcode is unavailable on Linux; no native UIKit, Alamofire, Digits, simulator,
  device, or backend execution is claimed.
