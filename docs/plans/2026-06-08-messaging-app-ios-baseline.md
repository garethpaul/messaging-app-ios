# Messaging App iOS Baseline Plan

status: completed

## Context

`messaging-app-ios` is a legacy Swift iOS messaging prototype named
WhineLocation. It uses vendored Fabric, Crashlytics, TwitterKit, Digits,
TwitterCore, CocoaPods, Parse, Alamofire, and location-related code.

## Risks

- The app target referenced a missing `WhineLocation/Info.plist`, preventing
  repeatable project verification.
- The Fabric run script contained raw crash-reporting key material.
- The Xcode project referenced local machine paths and a duplicate DigitsKit
  framework from a desktop folder.
- Message, phone identity, contacts, credentials, and location data are
  sensitive and need explicit local/CI configuration boundaries.

## Work Completed

- Restored tracked app and test plist files with bundle metadata and privacy
  usage descriptions for contacts and location.
- Replaced committed Fabric/Crashlytics values with `FABRIC_API_KEY` and
  `CRASHLYTICS_BUILD_SECRET` build settings.
- Removed stale local framework search paths, the desktop DigitsKit reference,
  and the absolute bridging-header path.
- Added `.gitignore`, a Fabric credential template, `Makefile`, and
  `scripts/check-baseline.py`.
- Updated docs for static verification and credential handling.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
