#!/usr/bin/env python3
from _hashlib import openssl_sha256
from pathlib import Path
import argparse
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SANITIZED_PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
VALIDATION_ROOT_PATH = "scripts/verify-validation-chain.py"
EXPECTED_HASHES = {
    "scripts/run-isolated-tests.py": "e084395a52183d222935ce66ce93ece97c71ba1255814d1d9fb999d3644814aa",
}


def sha256_file(path):
    return openssl_sha256(path.read_bytes()).hexdigest()


def validation_root_hash():
    return sha256_file(ROOT / VALIDATION_ROOT_PATH)


def hosted_validation_root_authentication():
    return (
        "/usr/bin/printf '%s  %s\\n' '" + validation_root_hash() +
        "' 'scripts/verify-validation-chain.py' | /usr/bin/shasum -a 256 -c -"
    )


def make_validation_root_authentication():
    return (
        "\t/usr/bin/printf '%s  %s\\n' '" + validation_root_hash() +
        "' \"$(ROOT)/scripts/verify-validation-chain.py\" | /usr/bin/shasum -a 256 -c -"
    )


def expected_makefile():
    return '''ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s\\n' "$$path" | sed 's/^ //'); dirname -- "$$path")

.PHONY: build check lint test

lint test build: check

check:
''' + make_validation_root_authentication() + '''
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/verify-validation-chain.py"
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/check-baseline.py"
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
'''


def expected_workflow():
    return """name: Check
on:
  pull_request:
  push:
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  baseline:
    runs-on: macos-15
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10
        with:
          persist-credentials: false
      - run: """ + hosted_validation_root_authentication() + """ && env -i HOME="$HOME" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I scripts/verify-validation-chain.py --require-clean
      - run: env -i HOME="$HOME" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I scripts/run-isolated-tests.py pre --require-clean --state /tmp/messaging-ios-integrity-state.json
      - run: env -i HOME="$HOME" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I scripts/run-isolated-tests.py test --require-clean --state /tmp/messaging-ios-integrity-state.json
      - run: env -i HOME="$HOME" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I scripts/check-baseline.py
      - run: env -i HOME="$HOME" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I scripts/run-isolated-tests.py post --require-clean --state /tmp/messaging-ios-integrity-state.json
"""


def git_status():
    return subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def parser():
    result = argparse.ArgumentParser()
    result.add_argument("--require-clean", action="store_true")
    return result


def main():
    arguments = parser().parse_args()
    failures = []
    if arguments.require_clean and git_status():
        failures.append("tracked tree must be clean")
    for relative_path, expected_hash in EXPECTED_HASHES.items():
        path = ROOT / relative_path
        if path.is_symlink() or not path.is_file():
            failures.append(relative_path + " must be a regular file")
        elif sha256_file(path) != expected_hash:
            failures.append(relative_path + " hash mismatch")
    expected_files = {
        ".github/workflows/check.yml": expected_workflow(),
        "Makefile": expected_makefile(),
    }
    for relative_path, expected_content in expected_files.items():
        path = ROOT / relative_path
        if path.is_symlink() or not path.is_file():
            failures.append(relative_path + " must be a regular file")
        elif path.read_text(encoding="utf-8", errors="replace") != expected_content:
            failures.append(relative_path + " contract mismatch")
    if failures:
        for failure in failures:
            print("validation-root: " + failure, file=sys.stderr)
        return 1
    print("Messaging app iOS validation chain authenticated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
