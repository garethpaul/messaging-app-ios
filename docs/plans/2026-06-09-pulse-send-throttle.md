# Pulse Send Throttle

status: completed

## Context

`PulseViewController` intended to disable repeat sends during the short refresh
cooldown after posting a message. The code compared `sendAvailable` to `false`
and `true` instead of assigning those values, leaving the state unchanged and
allowing rapid repeat taps to post duplicate messages.

## Objectives

- Set `sendAvailable` to `false` before posting a pulse message.
- Restore `sendAvailable` to `true` after the delayed refresh path runs.
- Keep the existing send endpoint, text-field reset, refresh delay, and button
  color feedback.
- Extend the static baseline and docs so the throttle remains an assignment,
  not an unused equality check.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
