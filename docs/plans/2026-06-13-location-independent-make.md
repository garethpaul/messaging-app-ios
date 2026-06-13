# Location-Independent Messaging iOS Verification

status: in progress

## Context

Absolute Makefile invocations resolve `scripts/check-baseline.py` relative to
the caller instead of the checkout, so every documented verification alias
fails outside the repository directory.

## Scope

1. Derive the checkout root from the loaded Makefile.
2. Invoke the static checker by an absolute repository path.
3. Add exact Makefile, completed-plan, external-run, and guidance contracts.
4. Preserve authentication, partner matching, pulse throttling, home-time
   submission, project metadata, workflow policy, and stacked artifacts.

## Verification Plan

- Run all four Make gates from the checkout and through an absolute Makefile
  path from a temporary directory.
- Run checker compilation, plist/XML/JSON/project parsing, and diff checks.
- Reject root derivation, checker invocation, plan status, plan evidence, and
  documentation mutations independently.
- Inspect intended paths, secret patterns, conflict markers, generated
  artifacts, and Objective-C/project/workflow changes before commit.

## Risk And Rollback

This changes verification path resolution only. Rollback restores the relative
checker recipe and removes its plan and documentation contracts.
