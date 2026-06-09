# Partner Prefix Preservation

status: completed

## Context

The partner phone field seeded `+1` whenever editing began. That helped blank
entry, but it could also erase a partially entered partner number when the field
was focused again.

## Objectives

- Keep the `+1` seed for blank partner phone fields.
- Preserve any nonblank partner number already entered by the user.
- Keep the partner request guardrails for normalized partner numbers and Digits
  user identities.
- Extend the static baseline and docs so the focus behavior stays intentional.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
