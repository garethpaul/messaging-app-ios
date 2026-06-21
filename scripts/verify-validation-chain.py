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
    "scripts/run-isolated-tests.py": "9980b0a71fabedab5677bcd7a1b92a98283bbb793111c2c20ee668f873642bae",
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
    return '''.PHONY: __repository-make-authority build check lint test
.SECONDEXPANSION:

override SHELL := /bin/sh
override .SHELLFLAGS := -c
ifneq ($(origin -*-eval-flags-*-),undefined)
$(error --eval must not be used for repository verification)
endif
ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell sed_path=/usr/bin/sed; [ -x "$$sed_path" ] || sed_path=/bin/sed; [ -x "$$sed_path" ] || exit 1; path=$$(/usr/bin/printf '%s' '$(subst ','"'"',$(value MAKEFILE_LIST))' | "$$sed_path" 's/^ //'); [ -f "$$path" ] || exit 1; directory=$${path%/*}; [ "$$directory" != "$$path" ] || directory=.; CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif

build check lint test:: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check lint test:: $$(if $$(shell sed_path=/usr/bin/sed && [ -x "$$$$sed_path" ] || sed_path=/bin/sed && [ -x "$$$$sed_path" ] && path=$$$$(printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | "$$$$sed_path" 's/^ //') && [ -f "$$$$path" ] && printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check lint test:: __repository-make-authority

__repository-make-authority::
\t@:

lint:: check
test:: check
build:: check

check::
''' + make_validation_root_authentication() + '''
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/verify-validation-chain.py"
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/check-baseline.py"
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
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
      - run: """ + hosted_validation_root_authentication() + """ && /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/verify-validation-chain.py --require-clean
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/run-isolated-tests.py pre --require-clean --state /tmp/messaging-ios-integrity-state.json
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/run-isolated-tests.py test --require-clean --state /tmp/messaging-ios-integrity-state.json
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/check-baseline.py
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/run-isolated-tests.py post --require-clean --state /tmp/messaging-ios-integrity-state.json
"""


def git_status():
    return subprocess.run(
        ["/usr/bin/git", "status", "--porcelain=v1", "--untracked-files=all"],
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
