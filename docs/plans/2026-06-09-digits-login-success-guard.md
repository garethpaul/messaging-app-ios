# Digits Login Success Guard Plan

status: completed

## Context

`LoginViewController` registers the Digits user, stores the Parse installation
identity, and opens the partner flow from the authentication callback. Failed
authentication callbacks should not enter identity-backed app flow.

## Objectives

- Require a non-nil Digits session and no authentication error before continuing.
- Reuse the normalized Digits user ID helper before registering or storing user
  identity.
- Keep failed authentication callbacks out of the partner flow.
- Extend the static baseline and docs so the login success guard remains
  visible.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
