# Read-State Publication Ownership

status: completed

## Problem

`compareRead` previously cached the remote read-state array immediately after
starting its backend POST. A failed request therefore looked synchronized on
the next refresh and was not retried. The cache helper also looked up the
current Digits session again, so an asynchronous completion after an account
change could persist one user's state under another user's key.

## Design

- Capture the normalized Digits user ID before comparing local and remote
  state.
- Validate the read-state POST against the successful HTTP status range.
- Persist the remote array only from the successful response callback.
- Pass the captured user ID into the cache helper instead of looking up the
  current session again.
- Leave failed publications uncached so a later pulse refresh retries them.

## Test-First Plan

1. Add a current-source contract for validated success and captured identity.
2. Add hostile mutations for missing validation, eager persistence, and
   asynchronous identity re-read.
3. Run the current-source contract to record the RED failure.
4. Implement the minimal request and cache-helper changes.
5. Update public guidance, agent guidance, and `CHANGES.md`.
6. Run focused mutations, authenticated root and external `make check`, Python
   compilation, and `git diff --check`.
7. Require hosted macOS validation, CodeQL, and exact-head review before merge.

## Work Completed

The read-state POST now validates successful HTTP statuses and persists only
after its response succeeds. The completion passes the originating normalized
Digits user ID to `setRead`, while failures leave local state unchanged for a
future retry. The checker rejects missing validation, eager persistence, and
session re-reading in the cache helper.

## Verification Completed

The focused current-source contract failed against the eager cache write. The
repaired source and three hostile mutations pass. All 94 isolated tests pass
with two expected GNU Make capability skips. Authenticated root aliases,
external-directory `make check`, direct validation, Python compilation, and
`git diff --check` pass. Hosted push, pull-request, and CodeQL checks pass on
the implementation head. Codex review failed before analysis with HTTP 401;
the exact head received a clean immutable manual review.
