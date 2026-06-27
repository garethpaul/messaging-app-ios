# Changes

## 2026-06-26 18:36 PDT — P1 read-state callback ordering

- Found that overlapping successful read-state POSTs could complete out of
  order and let an older callback overwrite the cache after a newer pulse
  refresh had observed different state.
- Added a monotonic publication generation that advances for every valid
  remote observation, is captured before starting a changed-state POST, and
  must still be current before the successful callback persists locally.
- Added a current-source contract and hostile mutations for a missing guard or
  an increment moved too late to invalidate already-running publications.
- Updated read-state ownership guidance and the completed implementation plan.
- The seven focused read-state contracts pass. Authenticated root and
  external-directory `make check` each pass all 97 isolated tests with two
  expected GNU Make capability skips; direct Python compilation and
  `git diff --check` pass. `xcodebuild` is unavailable locally. Required
  `codex review --base origin/master` was attempted on implementation head
  `b5df392` but failed before analysis with OpenAI HTTP 401 authentication
  errors. Hosted, immutable final-head review, merge, and post-merge evidence
  remain pending.

## 2026-06-26 18:19 PDT — P1 read-state publication ownership

- Found that `compareRead` cached remote read state immediately after starting
  its POST, so transport or non-2xx failures suppressed later retries.
- Found that the asynchronous cache path re-read the current Digits session,
  allowing an account change during the request to bind the completed state to
  the wrong local user key.
- Added successful-status validation and moved persistence into the successful
  response callback. The cache helper now requires the originating normalized
  Digits user ID captured before publication.
- Added a fail-closed checker contract and hostile mutations for missing HTTP
  validation, eager cache writes, and asynchronous identity re-reading. The
  focused current-source test first failed against the old eager write; the
  repaired source and all three mutations pass.
- Added the completed read-state publication ownership plan and synchronized
  README, security, vision, and agent guidance.
- All 94 isolated tests pass with two expected GNU Make capability skips.
  Authenticated `make lint`, `make test`, `make build`, and `make check` pass
  from the repository, and external-directory `make check`, direct validation,
  Python compilation, and `git diff --check` pass. `xcodebuild` is unavailable
  locally. Hosted push run 28274377109, pull-request run 28274377982, and PR
  analysis/CodeQL run 28274378068 pass on implementation head `00be76a`.
- Required `codex review --base origin/master` was attempted on that exact
  head but failed before analysis with OpenAI HTTP 401 authentication errors.
  An immutable manual review confirmed the PR head, request validation,
  success-before-persistence ordering, captured identity, mutation coverage,
  and clean diff with no actionable finding.

## 2026-06-26 04:32 PDT — P1 configured backend and privacy boundary

- Found three state-changing Swift requests that bypassed the placeholder-safe
  plist configuration and retained the historical App Engine host for user
  registration, location sharing, and message read-state publication.
- Added `userUrl`, `locationUrl`, and `pulseListReadUrl` with
  `https://example.invalid` defaults, then routed all three requests through
  `getInfo` so every backend call is locally configurable and a clean checkout
  cannot contact the historical host.
- Added a canonical ignored `Info.local.plist` and
  `ServiceKeys.local.xcconfig` workflow, an explicit `xcodebuild -xcconfig`
  example, and a nine-route map of phone identity, message, read-state,
  home-time, beacon, and precise-location fields.
- Added fail-closed source, plist, documentation, and roadmap contracts. The
  red baseline reported all three missing keys, all three source bypasses, the
  historical host, the absent guide, missing document links, and incomplete
  plan evidence before production changes.
- During repeated alias validation, `make test` failed postflight because nested
  snapshot tests could overwrite the outer checkout's fixed `/tmp` integrity
  state. Added a red two-checkout regression and made default state filenames
  checkout-specific; the previously failing back-to-back alias now passes.
- PR #28 merged concurrently with an identity-bound, transition-only beacon
  publication guard. Rebased onto that change, corrected the endpoint data map
  to include normalized beacon identity, and regenerated the combined
  checker/runner/validation-root authentication chain.
- All 90 combined isolated tests pass with two expected GNU Make capability
  skips. All four Make aliases passed from repository and external working
  directories before the rebase, combined rebased `make check` passes, and 29
  isolated backend-boundary mutations are rejected. `xcodebuild` is unavailable
  locally, so hosted macOS project parsing remains required.
- Retired the backend-configuration and privacy-expectation roadmap items;
  legacy SDK modernization and manual login/message flow verification remain.

## 2026-06-26 04:24 PDT

- **Priority:** P1 beacon identity and redundant-write correctness.
- **Summary:** Bound beacon publications to normalized Digits identity and a
  real proximity transition.
- **Work:** Moved the POST inside the existing previous-proximity comparison,
  included `userId` in request parameters, and left `prev` unchanged when no
  authenticated identity is available.
- **Threads:** No delegated threads were used.
- **Files:** Updated the Core Location delegate, static and hostile mutation
  contracts, validation-chain hashes, privacy guidance, roadmap, agent notes,
  and a completed plan.
- **Validation:** The focused current-source test and checker first failed on
  the anonymous unconditional POST. The repaired source and three hostile
  identity/parameter/ordering mutations pass. All 89 isolated tests, root and
  external-directory authenticated `make check`, direct validation-root and
  baseline checks, Python compilation, and `git diff --check` pass; two
  unrelated GNU Make `--eval` cases skip locally. Hosted macOS and CodeQL
  remain merge gates.
- **Findings:** `didRangeBeacons` previously posted on every known-beacon
  callback before checking `prev`, and the backend request carried no user
  identity even when a Digits session existed.
- **Blockers:** Runtime ranging still requires compatible legacy Xcode,
  Bluetooth beacon hardware, Digits identity, and the retired backend stack.
- **Next action:** Verify the exact PR head on hosted macOS and merge only that
  green reviewed head.

## 2026-06-25 10:20 PDT

- **Priority:** P1 validation portability and trust-boundary accuracy.
- **Summary:** Corrected the Makefile-path capability gate to require GNU Make
  4.3 instead of treating every GNU Make 4 release as equivalent.
- **Work:** Added a version-boundary regression covering GNU Make 3.81, 4.2,
  4.3, and 4.4; updated contributor and security guidance to match the tested
  behavior.
- **Finding:** GNU Make 4.2.1 expands literal `$(` and `${` path syntax before
  repository rules can inspect `MAKEFILE_LIST`, while the original fix was
  validated on GNU Make 4.3.
- **Validation:** The 4.2 host now skips only the two unenforceable path
  assertions while retaining the explicit 4.3+ contract; the authenticated
  validation chain and hosted checks must pass before merge.
- **Blockers:** Native app behavior still requires compatible macOS/Xcode and
  retired Digits/Parse/Fabric services.

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
  it. The regression now uses a real `$(shell ...)` payload on GNU Make 4.3+
  and skips that unenforceable assertion on 3.81 and 4.2; guidance documents
  the boundary.
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
