# Beacon Publication Guard

status: completed

## Problem

`CoreLocationController` publishes a beacon update on every ranging callback,
before checking whether proximity changed, and without requiring or sending a
normalized Digits user ID. That can produce redundant state-changing traffic
and leaves backend beacon state detached from the authenticated app identity.

## Design

- Keep the existing safe beacon cast and POST endpoint.
- Compare the current proximity with `prev` before any identity or network
  work.
- Require `currentDigitsUserID()` inside the changed-proximity branch.
- Send the normalized `userId` with the beacon identifier.
- Advance `prev` only after the guarded publication is started, so a callback
  without identity does not consume the transition.
- Do not add request ownership or UI behavior to this fire-and-forget location
  delegate path.

## Test-First Plan

1. Add a current-source contract that requires transition, identity, request,
   and state-update ordering.
2. Add hostile mutations for missing identity, missing request identity, and a
   publication moved before the proximity transition.
3. Run the focused current-source test and static checker to record the RED
   failure.
4. Implement the minimal `CoreLocationController` change.
5. Update README, security, vision, agent guidance, and `CHANGES.md`.
6. Run focused mutation tests, authenticated `make check`, external-directory
   `make check`, Python compilation, and `git diff --check`.
7. Require hosted macOS validation, CodeQL, and exact-head review before merge.

## Work Completed

The beacon POST now sits inside the changed-proximity branch, requires
`currentDigitsUserID()`, includes that normalized identity in the request, and
updates `prev` only after publication begins. The checker enforces ordering and
three mutations remove the guard, remove the request identity, or move the POST
ahead of the transition.

## Verification Completed

The current-source contract failed before production code changed. The focused
current-source test, three hostile mutations, and direct baseline checker pass.
All 89 isolated tests, authenticated root and external-directory `make check`,
validation-root and baseline checks, Python compilation, and `git diff --check`
pass. Two unrelated GNU Make `--eval` cases skip on this host. Hosted macOS
validation and CodeQL remain merge gates.
