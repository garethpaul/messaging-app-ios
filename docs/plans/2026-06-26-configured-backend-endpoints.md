# Configured Backend Endpoints

status: completed

## Problem

Six backend routes use placeholder-safe `Info.plist` configuration, but user
registration, location sharing, and message read-state writes still contain the
historical App Engine host in Swift source. Those requests bypass local backend
configuration and can transmit phone identity, coordinates, or message state
to a committed endpoint.

## Design

- Add `userUrl`, `locationUrl`, and `pulseListReadUrl` to the tracked plist with
  `example.invalid` defaults.
- Route all three writes through `getInfo`, matching the other backend calls.
- Fail validation if any tracked backend default is live or the historical host
  returns to executable source.
- Add a canonical guide for ignored local plist/xcconfig setup and document the
  request fields sent by every route.
- Link the guide from README, VISION, and SECURITY, then retire the completed
  backend-configuration and privacy-documentation roadmap items.

## Verification

- The new source, plist, and documentation contracts failed first.
- The direct static checker passes after routing all three requests and adding
  the guide.
- Twenty-nine isolated hostile mutations covering all nine tracked defaults,
  all three source lookups, the historical-host ban, thirteen guide claims, and
  three guide links were rejected.
- A repeated alias run exposed a real integrity-state collision: nested snapshot
  tests could overwrite the outer checkout's fixed `/tmp` state file. A red
  regression proved two checkouts selected the same path; the runner now derives
  a checkout-specific suffix and the regression passes.
- The branch was rebased after PR #28 added identity-bound, transition-only
  beacon publication. The guide and checker now record that beacon reports also
  include normalized user identity.
- The combined refreshed authenticated chain passes 90 isolated tests with two
  expected skips on this host's GNU Make capability. Before the rebase,
  `make lint`, `make test`,
  `make build`, and `make check` pass from both the repository and an external
  working directory after the collision fix; combined rebased `make check`
  also passes.
- `xcodebuild` is unavailable on this Linux host, so hosted macOS project
  parsing and CodeQL remain required before merge.
