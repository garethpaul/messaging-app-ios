#!/usr/bin/env python3
from _hashlib import openssl_sha256
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = Path(tempfile.gettempdir()) / "messaging-ios-integrity-state.json"
SANITIZED_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
GIT = "/usr/bin/git"
VALIDATION_ROOT_PATH = "scripts/verify-validation-chain.py"
EXPECTED_TEST_FILES = ["tests/test_check_baseline.py"]
EXPECTED_TEST_HASHES = {
    "tests/test_check_baseline.py": "003d848589fe69a40967ad6babcb39abbe3fa5c149110b245c29946a45d7886d",
}
EXPECTED_PROTECTED_HASHES = {
    "scripts/check-baseline.py":
        "3b5ff2be3222459ff7ffc6678cd23a63cdd0ed219dac0994204018414a323e3b",
    "WhineLocation/HomeTimeViewController.swift":
        "cd5ebd6aa378c470a08069a2fd574122d7819bc39d52f429c33740503f75591c",
    "WhineLocation/Base.lproj/Main.storyboard":
        "a621749ce902822ff3b7cda43b33619b815b22efdb25bac35fa30677b845bfb5",
    "WhineLocation.xcodeproj/project.pbxproj":
        "ea729e7bd458396bfa8d32dfef24c22747f6d89c440b4266f35da54194db3244",
    "WhineLocation.xcodeproj/project.xcworkspace/contents.xcworkspacedata":
        "2e227e22f3c5f01d6ffeeefdea778b54eb534d8f5c7f8b79a11a1598133bc8d9",
    "WhineLocation.xcworkspace/contents.xcworkspacedata":
        "c81e4a8c14e87e445f0c8a056af182b7d6923df91ef3a4ea0f9ee7a48e164441",
    "WhineLocation/ServiceKeys.xcconfig.example":
        "b05a5fe96d1c70f7d34b1f2ff615fa7675284476620191cb4af157850571a741",
}
EXPECTED_INTERFACE_FILES = [
    "WhineLocation/Base.lproj/LaunchScreen.xib",
    "WhineLocation/Base.lproj/Main.storyboard",
    "WhineLocation/DirectMessageCell.xib",
    "WhineLocation/PulseTableCell.xib",
    "WhineLocation/ReceivedMessage.xib",
]
EXPECTED_XCODE_GRAPH_FILES = [
    "WhineLocation.xcodeproj/project.pbxproj",
    "WhineLocation.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
    "WhineLocation.xcworkspace/contents.xcworkspacedata",
    "WhineLocation/ServiceKeys.xcconfig.example",
]


def sha256_bytes(value):
    return openssl_sha256(value).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


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

build check lint test: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check lint test: $$(if $$(shell sed_path=/usr/bin/sed && [ -x "$$$$sed_path" ] || sed_path=/bin/sed && [ -x "$$$$sed_path" ] && path=$$$$(printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | "$$$$sed_path" 's/^ //') && [ -f "$$$$path" ] && printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check lint test: __repository-make-authority

__repository-make-authority::
\t@:

lint test build: check

check:
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


def git_output(*arguments):
    return subprocess.run(
        [GIT, *arguments],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def candidate_files():
    return sorted(
        path for path in git_output(
            "ls-files", "--cached", "--others", "--exclude-standard"
        ).splitlines()
        if path and not path.endswith(".pyc") and "/__pycache__/" not in path
    )


def tree_fingerprint():
    entries = []
    for relative_path in candidate_files():
        path = ROOT / relative_path
        if path.is_symlink():
            entries.append([relative_path, "symlink", os.readlink(path)])
        elif path.is_file():
            entries.append([relative_path, "file", sha256_file(path)])
        else:
            entries.append([relative_path, "other", ""])
    return {
        "entries": entries,
        "status": git_output("status", "--porcelain=v1", "--untracked-files=all"),
    }


def matching_files(root, suffixes):
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in root.rglob("*")
        if path.suffix.lower() in suffixes
    )


def integrity_failures(require_clean=False):
    failures = []
    for relative_path, expected_hash in EXPECTED_PROTECTED_HASHES.items():
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
    test_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tests").rglob("*")
        if (path.is_file() or path.is_symlink())
        and not path.name.endswith(".pyc")
        and path.parent.name != "__pycache__"
    )
    if test_files != EXPECTED_TEST_FILES:
        failures.append("test inventory mismatch")
    for relative_path, expected_hash in EXPECTED_TEST_HASHES.items():
        path = ROOT / relative_path
        if path.is_symlink() or not path.is_file():
            failures.append(relative_path + " must be a regular file")
        elif sha256_file(path) != expected_hash:
            failures.append(relative_path + " hash mismatch")
    if matching_files(ROOT / "WhineLocation", {".storyboard", ".xib"}) != EXPECTED_INTERFACE_FILES:
        failures.append("interface inventory mismatch")
    graph_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and (
            ".xcodeproj/" in path.as_posix()
            or ".xcworkspace/" in path.as_posix()
            or path.name.lower().endswith(".xcconfig")
            or path.name.lower().endswith(".xcconfig.example")
        )
    )
    if graph_files != EXPECTED_XCODE_GRAPH_FILES:
        failures.append("Xcode graph inventory mismatch")
    if require_clean and git_output("status", "--porcelain=v1", "--untracked-files=all"):
        failures.append("tracked tree must be clean")
    return failures


def sanitized_environment(home):
    return {
        "HOME": str(home),
        "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def copy_candidate_tree(destination):
    for relative_path in candidate_files():
        source = ROOT / relative_path
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        elif source.is_file():
            shutil.copy2(source, target)


def run_copied_tests():
    with tempfile.TemporaryDirectory(prefix="messaging-ios-tests-") as temporary:
        temporary_root = Path(temporary)
        repository_copy = temporary_root / "repository"
        repository_copy.mkdir()
        copy_candidate_tree(repository_copy)
        subprocess.run([GIT, "init", "--quiet"], cwd=repository_copy, check=True)
        subprocess.run([GIT, "add", "--all"], cwd=repository_copy, check=True)
        subprocess.run(
            [GIT, "-c", "user.name=validation", "-c", "user.email=validation@example.invalid", "commit", "--quiet", "-m", "snapshot"],
            cwd=repository_copy,
            check=True,
        )
        return subprocess.run(
            [sys.executable, "-I", "tests/test_check_baseline.py", "-v"],
            cwd=repository_copy,
            env=sanitized_environment(temporary_root),
        ).returncode


def parser():
    result = argparse.ArgumentParser()
    result.add_argument("mode", choices=["pre", "test", "post"])
    result.add_argument("--require-clean", action="store_true")
    result.add_argument("--state", type=Path, default=DEFAULT_STATE)
    return result


def main():
    arguments = parser().parse_args()
    failures = integrity_failures(arguments.require_clean)
    if failures:
        for failure in failures:
            print("integrity: " + failure, file=sys.stderr)
        return 1
    if arguments.mode == "pre":
        arguments.state.write_text(json.dumps(tree_fingerprint(), sort_keys=True), encoding="utf-8")
    elif arguments.mode == "test":
        return run_copied_tests()
    else:
        if not arguments.state.is_file():
            print("integrity: preflight state missing", file=sys.stderr)
            return 1
        expected = json.loads(arguments.state.read_text(encoding="utf-8"))
        if tree_fingerprint() != expected:
            print("integrity: candidate tree changed during validation", file=sys.stderr)
            return 1
        arguments.state.unlink()
    print("Messaging app iOS integrity " + arguments.mode + " passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
