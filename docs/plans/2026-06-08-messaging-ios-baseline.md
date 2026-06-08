# Messaging App iOS Baseline Plan

## Context

`messaging-app-ios` is a legacy Swift iOS messaging prototype using Digits,
TwitterKit, Fabric/Crashlytics, Parse, Alamofire, location sharing, and a
Google App Engine backend. The repo had a missing committed app plist, a Fabric
build phase with literal credentials, and first-party requests that sent
identity/location data through GET query strings.

## Risks

- Committed Fabric/Crashlytics values and local framework paths make the project
  unsafe and difficult to reproduce on another machine.
- Missing app plist and ignored plist rules obscure required service keys,
  backend endpoint keys, and location permission strings.
- GET requests put phone identifiers, user identifiers, hometime, beacon, and
  location values into URLs.
- Location, waiting, and pulse debug logging can expose behavior or private
  messaging state; force casts can crash on malformed location/beacon delegate
  inputs.

## Work Completed

- Replaced Fabric build script literals with environment placeholders.
- Removed the developer Desktop framework reference from the Xcode project.
- Added `WhineLocation/Info.plist` with placeholder Fabric/Twitter settings,
  backend endpoint keys, and location permission descriptions.
- Added `WhineLocation/ServiceKeys.xcconfig.example` and safer ignore rules for
  local config.
- Switched first-party identity/location update requests to POST.
- Removed location, waiting, and pulse debug logging and guarded location/beacon casts.
- Added `Makefile` and `scripts/check-baseline.py` for non-Xcode static checks.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
