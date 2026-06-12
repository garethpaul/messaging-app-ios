# Checkout Credential Boundary

status: completed

## Context

The recorded remediation baseline describes the macOS checkout as
credential-free, but the exact PR head still uses the checkout action's default
credential persistence. Hosted validation only needs repository contents for
the offline static baseline and Xcode project parse.

## Objectives

- Disable checkout credential persistence without changing hosted coverage.
- Enforce one workflow, one read-only permission block, one checkout action,
  and one correctly nested boundary declaration.
- Preserve immutable action pins, `macos-15`, timeout, concurrency, and
  `make check`.
- Correct documentation to match the exact workflow.

## Implementation Units

### Workflow And Checker

Files: `.github/workflows/check.yml`, `scripts/check-baseline.py`

Add the non-persisted credential option and exact structural contracts for
workflow count, permissions, checkout count, nesting, contradiction, and plan
completion.

### Documentation

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Record the narrower workflow credential lifetime while keeping structural
hosted validation distinct from build, signing, authentication, location,
message, simulator, and UI coverage.

## Work Completed

- Added `persist-credentials: false` beneath the sole pinned checkout step.
- Added exact workflow, permission, checkout, nesting, contradiction, and plan
  evidence contracts to the static checker.
- Updated hosted-validation documentation without changing application or
  project behavior.

## Verification Completed

- `python3 scripts/check-baseline.py`
- `make lint`, `make test`, `make build`, and `make check`
- workflow YAML parse and `git diff --check`
- Hostile workflow and plan mutations

Local validation reports `xcodebuild` unavailable on Linux and proves the
portable static baseline only. Canonical hosted macOS checks remain required at
the exact successor head before owner merge.

## Boundaries

- Do not change Swift, plist, xcconfig, Xcode project, Pods, or backend values.
- Do not authenticate, request location, send messages, or call live services.
- Preserve the existing remediation PR and evidence.
