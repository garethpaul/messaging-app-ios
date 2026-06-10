# Pulse List User Guard

status: completed

## Context

`PulseViewController.getData()` loaded message list state with a direct Digits
session user ID lookup and parsed force-unwrapped response JSON. Message list
refreshes should follow the same normalized identity guardrails as read-state,
partner, and location flows.

## Completed Scope

- Required `currentDigitsUserID()` before requesting pulse list messages.
- Guarded missing response JSON before constructing `SwiftyJSON.JSON`.
- Cleared read-state arrays along with message arrays before each refresh.
- Ended refresh control state safely when refreshes run before the control is
  initialized or when refreshes are skipped.
- Extended the static baseline and docs for the pulse list user guard.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
