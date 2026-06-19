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
- Added status-only Alamofire validation for `200..<300` before JSON response
  handling so non-2xx responses populate the callback error and do not navigate
  without imposing a response MIME-type requirement.
- Added closed-world raw-byte SHA-256 contracts for the corrected Home Time
  controller, the exact main storyboard that binds its primary button, and the
  Xcode project/workspace/xcconfig build graph that selects those files.
- Added exact regular-file inventories for storyboard/XIB, build-graph, and
  test files, plus independent raw-byte contracts for the workflow and Makefile.
- Added an isolated test runner that validates protected bytes before loading
  tests, executes a copied candidate tree in a disposable repository, and then
  revalidates protected bytes and tree cleanliness after all gates.
- Changed the hosted workflow to invoke the protected runner and checker
  directly under a sanitized environment instead of trusting mutable Make
  execution or inherited `MAKEFLAGS`.
- Added independent mutation coverage for source/storyboard/project rewiring,
  decoys, byte/encoding changes, hash self-updates, interface/build/test
  inventory variants, test startup laundering, `sitecustomize`/`PYTHONPATH`
  import injection, mutation/restore startup, and workflow/Make gate skipping.
- Documented the guarded submission behavior across project guidance.

## Verification Completed

- `make check`
- `make lint`
- `make test`
- `make build`
- `python3 -m py_compile scripts/check-baseline.py`
- `python3 -I scripts/run-isolated-tests.py pre`
- `python3 -I scripts/run-isolated-tests.py test`
- `python3 -I scripts/check-baseline.py`
- `python3 -I scripts/run-isolated-tests.py post`
- `git diff --check`
- Historical pre-correction `push` Check run `27287606534` completed
  successfully for main SHA `854a1c6566e359a602b1582cdd106a1cfb5b4242`;
  it does not validate this local HTTP-validation correction.
- Historical pre-correction CodeQL Setup run `27402324851` completed
  successfully for main SHA `854a1c6566e359a602b1582cdd106a1cfb5b4242`;
  it does not validate this local HTTP-validation correction.
- Mutation checks confirmed the checker rejects an incomplete status,
  unfinished verification, altered run evidence, every prior source decoy,
  full-method block-comment substitution, storyboard action rewiring/removal/
  duplication/direct segue, added interface files and path/case/symlink
  variants, Xcode graph rewiring/additions, CRLF/encoding/single-byte mutations,
  test laundering/import injection, and workflow/Makefile test skipping.
- Independent test-owned SHA-256 values reject source or storyboard mutations
  even when the production checker hash is updated to bless the changed bytes.
- The implementation requires `guard let userId = currentDigitsUserID() else`
  before submission.
- The Alamofire request requires
  `.validate(statusCode: 200..<300).responseJSON` so only a 2xx response reaches
  the guarded navigation path without adding MIME-type rejection.
- The response callback requires `guard error == nil else` before calling
  `performSegueWithIdentifier("presentNav", sender: self)`.
