# Hosted Project Validation

status: completed

## Context

The repository has static checks for credentials, identity normalization,
message state, location sharing, request methods, pulse throttling, project
wiring, and vendored SDK references, but no hosted Xcode validation.

## Priorities

1. Add pinned, read-only, bounded macOS CI for the canonical `make check` gate.
2. Parse `WhineLocation.xcodeproj` whenever Xcode is available.
3. Enforce the workflow contract from `scripts/check-baseline.py`.
4. Keep credentials, authentication, backend calls, location sharing, message
   content, CocoaPods installation, signing, and simulator execution outside CI.

## Implementation Units

### Workflow And Checker

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`

Add push, pull-request, and manual triggers; read-only permissions; concurrency
cancellation; a bounded `macos-15` job; commit-pinned checkout; and `make check`.
Require those properties and run `xcodebuild -list -project
WhineLocation.xcodeproj` when Xcode exists.

### Documentation

Files:

- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`
- `docs/plans/2026-06-10-hosted-project-validation.md`

Document project parsing as structural validation only, not authentication,
network, location, simulator, or message-flow coverage.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted macOS `Check` workflow for the pushed commit

## Boundaries

- Do not provide service credentials or contact configured backends in CI.
- Do not install pods, access location, or introduce signing material.
