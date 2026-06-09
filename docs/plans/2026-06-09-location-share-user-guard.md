# Location Share User Guard

status: completed

## Context

`ShareLocation.location` posted latitude and longitude updates even when the
Digits session was missing, using an empty `userId`. Location data is sensitive
and should stay tied to the same normalized Digits identity guard used by
message read-state storage.

## Objectives

- Require `currentDigitsUserID()` before sending location updates.
- Reuse Digits user ID normalization so blank session IDs do not post
  coordinates.
- Preserve the existing location POST endpoint and payload shape when a
  normalized user ID exists.
- Extend the static baseline and docs for the location share user guard.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
