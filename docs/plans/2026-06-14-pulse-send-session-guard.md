# Pulse Send Session Guard

status: completed

## Context

Pulse list refresh already fails closed when no normalized Digits user exists,
but `sendMsg` dereferences the current session twice. A missing or expired
session can therefore crash before the throttle or request completes.

## Requirements

- Resolve one Digits session and normalized user ID before changing send state,
  button appearance, message text, or issuing the request.
- Return without side effects when the session or normalized user ID is absent.
- Reuse the resolved session phone number and user ID in the request.
- Preserve the existing one-second throttle, refresh, and button reset behavior.
- Add mutation-sensitive static contracts and matching documentation.

## Scope Boundaries

- Do not change backend endpoints, request payload names, Digits authentication,
  pulse throttling duration, dependencies, or unrelated legacy UI behavior.

## Verification

- Run all Make gates, external-directory validation, syntax/metadata checks,
  isolated hostile mutations, and exact diff/secret/artifact audits.

## Work Completed

- Resolved one Digits session and normalized user ID at the start of pulse
  sending, returning before any side effect when either is unavailable.
- Reused the guarded session phone number and normalized user ID in the request.
- Preserved the existing send throttle, text clearing, delayed refresh, and
  button reset behavior.
- Added ordering-sensitive static contracts and matching documentation.

## Verification Completed

- all four Make gates passed from the checkout and through the absolute
  Makefile path from `/tmp`; local Linux validation truthfully reported
  `xcodebuild` unavailable.
- Python checker compilation, maintained plist/XML/JSON/project parsing, and
  `git diff --check` passed.
- Six isolated hostile mutations were rejected for session lookup, normalized
  identity, guard ordering, request identity reuse, documentation, and
  completed plan evidence.
- The exact intended diff passed secret-pattern, conflict-marker,
  generated-artifact, binary, large-file, framework/Pod, and unrelated-path
  audits.
