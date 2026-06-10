# Changes

## 2026-06-10

- Added pinned, read-only macOS hosted validation for `make check` and
  `WhineLocation.xcodeproj` parsing without credentials or runtime service calls.
- Added a pulse list user guard so message refreshes require a normalized
  Digits user ID and guarded response JSON before parsing.

## 2026-06-09

- Added `make lint`, `make test`, and `make build` aliases so local gate
  commands run the same baseline as `make check`.
- Added a location share user guard so location POSTs require a normalized
  Digits user ID.
- Added a Digits login success guard so failed authentication callbacks do not
  open the partner flow or store identity.
- Added a new partner user guard so partner POSTs require a normalized Digits
  user ID and nonblank partner number.
- Added partner prefix preservation so focusing the partner field seeds blank
  values without erasing already-entered numbers.
- Fixed the pulse send throttle so message sends mark the cooldown state with
  assignments instead of unused equality checks.

## 2026-06-08

- Replaced committed Fabric/Crashlytics build-script values with `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` environment placeholders.
- Restored a committed `WhineLocation/Info.plist` with placeholder Fabric/Twitter keys and documented backend endpoint keys.
- Added `WhineLocation/ServiceKeys.xcconfig.example` for local credential setup.
- Switched first-party user, location, hometime, and beacon updates from GET to POST.
- Removed location, waiting, and pulse debug logging and guarded beacon/location casts in `CoreLocationController`.
- Guarded message read-state updates when Digits sessions or remote array data are unavailable.
- Added Digits user ID normalization so blank session IDs do not key message read-state storage.
- Added `make check` static baseline verification.
