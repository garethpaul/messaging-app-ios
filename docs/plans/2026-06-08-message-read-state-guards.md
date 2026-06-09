# Message Read-State Guards Plan

status: completed

## Context

`Messages.swift` compares remote message read-state data against a value cached
in `NSUserDefaults`, then posts an update when the data changes. The legacy
implementation force-cast both values to `NSArray` and assumed a Digits session
was always present.

## Objectives

- Preserve read-state caching by Digits user ID.
- Return safely when no Digits session is available.
- Return safely when remote read-state data is not an array.
- Avoid force-casting cached local read-state values.
- Keep the read-state update on a POST request.
- Extend `make check` so future message read-state changes preserve these
  guards.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
