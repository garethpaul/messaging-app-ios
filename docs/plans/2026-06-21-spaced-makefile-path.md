# Spaced Makefile Path

status: completed

## Problem

GNU Make list functions split `MAKEFILE_LIST` on whitespace, so the documented
absolute `make -f` workflow failed when the checkout path contained spaces.

## Change

1. Derive the root from the raw Makefile path with shell-safe quote handling
   and POSIX `printf`/`sed` normalization.
2. Preserve `override ROOT` and reject command-line or environment replacement
   of `MAKEFILE_LIST`.
3. Protect root-resolution regressions against paths containing spaces,
   brackets, and a literal apostrophe within the isolated integrity chain.
4. Fail closed for literal `$()` paths because GNU Make expands those bytes
   before exposing the loaded filename through `MAKEFILE_LIST`.

## Verification

- Root and external `make lint`, `make test`, `make build`, and `make check`
  gates passed through the pre/test/baseline/post integrity sequence.
- Hostile `ROOT` values could not redirect commands.
- Command-line and environment `MAKEFILE_LIST` attacks failed closed.
- No live service credential, API call, location request, Xcode build, signing,
  simulator, or UI flow was used by portable verification.
