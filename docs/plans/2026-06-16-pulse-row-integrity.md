# Pulse Row Integrity

Status: completed

## Priority

P1 crash prevention. The pulse table uses `dataDate.count` for its row count but
indexes four sibling arrays for each row, so partially populated response records
can produce an out-of-range trap during rendering.

## Problem

`PulseViewController.getData()` clears live table state before the request
completes and appends each response field independently. A record missing any
one of `dataType`, `dataInfo`, `date`, `rndId`, or `isRead` can leave the five
parallel arrays at different lengths while `cellForRowAtIndexPath` assumes every
index exists in all of them.

## Approach

- Build replacement pulse arrays locally while parsing the response.
- Accept a row only when all five fields required by rendering and read-state
  comparison are present.
- Publish all five arrays together on the main queue immediately before table
  reload and read-state comparison.
- Preserve the normalized Digits user guard, request parameters, refresh-control
  completion, rendering behavior, timer lifecycle, and send flow.
- Add mutation-sensitive static contracts, maintained guidance, and completed
  plan evidence.

## Files

- `WhineLocation/PulseViewController.swift`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-pulse-row-integrity.md`

## Verification

- Prove the static regression contract rejects independent live-array appends,
  incomplete-field acceptance, or publication after reload.
- Run every repository and external-directory Make gate available on Linux.
- Reject isolated parsing, alignment, publication-order, guidance, and plan
  completion mutations.
- Audit the exact diff, project-file drift, generated artifacts, credentials,
  conflict markers, binaries, large files, and whitespace.

## Scope Boundaries

- Do not change backend URLs, request parameters, Digits identity rules, row
  rendering, read-state behavior, dependencies, or the Xcode project.
- Concurrent refresh replacement and cancellation remain separate lifecycle work.
- Linux cannot compile or execute this legacy iOS app; hosted validation remains
  the canonical platform evidence for the exact pushed head.
- Do not merge or close stacked pull requests without explicit authorization.

## Success Criteria

- Every published pulse row has all five fields used by the table and read-state
  flow.
- Live table arrays remain aligned and are replaced together only after parsing
  finishes.
- Existing pulse and waiting lifecycle contracts remain intact.

## Verification Completed

- All four Make gates passed from the repository root on Linux.
- The absolute Makefile `check` gate passed from an external directory.
- The Python baseline checker compiled with bytecode redirected outside the
  repository.
- Eight isolated hostile mutations were rejected across complete-field parsing,
  local accumulation, publication ordering, refresh completion, maintained
  guidance, changelog evidence, and plan completion status.
- `git diff --check`, explicit generated-artifact inspection, tracked secret
  scanning, and the intended-file review passed.
- Xcode is unavailable on Linux, so native UIKit, Alamofire, and backend behavior
  remains delegated to the pinned hosted macOS baseline for the exact pushed
  head; no local native build or runtime execution is claimed.
