## Messaging App iOS Vision

Messaging App iOS is a legacy iOS messaging app backed by Google App Engine and
using Fabric, TwitterKit, Digits, Parse, Alamofire, and location-related code.

The repository is useful as a preserved mobile messaging prototype with phone
login, messaging UI, backend integration, and older third-party SDKs. Project
context lives in [`README.md`](README.md).

The goal is to keep the prototype understandable while making credentials,
identity, message data, and location behavior explicit.

The current focus is:

Priority:

- Preserve the messaging, login, and backend integration structure
- Keep Fabric/Twitter/Digits/Parse credential assumptions visible
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
- Document any change that stores or transmits messages or location data.

## Security And Privacy

Messages, phone identity, account sessions, and location signals are sensitive.
The app should avoid logging private content and keep all service credentials in
local or platform configuration.

## What We Will Not Merge For Now

- Hardcoded service credentials or signing material
- Message or location uploads beyond documented user-visible behavior
- Broad SDK migrations bundled with messaging behavior changes
- Private message fixtures or account data
