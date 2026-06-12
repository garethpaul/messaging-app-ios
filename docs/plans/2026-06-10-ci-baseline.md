# CI Baseline

status: completed

## Context

The repository had a local static `make check` baseline for the legacy iOS
messaging prototype, but no hosted workflow ran it for pushes and pull
requests. The audit also flagged a plaintext RFC reference inside the vendored
SwiftyJSON source and the need to keep the retired SDK posture explicit.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check`.
- Updated the SwiftyJSON RFC reference to an HTTPS documentation URL.
- Extended the static checker and docs so the hosted CI path and legacy SDK
  posture stay visible.

## Verification

- `make check`
