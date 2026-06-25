# Home-Time Request Ownership

status: completed

## Problem

`HomeTimeViewController` validated HTTP success but did not retain the
Alamofire request or associate its callback with the current visible controller
appearance. Repeated submissions could leave older callbacks able to navigate,
and a response arriving after disappearance could still present the next flow.

## Design

- Retain one optional home-time request.
- Mark each visible appearance active with a monotonically increasing
  generation and invalidate that generation on disappearance.
- Cancel and clear an existing request before every new submission and when the
  controller disappears.
- Reject inactive submissions before identity, date, request, or UI work.
- Capture the current generation, retain the validated request before its
  callback, and publish callback effects on the main queue.
- Require exact request identity before clearing ownership, then require the
  active captured generation and a successful response before navigation.

## Test-First Evidence

The canonical source contract and checker ownership requirements were added
before production code. The current-source regression failed because the
controller lacked retained request, activity, generation, and callback identity
handling. Production code was then changed to satisfy that contract. Mutation
tests remove disappearance cancellation, active-entry rejection, and callback
identity in turn and require the checker to reject each variant.
Codex review found that the original disappearance slice also included
`viewDidLoad`; a new red decoy mutation moved cancellation into that method,
then the checker boundary was narrowed to the next override.

## Verification

- Focused current-source and four ownership mutation tests pass.
- All 84 isolated tests pass with two unrelated GNU Make `--eval` skips.
- Authenticated root and external Make checks, static baseline, validation-root
  authentication, integrity pre/post checks, Python compilation, and
  `git diff --check` pass.
- Hosted macOS validation and CodeQL remain required before merge.
- Native runtime exercise remains unavailable without a compatible legacy
  Xcode/CocoaPods and retired backend-service environment.
