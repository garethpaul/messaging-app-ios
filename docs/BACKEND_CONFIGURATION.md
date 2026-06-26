# Backend Configuration and Data Flow

This repository preserves a legacy messaging prototype. The tracked
`WhineLocation/Info.plist` uses `https://example.invalid` for every backend
route, so a clean checkout cannot contact the historical service by default.
Static maintenance with `make check` needs no service credentials or live
backend.

## Local Configuration

Create ignored local copies instead of putting real values in tracked files:

```bash
cp WhineLocation/Info.plist WhineLocation/Info.local.plist
cp WhineLocation/ServiceKeys.xcconfig.example \
  WhineLocation/ServiceKeys.local.xcconfig
```

Set the four Fabric/Twitter values in
`WhineLocation/ServiceKeys.local.xcconfig`, then add this build override:

```xcconfig
INFOPLIST_FILE = WhineLocation/Info.local.plist
```

Replace the nine `example.invalid` values in
`WhineLocation/Info.local.plist` with HTTPS routes for a backend you control.
The key names are listed below. Keep authentication or administrative secrets
on the server; a value embedded in an iOS app is not a server secret.

An explicit command-line build can apply both ignored files without changing
the tracked Xcode project:

```bash
xcodebuild \
  -project WhineLocation.xcodeproj \
  -target WhineLocation \
  -configuration Debug \
  -xcconfig WhineLocation/ServiceKeys.local.xcconfig \
  CODE_SIGNING_ALLOWED=NO \
  build
```

The project uses old Swift, CocoaPods, Fabric, TwitterKit, Digits, Parse, and
Alamofire artifacts. The configuration command does not make those retired or
legacy dependencies compatible with a current Xcode release. Use `make check`
for the maintained credential-free static baseline.

Do not commit `WhineLocation/Info.local.plist`,
`WhineLocation/ServiceKeys.local.xcconfig`, credentials, signing material,
phone identifiers, messages, coordinates, or backend responses. The existing
`.gitignore` excludes `*.local.plist` and `*.local.xcconfig`.

## Endpoint and Data Map

All requests use `POST`. The app does not attach a separate backend bearer
token in the checked-in implementation, so a revived service must authenticate
and authorize every request rather than trusting client-supplied identity.

| Plist key | Purpose | Client-supplied fields |
| --- | --- | --- |
| `userUrl` | Register the signed-in app user | bundle identifier, `phoneNumber`, normalized Digits user ID |
| `waitingUrl` | Check for a partner match | normalized user ID, signed-in phone number |
| `newpartnerUrl` | Submit a partner number | normalized user ID, partner phone number, signed-in phone number |
| `pulseListUrl` | Fetch pulse/message rows | normalized user ID |
| `pulseListSendUrl` | Send a pulse/message | normalized user ID, signed-in phone number, message text |
| `pulseListReadUrl` | Publish message read state | normalized user ID, read-state identifiers as a JSON array |
| `locationUrl` | Share the latest location | normalized user ID, latitude and longitude strings |
| `beaconUrl` | Report a changed ranged-beacon proximity | beacon region identifier, normalized user ID |
| `newHometimeUrl` | Submit home time | normalized user ID, formatted home-time string |

## Privacy Expectations

- Treat phone numbers and Digits user IDs as account identifiers. Do not log
  them, expose them in URLs, or use them as authorization proof by themselves.
- Treat message text and read-state identifiers as private communications
  metadata. Enforce participant authorization and avoid retaining more than the
  messaging flow requires.
- Treat latitude and longitude as precise location data. Send them only after
  user-granted location permission and an explicit product decision to share.
- Treat beacon reports and home time as behavioral/location signals even when
  they do not contain coordinates.
- Use HTTPS, validate server responses, bound request and response sizes, and
  define deletion and retention behavior before reviving a backend.
- Keep tests and CI on placeholder endpoints; live-account or live-location
  traffic is not part of the repository verification baseline.

## Manual Flow Boundary

A credentialed revival should verify login success and failure, partner entry,
waiting, message list and send, read-state updates, home-time submission,
location permission grant and denial, and beacon behavior. Record the exact app
commit, backend revision, test account policy, and data cleanup performed.
