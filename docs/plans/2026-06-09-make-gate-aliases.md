# Messaging App iOS Make Gate Aliases

status: completed

## Context

The repository had a single `make check` target for the static baseline. The
fleet pre-push gate also invokes `make lint`, `make test`, and `make build`, so
those commands should reach the same SDK-free checks instead of failing before
the baseline runs.

## Objectives

- Expose `lint`, `test`, `build`, and `check` Make targets.
- Keep all four targets delegated to `scripts/check-baseline.py`.
- Document the gate commands in README, VISION, SECURITY, and CHANGES.
- Extend the static checker so the aliases and completed plan remain covered.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
