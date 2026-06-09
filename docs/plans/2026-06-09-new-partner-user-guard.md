# New Partner User Guard

status: completed

## Context

`NewPartnerViewController` posts partner requests with the current Digits user
identity and the entered partner phone number. Other identity-sensitive paths
now use normalized Digits user IDs, but the partner flow still read the session
directly and accepted blank partner input.

## Objectives

- Require a normalized current Digits user ID before partner requests.
- Require an available Digits session before reading the current phone number.
- Trim and reject blank partner numbers before backend POSTs.
- Preserve the existing partner request endpoint and segue behavior after a
  successful response.
- Extend the static baseline and docs so the partner flow keeps the same
  identity guardrails as read-state and location sharing.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
