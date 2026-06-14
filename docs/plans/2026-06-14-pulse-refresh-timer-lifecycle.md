# Pulse Refresh Timer Lifecycle

Status: planned

## Problem

Every pulse-screen appearance schedules a repeating refresh timer without
retaining or invalidating it. Repeated navigation can therefore accumulate
refresh requests, and the timer can keep the controller alive after the screen
disappears.

## Scope

- Retain at most one repeating pulse refresh timer.
- Invalidate and clear it when the screen disappears.
- Preserve the 30-second refresh interval, immediate initial load, keyboard
  observer lifecycle, and message behavior.
- Add mutation-sensitive static and documentation contracts.

## Validation

- Run every canonical Make gate from the checkout and an external directory.
- Reject mutations that remove timer ownership, invalidation, clearing, or plan
  completion evidence.
- Run exact diff, generated-artifact, conflict-marker, intended-path, and
  secret-pattern audits.
- Record that Xcode and simulator execution are unavailable on Linux.

## Risks

- Timer behavior remains tied to the run loop used by the legacy Swift sample.
- The stacked base PR must merge first and remain open until then.
