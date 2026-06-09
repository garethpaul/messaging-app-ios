# Digits User ID Normalization Plan

status: completed

## Context

Message read-state storage is keyed by the active Digits session user ID. The session lookup was guarded, but blank or whitespace-only IDs could still be used as the local defaults key.

## Objectives

- Normalize Digits session user IDs before read-state storage uses them.
- Reject missing, blank, or whitespace-only user IDs.
- Preserve guarded remote read-state array handling.
- Extend the static baseline and docs to keep Digits user ID normalization visible.

## Verification

- `make check`
- `git diff --check`
