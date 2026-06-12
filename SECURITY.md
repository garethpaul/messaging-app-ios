# Security Policy

## Supported Versions

The supported security scope for `messaging-app-ios` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: An iOS Messaging App 

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/messaging-app-ios` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be an Apple platform application or Swift sample. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: Podfile, Podfile.lock. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- Run `make lint`, `make test`, `make build`, and `make check` after changing Xcode project metadata, `Info.plist` handling, Fabric/Crashlytics setup, backend URLs, Swift sources, Podfile metadata, or security docs.
- Fabric, TwitterKit, Digits, and Crashlytics are legacy SDKs in this preserved
  prototype; treat SDK migration or replacement as security-sensitive work.
- The pinned macOS GitHub Actions workflow only parses project metadata and static resources;
  it does not install pods, receive service credentials, authenticate users,
  contact backends, share location, process messages, build or sign the app, or
  launch a simulator.
- `WhineLocation/Info.plist` should stay tracked with placeholder-safe metadata and privacy usage descriptions.
- Fabric API keys, Crashlytics build secrets, Parse credentials, signing material, phone identity data, messages, and location data should stay out of git.
- Use `WhineLocation/ServiceKeys.xcconfig.example` as a placeholder template for local service credentials.
- Plist-backed endpoint lookup through `getInfo` should fail closed instead of force-unwrapping missing local configuration.
- Message read-state updates should guard Digits session lookup and remote array parsing before posting changes.
- Digits user ID normalization should reject blank session IDs before local message read-state storage changes.
- The Digits login success guard should prevent failed authentication callbacks from storing identity or opening the partner flow.
- The new partner user guard should require a normalized Digits user ID and nonblank partner number before posting partner requests.
- Partner prefix preservation should not erase a partially entered partner number when the partner field is focused again.
- The location share user guard should require a normalized Digits user ID before posting location coordinates.
- The pulse send throttle should mark message sends unavailable during cooldown so repeat taps cannot post duplicate messages.
- The pulse list user guard should require a normalized Digits user ID and
  guarded response JSON before refreshing message list state.
- The home time submission guard should require a normalized Digits user ID
  before posting and should not present failed requests as successful updates.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

For this app, reports involving pulse/message read-state behavior should state
whether malformed remote data or missing Digits sessions can expose or corrupt
message state. Include whether Digits user ID normalization can be bypassed with
blank or whitespace-only session IDs.
Reports involving login should state whether the Digits login success guard can
be bypassed after failed authentication.
Reports involving partner requests should state whether the new partner user
guard can be bypassed with missing Digits sessions or blank partner numbers.
Reports involving partner prefix preservation should state whether focus changes
can erase already-entered partner numbers before submission.
Reports involving location sharing should state whether the location share user
guard can be bypassed with missing or blank Digits session IDs.
Reports involving pulse sends should state whether the pulse send throttle can
be bypassed with rapid taps while a message refresh is pending.
Reports involving pulse list refreshes should state whether the pulse list user
guard can be bypassed with missing Digits sessions or malformed response JSON.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
