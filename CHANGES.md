# Changes

## 2026-06-25 09:23 PDT

- **Priority:** P1 stale write-response and navigation correctness.
- **Summary:** Bound home-time submission callbacks to one retained request and
  the controller appearance that created it.
- **Work:** Added appearance activity/generation state, replacement and
  disappearance cancellation, exact request identity cleanup, main-queue
  publication, and success-only navigation.
- **Threads:** No delegated threads were used.
- **Files:** Updated the home-time controller, static and mutation contracts,
  authenticated validation hashes, guidance, and a completed plan.
- **Validation:** The ownership contract failed before production changes;
  focused current-source and hostile disappearance/activity/identity mutations,
  all 83 Python tests, root and external-directory `make check`, direct baseline,
  validation-root authentication, Python compilation, and `git diff --check`
  pass. Two unrelated GNU Make `--eval` cases skip locally; hosted validation
  remains the merge gate.
- **Review fix:** Codex identified that the disappearance scan extended through
  `viewDidLoad`. A red mutation proved cancellation could be moved there as a
  decoy; the scan now stops at the next override and rejects that variant.
- **Findings:** The previous callback could navigate after replacement or
  disappearance because no transport, request identity, or appearance state
  was retained.
- **Blockers:** Runtime behavior still requires compatible macOS/Xcode and the
  retired Digits/Parse/Fabric service stack.

## 2026-06-25 09:08 PDT

- **Priority:** P1 local validation command-execution boundary.
- **Summary:** Rejected literal Make syntax in Makefile paths before trusted
  root resolution can evaluate it.
- **Work:** Added pre-expansion `$(` and `${` guards to the live Makefile and
  every independently generated Makefile contract, plus hostile path tests.
- **Threads:** No delegated threads were used.
- **Files:** Updated Make authority, checker/test/runner/verifier templates,
  hosted authentication hashes, project guidance, and a completed plan.
- **Validation:** The existing `$()` regression failed on untouched `master`
  and created its marker; focused `$()`/`${` tests, the 80-test suite, hostile
  external marker probe, root and external-directory `make check`, validation
  chain pre/post checks, and `git diff --check` pass. Two GNU Make `--eval`
  cases remain skipped because this host's Make lacks that option; Xcode project
  parsing is skipped because `xcodebuild` is unavailable.
- **Findings:** A previously documented fail-closed path reached Make expansion
  and executed attacker-controlled text before the later shasum failure.
- **Hosted follow-up:** The first macOS runs exposed that Apple's GNU Make 3.81
  expands `MAKEFILE_LIST` path syntax before any repository rule can inspect
  it. The regression now uses a real `$(shell ...)` payload on GNU Make 4+ and
  skips that unenforceable assertion on 3.81; guidance documents the boundary.
- **Blockers:** Native app behavior still requires compatible macOS/Xcode and
  retired Digits/Parse/Fabric services.
- **Deferred work:** Home-time request ownership was saved outside the tree and
  resumed after this higher-priority validation flaw merged.
- **Next action:** Review the exact PR head and merge only after hosted checks
  pass.

## 2026-06-21

- Made absolute external Makefile invocations work when checkout paths contain
  spaces or a literal apostrophe while rejecting `ROOT` and `MAKEFILE_LIST`
  attempts to redirect isolated verification.
- Added a verifier-first validation gate so `scripts/run-isolated-tests.py` is
  hashed before it can run isolated preflight, tests, or postflight checks.
- Added a hosted workflow SHA-256 check for `scripts/verify-validation-chain.py`
  so the first verifier bytes are authenticated before Python executes them.
- Rejected protected Make metadata overrides, later single-colon public recipe
  replacement, and non-executing Make modes; documented caller startup code and
  caller-added double-colon recipes as outside the local Make trust boundary.
  Fixed validation tools to system paths and authenticated the static checker
  before the isolated runner imports or executes it.
- Rejected GNU Make `--eval` during parsing before target-specific variables can
  replace the authenticated validation root or execute a caller-selected shell.

## 2026-06-17

- Added partner request ownership so repeated taps supersede older lookups and
  stale callbacks cannot navigate after the screen disappears.
- Added pulse send request ownership so drafts clear and pulse lists refresh
  only after the exact retained write succeeds, while failures remain retryable.

## 2026-06-16

- Added pulse publication ownership so a successful snapshot revalidates its
  exact request on the main queue before mutating table and read-state data.
- Added pulse request ownership so replaced and disappearing list loads are
  canceled and stale callbacks cannot overwrite newer pulse snapshots.
- Added pulse row integrity so incomplete backend records are skipped and all
  table and read-state arrays are replaced together before reload.

## 2026-06-15

- Added waiting request cancellation so obsolete Alamofire transport is stopped
  without allowing canceled callbacks to clear a newer request.
- Added a waiting concurrent check guard to prevent overlapping delayed match
  requests and repeated navigation after a successful response.
- Added a waiting view activity guard so delayed work and responses become inert
  after the controller leaves the screen.
- Added a waiting appearance generation guard so a callback from an earlier
  appearance cannot mutate state or navigate after controller re-entry.
- Added a waiting active check entry guard so off-screen callers cannot strand
  request state or suppress the next appearance's automatic check.

## 2026-06-14

- Added a waiting session and response guard before match requests and JSON
  parsing, with loading-state completion tied to guarded outcomes.
- Scoped the repeating pulse refresh timer to the visible controller lifecycle.
- Added a pulse send session guard before request, throttle, text, or button
  mutation when the Digits session or normalized user ID is unavailable.

## 2026-06-13

- Made every Make verification alias resolve the static checker from the
  checkout, including absolute Makefile invocations elsewhere.

## 2026-06-12

- Stopped the hosted checkout from persisting its credential and added an exact
  static contract for the sole workflow, permissions, and checkout step.

## 2026-06-10

- Added a home time submission guard so updates require a normalized Digits
  user ID and navigate only after a successful POST response.
- Added pinned, read-only macOS hosted validation for `make check` and
  `WhineLocation.xcodeproj` parsing without credentials or runtime service calls.
- Added a pulse list user guard so message refreshes require a normalized
  Digits user ID and guarded response JSON before parsing.

## 2026-06-09

- Added `make lint`, `make test`, and `make build` aliases so local gate
  commands run the same baseline as `make check`.
- Added a location share user guard so location POSTs require a normalized
  Digits user ID.
- Added a Digits login success guard so failed authentication callbacks do not
  open the partner flow or store identity.
- Added a new partner user guard so partner POSTs require a normalized Digits
  user ID and nonblank partner number.
- Added partner prefix preservation so focusing the partner field seeds blank
  values without erasing already-entered numbers.
- Fixed the pulse send throttle so message sends mark the cooldown state with
  assignments instead of unused equality checks.

## 2026-06-08

- Replaced committed Fabric/Crashlytics build-script values with `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` environment placeholders.
- Restored a committed `WhineLocation/Info.plist` with placeholder Fabric/Twitter keys and documented backend endpoint keys.
- Added `WhineLocation/ServiceKeys.xcconfig.example` for local credential setup.
- Switched first-party user, location, hometime, and beacon updates from GET to POST.
- Removed location, waiting, and pulse debug logging and guarded beacon/location casts in `CoreLocationController`.
- Guarded message read-state updates when Digits sessions or remote array data are unavailable.
- Added Digits user ID normalization so blank session IDs do not key message read-state storage.
- Added `make check` static baseline verification.
