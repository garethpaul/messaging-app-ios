# Home Time Submission Guard

status: completed

## Problem

The home-time action dereferences the Digits session directly and transitions
away immediately after starting its POST. A missing session can crash the flow,
and a failed request is presented as though the update succeeded.

## Scope

- Require the normalized current Digits user ID before constructing the POST.
- Keep the existing first-party home-time endpoint and POST parameters.
- Transition only from a successful Alamofire response callback.
- Add static and mutation guardrails for identity and response handling.
- Document the behavior without adding credentials or live service tests.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- mutation checks for the user and response-success guards
- `git diff --check`

## Work Completed

- Replaced direct Digits session dereferencing with `currentDigitsUserID()`.
- Kept the home-time endpoint and request payload unchanged.
- Moved navigation into the Alamofire response callback after an explicit
  success guard.
- Added mutation-sensitive baseline checks for normalized identity and callback
  ordering.
- Documented the guarded submission behavior across project guidance.
