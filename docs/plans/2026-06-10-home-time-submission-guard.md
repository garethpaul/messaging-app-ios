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

## Work Completed

- Replaced direct Digits session dereferencing with `currentDigitsUserID()`.
- Kept the home-time endpoint and request payload unchanged.
- Moved navigation into the Alamofire response callback after an explicit
  success guard.
- Added mutation-sensitive baseline checks for normalized identity and callback
  ordering.
- Documented the guarded submission behavior across project guidance.

## Verification Completed

- `make check`
- `make lint`
- `make test`
- `make build`
- `python3 -m py_compile scripts/check-baseline.py`
- `git diff --check`
- Historical `push` Check run `27287606534` completed successfully for exact
  main SHA `854a1c6566e359a602b1582cdd106a1cfb5b4242`.
- Historical CodeQL Setup run `27402324851` completed successfully for exact
  main SHA `854a1c6566e359a602b1582cdd106a1cfb5b4242`.
- Mutation checks confirmed the plan checker rejects an incomplete status,
  unfinished verification, altered run evidence, and either missing guard.
- The implementation requires `guard let userId = currentDigitsUserID() else`
  before submission.
- The response callback requires `guard error == nil else` before calling
  `performSegueWithIdentifier("presentNav", sender: self)`.
