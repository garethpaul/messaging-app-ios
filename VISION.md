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

Current baseline: `make check` runs `scripts/check-baseline.py` to verify
legacy CocoaPods and Digits/Fabric/Twitter framework wiring, Fabric/Crashlytics
placeholder build settings, `ServiceKeys.xcconfig.example`,
placeholder-safe plist metadata, `getInfo` fallback behavior, and message
read-state guardrails.

The current focus is:

Priority:

- Preserve the messaging, login, and backend integration structure
- Keep Fabric/Twitter/Digits/Parse credential assumptions visible
- Keep `getInfo` safe when local plist endpoint configuration is absent
- Keep message read-state updates guarded around Digits sessions and remote data shape
- Keep Digits user ID normalization in front of message read-state storage
- Keep state-changing user, location, hometime, and beacon updates on POST
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
- Run `make check` before pushing project, credential, backend URL, or `getInfo` changes.
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

## What We Will Not Merge (For Now)

- Hardcoded service credentials or signing material
- Message or location uploads beyond documented user-visible behavior
- Broad SDK migrations bundled with messaging behavior changes
- Private message fixtures or account data

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
