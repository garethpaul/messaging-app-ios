# Waiting Refresh Response Guard

status: completed

## Context

`WaitingViewController.check()` force-loads the Digits session and response JSON.
It also hides the spinner immediately after starting the request rather than when
the callback completes. A missing session or malformed/failed response can
therefore crash the waiting flow or leave its progress state disconnected from
the request lifecycle.

## Priorities

1. Require a normalized Digits user ID before posting a waiting refresh.
2. Parse waiting JSON only when the Alamofire callback has no error and a body.
3. Restore the spinner and waiting text in the callback on every response path.
4. Protect the behavior with the portable static contract.

## Implementation Units

### Waiting Flow

File: `WhineLocation/WaitingViewController.swift`

Guard the optional Digits session through `currentDigitsUserID()`, retain the
session phone number for the request, and use a callback `defer` block for UI
cleanup before guarded response parsing and navigation.

### Static Contract And Documentation

Files:

- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-waiting-refresh-response-guard.md`

Require the identity guard, callback-scoped UI cleanup, guarded JSON parsing,
and synchronized maintenance documentation.

## Verification

Completed locally on 2026-06-12:

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hostile mutations removing the identity, JSON, and callback cleanup guards
  were each rejected by their specific static contract
- `git diff --check`

`xcodebuild` is unavailable on this Linux host, so local verification is static.
Hosted push and pull-request checks will be recorded after the branch is pushed.

## Boundaries

- Do not make live backend requests in verification.
- Do not change endpoint, request parameters, or match semantics.
- Do not claim simulator or app-runtime coverage without Xcode execution.
