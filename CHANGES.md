# Changes

## 2026-06-08

- Replaced committed Fabric/Crashlytics build-script values with `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` environment placeholders.
- Restored a committed `WhineLocation/Info.plist` with placeholder Fabric/Twitter keys and documented backend endpoint keys.
- Added `WhineLocation/ServiceKeys.xcconfig.example` for local credential setup.
- Switched first-party user, location, hometime, and beacon updates from GET to POST.
- Removed location, waiting, and pulse debug logging and guarded beacon/location casts in `CoreLocationController`.
- Guarded message read-state updates when Digits sessions or remote array data are unavailable.
- Added `make check` static baseline verification.
