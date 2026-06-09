# Changes

## 2026-06-09

- Added a Digits login success guard so failed authentication callbacks do not
  open the partner flow or store identity.

## 2026-06-08

- Replaced committed Fabric/Crashlytics build-script values with `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` environment placeholders.
- Restored a committed `WhineLocation/Info.plist` with placeholder Fabric/Twitter keys and documented backend endpoint keys.
- Added `WhineLocation/ServiceKeys.xcconfig.example` for local credential setup.
- Switched first-party user, location, hometime, and beacon updates from GET to POST.
- Removed location, waiting, and pulse debug logging and guarded beacon/location casts in `CoreLocationController`.
- Guarded message read-state updates when Digits sessions or remote array data are unavailable.
- Added Digits user ID normalization so blank session IDs do not key message read-state storage.
- Added `make check` static baseline verification.
