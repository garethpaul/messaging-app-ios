# AGENTS.md

## Repository purpose

`garethpaul/messaging-app-ios` is a legacy Swift iOS messaging and location
sample built around Digits identity, Parse-backed data, and partner pulses.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `Podfile` - CocoaPods dependency definition
- `WhineLocation.xcodeproj` - Xcode project
- `WhineLocation.xcworkspace` - Xcode workspace
- `Crashlytics.framework` - vendored legacy crash-reporting runtime
- `DigitsKit.framework` - vendored legacy phone-identity runtime
- `Fabric.framework` - vendored legacy Fabric runtime and installer
- `TwitterCore.framework` - vendored legacy Twitter authentication runtime
- `TwitterKit.framework` - vendored legacy Twitter integration runtime
- `WhineLocation` - application source, storyboards, assets, and metadata

## Development commands

- Install dependencies: `pod install`
- Full baseline: `make check`, which authenticates the isolated test runner
  before it runs pre/test/baseline/post validation.
- Local Apple development: `open WhineLocation.xcworkspace`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: C/C++ headers (118), Swift (27).
- Use the CocoaPods workspace when present; update `Podfile.lock` only with an intentional dependency change.
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test surfaces: `tests/test_check_baseline.py` is the active hosted static contract; `WhineLocationTests/WhineLocationTests.swift` is an orphaned legacy test source and is not wired to an Xcode test target.
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Hosted validation must keep `scripts/verify-validation-chain.py` ahead of
  `scripts/run-isolated-tests.py`; the runner is not trusted until that
  verifier has authenticated it. The hosted workflow must also keep the
  hardcoded `/usr/bin/shasum` digest check immediately before executing the
  verifier; changing that first command changes the workflow trust boundary.
- Repository Make targets reject preloaded or additional Makefiles and
  non-executing/error-ignoring modes. GNU Make may parse a caller-supplied
  preload before this repository can reject it, so only the documented
  single-`-f` invocation is inside the local Make trust boundary.
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
