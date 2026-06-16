# Pulse Publication Ownership

Status: completed

## Priority

P1 stale-state prevention. A pulse response can pass the transport ownership
guard, queue its table update, and then publish after a replacement request has
started or the controller has disappeared.

## Problem

`PulseViewController.getData()` currently clears `pulseRequest` before
dispatching successful row publication to the main queue. The queued block does
not revalidate request ownership. A replacement refresh or disappearance in
that interval can therefore invalidate the response while still allowing its
older snapshot to replace current table state and invoke read comparison.

## Approach

- Keep successful response ownership until the main-queue publication block.
- Revalidate that the queued response still belongs to the exact retained
  Alamofire request immediately before mutating table state.
- Clear request ownership only after that publication guard succeeds.
- Preserve replacement cancellation, disappearance cancellation, failure
  completion, row integrity, request parameters, and refresh behavior.
- Add mutation-sensitive static contracts and synchronized project guidance.

## Files

- `WhineLocation/PulseViewController.swift`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-pulse-publication-ownership.md`

## Verification

- Prove the focused checker rejects ownership clearing before dispatch, a
  missing publication guard, or publication before ownership clearing.
- Run every repository and external-directory Make gate available on Linux.
- Run isolated hostile mutations covering the implementation, guidance, and
  completed plan record.
- Audit the exact diff, generated artifacts, credentials, conflict markers,
  binaries, large files, and whitespace.

## Scope Boundaries

- Do not change backend URLs, request parameters, Digits identity rules, pulse
  row parsing, table rendering, timer cadence, or dependencies.
- Do not claim local Xcode, simulator, or backend execution on Linux.
- Keep the pull request stacked on the request-ownership branch and do not
  merge or close either pull request without explicit authorization.

## Success Criteria

- A successful pulse snapshot publishes only while its exact request remains
  authoritative at main-queue execution time.
- Replacement refreshes and view disappearance make already-queued success
  blocks inert.
- Existing request cancellation and row-integrity contracts remain intact.

## Verification Completed

- All four Make gates passed from the repository root, and the absolute
  Makefile `check` gate passed from an external directory.
- Seven isolated hostile mutations were rejected across success ownership,
  ownership retention, publication ordering, failure completion, guidance,
  plan status, and plan evidence.
- Python checker compilation, `git diff --check`, and explicit artifact and
  changed-line secret audits passed.
- Xcode is unavailable on Linux, so native UIKit, Alamofire, simulator, and
  backend execution could not be performed.
