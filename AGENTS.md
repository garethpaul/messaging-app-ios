# AGENTS.md

## Repository purpose

`garethpaul/messaging-app-ios` is an Apple platform application or Swift sample. An iOS Messaging App

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `Podfile` - CocoaPods dependency definition
- `WhineLocation.xcodeproj` - Xcode project
- `WhineLocation.xcworkspace` - Xcode workspace
- `Crashlytics.framework` - repository source or sample assets
- `DigitsKit.framework` - repository source or sample assets
- `Fabric.framework` - repository source or sample assets
- `TwitterCore.framework` - repository source or sample assets
- `TwitterKit.framework` - repository source or sample assets
- `WhineLocation` - repository source or sample assets

## Development commands

- Install dependencies: `pod install`
- Full baseline: `make check`
- Local Apple development: `open WhineLocation.xcworkspace`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: C/C++ headers (118), Swift (27).
- Use the CocoaPods workspace when present; update `Podfile.lock` only with an intentional dependency change.
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `WhineLocationTests/WhineLocationTests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Detected references to Twitter. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.
- Keep `WhineLocation/Info.plist` tracked with placeholder-safe metadata and privacy usage descriptions.
- Do not commit Fabric API keys, Crashlytics build secrets, Parse credentials, signing material, message fixtures, phone identity data, or location data.
- Message read-state changes should preserve guarded Digits session lookup and array casts.
- Digits user ID normalization should continue to reject blank session IDs before writing local read-state data.
- The Digits login success guard should keep failed authentication callbacks from storing identity or opening the partner flow.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
