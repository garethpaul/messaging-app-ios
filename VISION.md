## Messaging App iOS Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Messaging App iOS is a legacy iOS messaging app backed by Google App Engine and
using Fabric, TwitterKit, Digits, Parse, Alamofire, and location-related code.

The repository is useful as a preserved mobile messaging prototype with phone
login, messaging UI, backend integration, and older third-party SDKs. Project
context lives in [`README.md`](README.md).

The goal is to keep the prototype understandable while making credentials,
identity, message data, and location behavior explicit.

Current baseline: `make lint`, `make test`, `make build`, and `make check` run
`scripts/check-baseline.py` to verify legacy CocoaPods and
Digits/Fabric/Twitter framework wiring, Fabric/Crashlytics placeholder build
settings, `ServiceKeys.xcconfig.example`, placeholder-safe plist metadata,
`getInfo` fallback behavior, and message read-state guardrails.

The current focus is:

Priority:

- Preserve the messaging, login, and backend integration structure
- Keep Fabric/Twitter/Digits/Parse credential assumptions visible
- Keep `getInfo` safe when local plist endpoint configuration is absent
- Keep message read-state updates guarded around Digits sessions and remote data shape
- Keep Digits user ID normalization in front of message read-state storage
- Keep the Digits login success guard before partner flow and identity storage
- Keep the new partner user guard before partner flow backend requests
- Keep partner prefix preservation from erasing already-entered partner numbers
- Keep the location share user guard before posting location updates
- Keep the pulse send throttle from allowing repeat message posts during cooldown
- Keep the pulse send session guard before request, throttle, and UI mutation
- Keep one pulse refresh timer scoped to the visible controller lifecycle
- Keep the pulse list user guard before refreshing message list state
- Keep the home time submission guard behind normalized identity and successful
  backend responses
- Keep state-changing user, location, hometime, and beacon updates on POST
- Keep local lint, test, build, and check gates on the same static baseline
- Keep hosted project validation pinned, read-only, and credential-free on
  macOS through `WhineLocation.xcodeproj` parsing and `make check`
- Avoid committing real credentials, signing material, message data, or location data
- Maintain the CocoaPods workspace and legacy dependency context

Next priorities:

- Add setup details for backend configuration and local credentials
- Modernize deprecated SDKs only in a dedicated pass
- Add tests or manual checklists for login and message flows
- Document privacy expectations for messages, phone identity, and location

Contribution rules:

- One PR = one focused auth, messaging, backend, build, or documentation change.
- Verify app flow after SDK or storyboard changes.
- Keep credentials and generated signing files out of git.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  project, credential, backend URL, or `getInfo` changes.
- Document any change that stores or transmits messages or location data.
- Preserve message read-state guards when changing pulse/message flows.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Messages, phone identity, account sessions, and location signals are sensitive.
The app should avoid logging private content and keep all service credentials in
local or platform configuration. Fabric/Crashlytics values should be supplied
through local or CI build settings, not committed Xcode project literals.
Message read-state updates should keep guarded Digits session lookup, Digits
user ID normalization, and remote array parsing before posting state changes.
The Digits login success guard should prevent failed authentication callbacks
from opening identity-backed app flows.
The new partner user guard should keep partner requests tied to normalized
Digits identities and nonblank partner numbers.
Partner prefix preservation should avoid erasing partially entered partner phone
numbers when the field is focused again.
The location share user guard should keep location updates tied to normalized
Digits session identities.
The pulse send throttle should keep repeat taps from posting duplicate messages
while the message list refresh is pending.
The pulse list user guard should keep message list refreshes tied to normalized
Digits session identities and guarded response JSON.
The home time submission guard should keep home-time updates tied to normalized
Digits identities and only navigate after successful Alamofire responses.

## What We Will Not Merge (For Now)

- Hardcoded service credentials or signing material
- Message or location uploads beyond documented user-visible behavior
- Broad SDK migrations bundled with messaging behavior changes
- Private message fixtures or account data

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
