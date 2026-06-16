# Pulse Request Ownership

Status: planned

## Problem

Pulse loads can be started by appearance, pull-to-refresh, and the repeating
timer. Those requests can overlap, allowing an older response to replace a
newer pulse snapshot after the newer request has already completed. Requests
also continue after the view disappears.

## Approach

- Retain the current Alamofire pulse request.
- Cancel and clear obsolete work before starting a replacement and when the
  view disappears.
- Accept a response only when it belongs to the exact retained request, then
  clear ownership before applying the existing row-integrity update.
- Preserve normalized user identity, POST parameters, refresh behavior, and
  successful row rendering.

## Files

- `WhineLocation/PulseViewController.swift`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-pulse-request-ownership.md`

## Verification Planned

- Run the focused baseline checker and all four Make gates from the repository
  root and an external directory.
- Run isolated hostile mutations for request retention, replacement
  cancellation, disappearance cancellation, response identity, ownership
  clearing, and completed plan evidence.
- Run `git diff --check` plus explicit artifact and changed-line secret audits.
- Record the Linux Xcode limitation without claiming simulator execution.
