# Waiting View Activity Guard

Status: planned

## Problem

The waiting controller prevents overlapping checks and stale session results,
but its two-second delayed block and backend completion remain active after the
view disappears. A late match can therefore perform a segue from an off-screen
controller, while a delayed block can start a request the user no longer needs.

## Scope

- Track whether the waiting view is currently active through UIKit appearance
  callbacks.
- Stop delayed work before the backend request when the view is inactive.
- Ignore backend completions after the view disappears, including successful
  matches, without leaving the controller permanently in-flight.
- Preserve the existing delay, one-request guard, identity validation, request
  parameters, loading UI, retry behavior, and successful active-view segue.
- Add dependency-free static contracts and maintenance guidance.

## Implementation

1. Add private view-activity state set in `viewWillAppear` and cleared in
   `viewWillDisappear`.
2. Release the in-flight flag when the view disappears so a later visible
   refresh can retry.
3. Guard both the delayed request boundary and response boundary before any
   off-screen request, UI update, matched-state mutation, or segue.
4. Extend the baseline checker, completed evidence, and project docs.

## Verification

- Run the dependency-free baseline, Swift source contracts, and every Make gate
  from the repository and an external directory with explicit timeouts.
- Reject mutations that remove appearance state, delayed-work gating,
  completion gating, retry release, guidance, or completed plan evidence.
- Audit the exact diff, generated artifacts, credential patterns, project-file
  integrity, conflict markers, binaries, large files, and intended paths.

## Risks

- `viewDidLoad` schedules the initial check before `viewWillAppear`; the delay
  remains long enough for the normal appearance callback to activate the view.
- In-flight network work is not cancelled at the transport layer; its callback
  is made inert after disappearance.
- The stacked base pull request must remain available and merge first.
