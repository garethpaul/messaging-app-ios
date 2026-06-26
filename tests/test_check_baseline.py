import contextlib
from _hashlib import openssl_sha256
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPOSITORY_ROOT / "scripts/check-baseline.py"
RUNNER_PATH = REPOSITORY_ROOT / "scripts/run-isolated-tests.py"
SANITIZED_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
VALIDATION_ROOT_PATH = "scripts/verify-validation-chain.py"
REQUEST = (
    'let request = Alamofire.request(.POST, getInfo("newHometimeUrl"), '
    'parameters: ["userId": userId, "homeTime": dateString])'
)
PARAMETERLESS_VALIDATED_RESPONSE = REQUEST + ".validate()"
STATUS_VALIDATED_RESPONSE = REQUEST + ".validate(statusCode: 200..<300)"
UNVALIDATED_RESPONSE = REQUEST
PARTNER_REQUEST = (
    'let request = Alamofire.request(.POST, getInfo("newpartnerUrl"), '
    'parameters: ["userId": userId, "partner": partner, "userPhoneNumber": userPhoneNumber])'
)
PARTNER_VALIDATED_REQUEST = PARTNER_REQUEST + ".validate(statusCode: 200..<300)"
PULSE_LIST_REQUEST = (
    'let request = Alamofire.request(.POST, getInfo("pulseListUrl"), '
    'parameters: ["userId": userId])'
)
PULSE_LIST_VALIDATED_REQUEST = PULSE_LIST_REQUEST + ".validate(statusCode: 200..<300)"
PULSE_SEND_REQUEST = (
    'let request = Alamofire.request(.POST, getInfo("pulseListSendUrl"), '
    'parameters: ["userId": userId, "phoneNumber": digitsSession.phoneNumber, "msg": self.textField.text])'
)
PULSE_SEND_VALIDATED_REQUEST = PULSE_SEND_REQUEST + ".validate(statusCode: 200..<300)"
WAITING_REQUEST = (
    'let request = Alamofire.request(.POST, getInfo("waitingUrl"), '
    'parameters: ["userId": userId, "phoneNumber": digitsSession.phoneNumber])'
)
WAITING_VALIDATED_REQUEST = WAITING_REQUEST + ".validate(statusCode: 200..<300)"
BEACON_REQUEST = (
    'Alamofire.request(.POST, getInfo("beaconUrl"), '
    'parameters: ["beacon": region.identifier, "userId": userId])'
)
PROTECTED_HASHES = {
    "WhineLocation/HomeTimeViewController.swift":
        "0d4410f43629b517b0fa7b0801b728ebeb33d23e046c6791827b63ea31a3f594",
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
INTERFACE_INVENTORY = [
    "WhineLocation/Base.lproj/LaunchScreen.xib",
    "WhineLocation/Base.lproj/Main.storyboard",
    "WhineLocation/DirectMessageCell.xib",
    "WhineLocation/PulseTableCell.xib",
    "WhineLocation/ReceivedMessage.xib",
]
XCODE_GRAPH_INVENTORY = [
    "WhineLocation.xcodeproj/project.pbxproj",
    "WhineLocation.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
    "WhineLocation.xcworkspace/contents.xcworkspacedata",
    "WhineLocation/ServiceKeys.xcconfig.example",
]
def sha256_file(path):
    return openssl_sha256(path.read_bytes()).hexdigest()


def make_preserves_literal_makefile_list(make_binary="make"):
    result = subprocess.run(
        [make_binary, "--version"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0 or not result.stdout.startswith("GNU Make "):
        return False
    version = result.stdout.splitlines()[0].split()[-1]
    try:
        major, minor = (int(part) for part in version.split(".", 2)[:2])
    except (TypeError, ValueError):
        return False
    return (major, minor) >= (4, 3)


def validation_root_hash(root):
    return sha256_file(root / VALIDATION_ROOT_PATH)


def hosted_validation_root_authentication(root):
    return (
        "/usr/bin/printf '%s  %s\\n' '" + validation_root_hash(root) +
        "' 'scripts/verify-validation-chain.py' | /usr/bin/shasum -a 256 -c -"
    )


def make_validation_root_authentication(root):
    return (
        "\t/usr/bin/printf '%s  %s\\n' '" + validation_root_hash(root) +
        "' \"$(ROOT)/scripts/verify-validation-chain.py\" | /usr/bin/shasum -a 256 -c -"
    )


def expected_makefile(root):
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
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
override REPOSITORY_MAKE_BRACE := {
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value MAKEFILE_LIST)),)
$(error repository Makefile path must not contain Make syntax)
endif
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_BRACE),$(value MAKEFILE_LIST)),)
$(error repository Makefile path must not contain Make syntax)
endif
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
''' + make_validation_root_authentication(root) + '''
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/verify-validation-chain.py"
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/check-baseline.py"
\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
'''


def expected_workflow(root):
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
      - run: """ + hosted_validation_root_authentication(root) + """ && /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/verify-validation-chain.py --require-clean
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/run-isolated-tests.py pre --require-clean --state /tmp/messaging-ios-integrity-state.json
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/run-isolated-tests.py test --require-clean --state /tmp/messaging-ios-integrity-state.json
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/check-baseline.py
      - run: /usr/bin/env -i HOME="$HOME" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I scripts/run-isolated-tests.py post --require-clean --state /tmp/messaging-ios-integrity-state.json
"""


EXPECTED_MAKEFILE = expected_makefile(REPOSITORY_ROOT)
CANONICAL_SEND_TIME_METHOD = '''    @IBAction func sendTime(sender: AnyObject) {
        homeTimeRequest?.cancel()
        homeTimeRequest = nil

        guard isHomeTimeViewActive else {
            return
        }

        guard let userId = currentDigitsUserID() else {
            return
        }

        let requestGeneration = homeTimeViewGeneration

        let dateFormatter = NSDateFormatter()
        dateFormatter.dateFormat = "hh:mm a" //format style. Browse online to get a format that fits your needs.
        let dateString = dateFormatter.stringFromDate(uiPicker.date)

        let request = Alamofire.request(.POST, getInfo("newHometimeUrl"), parameters: ["userId": userId, "homeTime": dateString]).validate(statusCode: 200..<300)
        homeTimeRequest = request
        request.responseJSON { (req, res, json, error) in
            dispatch_async(dispatch_get_main_queue()) {
                guard self.homeTimeRequest === request else {
                    return
                }

                self.homeTimeRequest = nil
                guard self.isHomeTimeViewActive &&
                    requestGeneration == self.homeTimeViewGeneration else {
                        return
                }

                guard error == nil else {
                    return
                }

                self.performSegueWithIdentifier("presentNav", sender: self)
            }
        }
    }
'''


def load_checker():
    specification = importlib.util.spec_from_file_location(
        "messaging_app_ios_check_baseline",
        CHECKER_PATH,
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load_runner():
    specification = importlib.util.spec_from_file_location(
        "messaging_app_ios_run_isolated_tests",
        RUNNER_PATH,
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


CHECKER = load_checker()
RUNNER = load_runner()


class MakeCapabilityTests(unittest.TestCase):
    def test_literal_makefile_list_requires_gnu_make_4_3(self):
        versions = {
            "GNU Make 3.81\n": False,
            "GNU Make 4.2.1\n": False,
            "GNU Make 4.3\n": True,
            "GNU Make 4.4.1\n": True,
            "BSD make 20240101\n": False,
        }
        for output, expected in versions.items():
            with self.subTest(output=output):
                completed = subprocess.CompletedProcess(
                    ["make", "--version"], 0, output, ""
                )
                with mock.patch.object(subprocess, "run", return_value=completed):
                    self.assertEqual(expected, make_preserves_literal_makefile_list())


class XcodebuildProbeContractTests(unittest.TestCase):
    def test_checker_bounds_xcodebuild_project_parse_probe(self):
        original_run = CHECKER.subprocess.run
        xcodebuild_calls = []

        def bounded_xcodebuild(command, *arguments, **keywords):
            if command == [
                "/usr/bin/xcodebuild", "-list", "-project", "WhineLocation.xcodeproj",
            ]:
                xcodebuild_calls.append(keywords)
                if "timeout" in keywords:
                    raise subprocess.TimeoutExpired(
                        command,
                        keywords["timeout"],
                        stderr="hung xcodebuild",
                    )
                return subprocess.CompletedProcess(command, 0, "", "")
            return original_run(command, *arguments, **keywords)

        failures = []
        with mock.patch.object(CHECKER.Path, "is_file", return_value=True):
            with mock.patch.object(
                CHECKER.subprocess,
                "run",
                side_effect=bounded_xcodebuild,
            ):
                CHECKER.check_xcodebuild_project(failures)

        self.assertTrue(xcodebuild_calls)
        self.assertIn("timeout", xcodebuild_calls[0])
        self.assertEqual(1, len(failures))
        self.assertIn(
            "xcodebuild timed out parsing WhineLocation.xcodeproj",
            failures[0],
        )


def send_time_method(source):
    start_marker = "    @IBAction func sendTime(sender: AnyObject) {"
    end_marker = "    override func prepareForSegue"
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end].rstrip() + "\n"


def normalized_method(source):
    return "\n".join(line.rstrip() for line in source.splitlines()) + "\n"


class HomeTimeValidationContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.snapshot_root = Path(self.temporary_directory.name)
        tracked_paths = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=REPOSITORY_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.splitlines()
        for relative_path in tracked_paths:
            source = REPOSITORY_ROOT / relative_path
            destination = self.snapshot_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        subprocess.run(["git", "init", "--quiet"], cwd=self.snapshot_root, check=True)
        subprocess.run(
            ["git", "config", "gc.auto", "0"],
            cwd=self.snapshot_root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "maintenance.auto", "false"],
            cwd=self.snapshot_root,
            check=True,
        )
        subprocess.run(["git", "add", "--all"], cwd=self.snapshot_root, check=True)
        subprocess.run(
            [
                "git", "-c", "user.name=validation",
                "-c", "user.email=validation@example.invalid",
                "commit", "--quiet", "-m", "snapshot",
            ],
            cwd=self.snapshot_root,
            check=True,
        )
        source_path = self.home_time_source()
        source = source_path.read_text(encoding="utf-8")
        self.assertEqual(
            CANONICAL_SEND_TIME_METHOD,
            normalized_method(send_time_method(source)),
        )
        self.assertNotIn(PARAMETERLESS_VALIDATED_RESPONSE, source)

    def tearDown(self):
        for attempt in range(20):
            try:
                self.temporary_directory.cleanup()
                return
            except OSError:
                if attempt == 19:
                    raise
                time.sleep(0.05)

    def test_makefile_preserves_spaced_quoted_checkout_root(self):
        external = self.snapshot_root / "external caller"
        checkout = self.snapshot_root / "checkout with spaces 'quoted' [hostile]"
        checkout.mkdir()
        external.mkdir()
        (checkout / "Makefile").write_text(EXPECTED_MAKEFILE, encoding="utf-8")

        for extra_arguments in ((), ("ROOT=/tmp/untrusted",), ("-e", "ROOT=/tmp/untrusted")):
            with self.subTest(extra_arguments=extra_arguments):
                result = subprocess.run(
                    ["make", "-f", str(checkout / "Makefile"),
                     *extra_arguments, "__repository-make-authority"],
                    cwd=external,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(0, result.returncode, result.stderr)

    def test_makefile_literal_dollar_parentheses_path_fails_closed(self):
        if not make_preserves_literal_makefile_list():
            self.skipTest("GNU Make 4.3+ is required to inspect literal Makefile path syntax")

        external = self.snapshot_root / "external caller"
        marker = external / "make-path-executed"
        checkout = self.snapshot_root / "checkout $(shell touch make-path-executed)"
        checkout.mkdir()
        external.mkdir()
        (checkout / "Makefile").write_text(EXPECTED_MAKEFILE, encoding="utf-8")

        result = subprocess.run(
            ["make", "-f", str(checkout / "Makefile"), "check"],
            cwd=external,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("repository Makefile path must not contain Make syntax", result.stderr)
        self.assertFalse(marker.exists())

    def test_makefile_literal_dollar_brace_path_fails_closed(self):
        if not make_preserves_literal_makefile_list():
            self.skipTest("GNU Make 4.3+ is required to inspect literal Makefile path syntax")

        external = self.snapshot_root / "external brace caller"
        checkout = self.snapshot_root / "checkout ${untrusted-make-variable}"
        checkout.mkdir()
        external.mkdir()
        (checkout / "Makefile").write_text(EXPECTED_MAKEFILE, encoding="utf-8")

        result = subprocess.run(
            ["make", "-f", str(checkout / "Makefile"), "check"],
            cwd=external,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("repository Makefile path must not contain Make syntax", result.stderr)

    def test_makefile_rejects_additional_makefiles_before_and_after(self):
        marker = self.snapshot_root / "extra-makefile-executed"
        extra = self.snapshot_root / "extra.mk"
        extra.write_text(
            "check:\n\t@/usr/bin/touch " + str(marker) + "\n",
            encoding="utf-8",
        )
        makefile = self.snapshot_root / "Makefile"

        for files in ((extra, makefile), (makefile, extra)):
            for target in ("check", "lint", "test", "build"):
                marker.unlink(missing_ok=True)
                with self.subTest(files=files, target=target):
                    command = ["make"]
                    for path in files:
                        command.extend(["-f", str(path)])
                    command.append(target)
                    result = subprocess.run(
                        command,
                        cwd=self.snapshot_root,
                        check=False,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    self.assertNotEqual(0, result.returncode)
                    self.assertTrue(
                        "repository Makefile" in result.stderr
                        or "has both : and :: entries" in result.stderr,
                        result.stderr,
                    )
                    self.assertFalse(marker.exists())

    def test_makefile_rejects_later_target_specific_recipe_replacement(self):
        marker = self.snapshot_root / "later-recipe-executed"
        later = self.snapshot_root / "later-target-specific.mk"
        later.write_text(
            "build check lint test: MAKEFILE_LIST := " + str(self.snapshot_root / "Makefile") + "\n"
            "build check lint test:\n"
            "\t@/bin/echo '$@' >> '" + str(marker) + "'\n",
            encoding="utf-8",
        )
        makefile = self.snapshot_root / "Makefile"
        make_binaries = ["make"]
        gnu_make_43 = Path(
            "/var/folders/xw/s4g4vjcd18j8bd9lr4__0k7r0000gn/T/"
            "gnu-make-4.3.tyZ3BS/install/bin/make"
        )
        if gnu_make_43.exists():
            make_binaries.append(str(gnu_make_43))

        for make_binary in make_binaries:
            for target in ("check", "lint", "test", "build"):
                marker.unlink(missing_ok=True)
                with self.subTest(make_binary=make_binary, target=target):
                    result = subprocess.run(
                        [make_binary, "-f", str(makefile), "-f", str(later), target],
                        cwd=self.snapshot_root,
                        check=False,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("has both : and :: entries", result.stderr)
                    self.assertFalse(marker.exists())

    def test_makefile_rejects_preloads_and_nonexecuting_modes(self):
        preload = self.snapshot_root / "preload.mk"
        preload.write_text("PRELOADED := 1\n", encoding="utf-8")
        makefile = self.snapshot_root / "Makefile"
        attacks = [
            (["make", "-f", str(makefile), "MAKEFLAGS=", "check"], None),
            (["make", "-n", "-f", str(makefile), "check"], None),
            (["make", "-t", "-f", str(makefile), "check"], None),
            (["make", "-q", "-f", str(makefile), "check"], None),
            (["make", "-i", "-f", str(makefile), "check"], None),
            (["make", "-f", str(makefile), "check"], {**os.environ, "MAKEFLAGS": "-n"}),
            (["make", "-f", str(makefile), "check"], {**os.environ, "MAKEFILES": str(preload)}),
        ]
        for command, environment in attacks:
            with self.subTest(command=command, environment=environment):
                result = subprocess.run(
                    command,
                    cwd=self.snapshot_root,
                    env=environment,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertNotEqual(0, result.returncode)

    def test_makefile_rejects_eval_before_target_specific_shell_execution(self):
        gnu_make_43 = Path(
            "/var/folders/xw/s4g4vjcd18j8bd9lr4__0k7r0000gn/T/"
            "gnu-make-4.3.tyZ3BS/install/bin/make"
        )
        if not gnu_make_43.exists():
            self.skipTest("GNU Make with --eval support is unavailable")

        marker = self.snapshot_root / "target-specific-shell-executed"
        hostile_shell = self.snapshot_root / "hostile-shell"
        hostile_shell.write_text(
            "#!/bin/sh\n/usr/bin/touch " + str(marker) + "\nexit 97\n",
            encoding="utf-8",
        )
        hostile_shell.chmod(0o755)

        result = subprocess.run(
            [
                str(gnu_make_43),
                "--eval=check: override SHELL := " + str(hostile_shell),
                "-f", str(self.snapshot_root / "Makefile"),
                "check",
            ],
            cwd=self.snapshot_root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("--eval must not be used", result.stderr)
        self.assertFalse(marker.exists())

    def test_makefile_rejects_eval_before_target_specific_root_redirection(self):
        gnu_make_43 = Path(
            "/var/folders/xw/s4g4vjcd18j8bd9lr4__0k7r0000gn/T/"
            "gnu-make-4.3.tyZ3BS/install/bin/make"
        )
        if not gnu_make_43.exists():
            self.skipTest("GNU Make with --eval support is unavailable")

        decoy_root = self.snapshot_root / "decoy-root"
        (decoy_root / "scripts").mkdir(parents=True)
        shutil.copy2(
            self.snapshot_root / "scripts/verify-validation-chain.py",
            decoy_root / "scripts/verify-validation-chain.py",
        )

        result = subprocess.run(
            [
                str(gnu_make_43),
                "--eval=check: override ROOT := " + str(decoy_root),
                "-f", str(self.snapshot_root / "Makefile"),
                "check",
            ],
            cwd=self.snapshot_root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("--eval must not be used", result.stderr)
        self.assertNotIn(str(decoy_root), result.stdout + result.stderr)

    def test_validation_commands_use_fixed_system_tools(self):
        workflow = expected_workflow(REPOSITORY_ROOT)
        for contract in (EXPECTED_MAKEFILE, workflow):
            self.assertIn("/usr/bin/env -i", contract)
            self.assertIn("/usr/bin/python3 -I", contract)
            self.assertIn('PATH="/usr/bin:/bin:/usr/sbin:/sbin"', contract)
            self.assertNotIn("PATH=\"/usr/local/bin", contract)

    def test_makefile_rejects_makefile_list_injection(self):
        checkout = self.snapshot_root / "checkout with spaces 'quoted' [hostile]"
        external = self.snapshot_root / "external caller"
        checkout.mkdir()
        external.mkdir()
        (checkout / "Makefile").write_text(EXPECTED_MAKEFILE, encoding="utf-8")
        environment = os.environ.copy()
        environment["MAKEFILE_LIST"] = "/tmp/untrusted"

        attacks = (
            (["make", "-f", str(checkout / "Makefile"),
              "MAKEFILE_LIST=/tmp/untrusted", "check"], None),
            (["make", "-e", "-f", str(checkout / "Makefile"), "check"],
             environment),
        )
        for command, attack_environment in attacks:
            with self.subTest(command=command):
                result = subprocess.run(
                    command,
                    cwd=external,
                    env=attack_environment,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)

    def xcodebuild_success_run(self, original_run):
        def run(command, *arguments, **keywords):
            if command == [
                "/usr/bin/xcodebuild", "-list", "-project", "WhineLocation.xcodeproj",
            ]:
                return subprocess.CompletedProcess(command, 0, "", "")
            return original_run(command, *arguments, **keywords)
        return run

    def run_checker(self, subprocess_run=None):
        standard_output = io.StringIO()
        standard_error = io.StringIO()
        run_side_effect = subprocess_run or self.xcodebuild_success_run(
            CHECKER.subprocess.run,
        )
        with mock.patch.object(CHECKER, "ROOT", self.snapshot_root), mock.patch.object(
            CHECKER.shutil,
            "which",
            return_value=None,
        ), mock.patch.object(
            CHECKER.subprocess,
            "run",
            side_effect=run_side_effect,
        ), contextlib.redirect_stdout(standard_output), contextlib.redirect_stderr(
            standard_error
        ):
            return_code = CHECKER.main()
        return return_code, standard_output.getvalue(), standard_error.getvalue()

    def run_snapshot_checker(self, subprocess_run=None):
        checker_path = self.snapshot_root / "scripts/check-baseline.py"
        specification = importlib.util.spec_from_file_location(
            "snapshot_messaging_app_ios_check_baseline",
            checker_path,
        )
        checker = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(checker)
        standard_output = io.StringIO()
        standard_error = io.StringIO()
        run_side_effect = subprocess_run or self.xcodebuild_success_run(
            checker.subprocess.run,
        )
        with mock.patch.object(checker, "ROOT", self.snapshot_root), mock.patch.object(
            checker.shutil,
            "which",
            return_value=None,
        ), mock.patch.object(
            checker.subprocess,
            "run",
            side_effect=run_side_effect,
        ), contextlib.redirect_stdout(standard_output), contextlib.redirect_stderr(
            standard_error
        ):
            return_code = checker.main()
        return return_code, standard_output.getvalue(), standard_error.getvalue()

    def run_integrity(self, mode, require_clean=False, environment=None):
        state = Path(self.temporary_directory.name).parent / (
            self.snapshot_root.name + "-integrity-state.json"
        )
        command = [
            sys.executable, "-I", "scripts/run-isolated-tests.py", mode,
            "--state", str(state),
        ]
        if require_clean:
            command.append("--require-clean")
        return subprocess.run(
            command,
            cwd=self.snapshot_root,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def run_validation_root(self, require_clean=False):
        command = [sys.executable, "-I", "scripts/verify-validation-chain.py"]
        if require_clean:
            command.append("--require-clean")
        return subprocess.run(
            command,
            cwd=self.snapshot_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def first_hosted_workflow_command(self):
        workflow = (self.snapshot_root / ".github/workflows/check.yml").read_text(
            encoding="utf-8"
        )
        commands = [
            line.split("- run: ", 1)[1]
            for line in workflow.splitlines()
            if line.lstrip().startswith("- run: ")
        ]
        self.assertTrue(commands)
        return commands[0]

    def run_first_hosted_workflow_command(self):
        return subprocess.run(
            self.first_hosted_workflow_command(),
            cwd=self.snapshot_root,
            env={
                "HOME": os.environ.get("HOME", ""),
                "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            shell=True,
            executable="/bin/sh",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def independent_contract_failures(self):
        failures = []
        for relative_path, expected_hash in PROTECTED_HASHES.items():
            path = self.snapshot_root / relative_path
            if path.is_symlink() or not path.is_file():
                failures.append(relative_path + " must be a regular file")
            elif openssl_sha256(path.read_bytes()).hexdigest() != expected_hash:
                failures.append(relative_path + " hash mismatch")
        interface_files = sorted(
            path.relative_to(self.snapshot_root).as_posix()
            for path in (self.snapshot_root / "WhineLocation").rglob("*")
            if path.suffix.lower() in {".storyboard", ".xib"}
        )
        if interface_files != INTERFACE_INVENTORY:
            failures.append("interface inventory mismatch")
        for relative_path in interface_files:
            path = self.snapshot_root / relative_path
            if path.is_symlink() or not path.is_file():
                failures.append(relative_path + " must be a regular file")
        graph_files = sorted(
            path.relative_to(self.snapshot_root).as_posix()
            for path in self.snapshot_root.rglob("*")
            if path.is_file() and (
                ".xcodeproj/" in path.as_posix()
                or ".xcworkspace/" in path.as_posix()
                or path.name.lower().endswith(".xcconfig")
                or path.name.lower().endswith(".xcconfig.example")
            )
        )
        if graph_files != XCODE_GRAPH_INVENTORY:
            failures.append("Xcode graph inventory mismatch")
        workflow = self.snapshot_root / ".github/workflows/check.yml"
        if workflow.read_text(encoding="utf-8") != expected_workflow(self.snapshot_root):
            failures.append("workflow mismatch")
        makefile = self.snapshot_root / "Makefile"
        if makefile.read_text(encoding="utf-8") != expected_makefile(self.snapshot_root):
            failures.append("Makefile mismatch")
        return failures

    def home_time_source(self):
        return self.snapshot_root / "WhineLocation/HomeTimeViewController.swift"

    def source(self, relative_path):
        return self.snapshot_root / relative_path

    def replace_source(self, relative_path, current, replacement):
        source_path = self.source(relative_path)
        source = source_path.read_text(encoding="utf-8")
        self.assertIn(current, source)
        source_path.write_text(source.replace(current, replacement, 1), encoding="utf-8")

    def replace_status_validation(self, replacement):
        source_path = self.home_time_source()
        source = source_path.read_text(encoding="utf-8")
        self.assertIn(STATUS_VALIDATED_RESPONSE, source)
        source_path.write_text(
            source.replace(STATUS_VALIDATED_RESPONSE, replacement, 1),
            encoding="utf-8",
        )

    def replace_send_time_method(self, replacement):
        source_path = self.home_time_source()
        source = source_path.read_text(encoding="utf-8")
        current_method = send_time_method(source)
        source_path.write_text(
            source.replace(current_method, replacement, 1),
            encoding="utf-8",
        )

    def assert_checker_rejects(self):
        return_code, _, standard_error = self.run_checker()
        self.assertEqual(1, return_code)
        self.assertIn(
            "protected home-time contract",
            standard_error,
        )

    def assert_checker_rejects_with(self, expected_message):
        return_code, _, standard_error = self.run_checker()
        self.assertEqual(1, return_code)
        self.assertIn(expected_message, standard_error)

    def assert_independent_contract_rejects(self):
        self.assertTrue(self.independent_contract_failures())

    def test_current_source_validates_http_status_before_response_json(self):
        source = self.home_time_source().read_text(encoding="utf-8")
        self.assertIn(STATUS_VALIDATED_RESPONSE, source)
        return_code, _, standard_error = self.run_checker()
        self.assertEqual(0, return_code, standard_error)
        self.assertEqual([], self.independent_contract_failures())

    def test_current_beacon_publication_requires_identity_and_transition(self):
        return_code, _, standard_error = self.run_checker()
        self.assertEqual(0, return_code, standard_error)

    def test_checker_rejects_beacon_publication_without_identity_guard(self):
        self.replace_source(
            "WhineLocation/CoreLocationController.swift",
            "guard let userId = currentDigitsUserID() else {\n                    return\n                }",
            'let userId = ""',
        )
        self.assert_checker_rejects_with(
            "beacon publication must require changed proximity and normalized identity before POST"
        )

    def test_checker_rejects_beacon_request_without_user_identity(self):
        self.replace_source(
            "WhineLocation/CoreLocationController.swift",
            BEACON_REQUEST,
            'Alamofire.request(.POST, getInfo("beaconUrl"), parameters: ["beacon": region.identifier])',
        )
        self.assert_checker_rejects_with(
            "beacon publication must require changed proximity and normalized identity before POST"
        )

    def test_checker_rejects_beacon_publication_before_proximity_change(self):
        source_path = self.source("WhineLocation/CoreLocationController.swift")
        source = source_path.read_text(encoding="utf-8")
        guarded_block = (
            "            if prev != proximity {\n"
            "                guard let userId = currentDigitsUserID() else {\n"
            "                    return\n"
            "                }\n\n"
            "                " + BEACON_REQUEST + "\n"
        )
        unsafe_block = (
            "            guard let userId = currentDigitsUserID() else {\n"
            "                return\n"
            "            }\n"
            "            " + BEACON_REQUEST + "\n\n"
            "            if prev != proximity {\n"
        )
        self.assertIn(guarded_block, source)
        source_path.write_text(source.replace(guarded_block, unsafe_block, 1), encoding="utf-8")
        self.assert_checker_rejects_with(
            "beacon publication must require changed proximity and normalized identity before POST"
        )

    def test_checker_rejects_home_time_disappearance_without_cancellation(self):
        self.replace_source(
            "WhineLocation/HomeTimeViewController.swift",
            "        homeTimeRequest?.cancel()\n        homeTimeRequest = nil\n    }\n\n    override func viewDidLoad",
            "        homeTimeRequest = nil\n    }\n\n    override func viewDidLoad",
        )
        self.assert_checker_rejects_with(
            "home time disappearance must invalidate, cancel, and clear request ownership"
        )

    def test_checker_rejects_home_time_cancellation_moved_into_view_did_load(self):
        self.replace_source(
            "WhineLocation/HomeTimeViewController.swift",
            '''        homeTimeRequest?.cancel()
        homeTimeRequest = nil
    }

    override func viewDidLoad() {
        super.viewDidLoad()''',
            '''    }

    override func viewDidLoad() {
        homeTimeRequest?.cancel()
        homeTimeRequest = nil
        super.viewDidLoad()''',
        )
        self.assert_checker_rejects_with(
            "home time disappearance must invalidate, cancel, and clear request ownership"
        )

    def test_checker_rejects_home_time_submission_while_inactive(self):
        replacement = CANONICAL_SEND_TIME_METHOD.replace(
            '''        guard isHomeTimeViewActive else {
            return
        }

''',
            "",
            1,
        )
        self.replace_send_time_method(replacement)
        self.assert_checker_rejects_with(
            "home time submission must replace, retain, and identity-bind one visible appearance request"
        )

    def test_checker_rejects_home_time_callback_without_request_identity(self):
        replacement = CANONICAL_SEND_TIME_METHOD.replace(
            '''                guard self.homeTimeRequest === request else {
                    return
                }

''',
            "",
            1,
        )
        self.replace_send_time_method(replacement)
        self.assert_checker_rejects_with(
            "home time submission must replace, retain, and identity-bind one visible appearance request"
        )

    def test_credential_fingerprint_detection_uses_non_reversible_digest(self):
        candidate = "a" * 40
        fingerprint = openssl_sha256(candidate.encode("ascii")).hexdigest()
        self.assertTrue(
            CHECKER.contains_credential_fingerprint(candidate, {fingerprint}),
        )
        self.assertFalse(
            CHECKER.contains_credential_fingerprint("b" * 40, {fingerprint}),
        )

    def test_repository_ownership_covers_all_paths(self):
        codeowners = self.source(".github/CODEOWNERS").read_text(encoding="utf-8")
        self.assertEqual("* @garethpaul\n", codeowners)

    def test_agent_guidance_preserves_validation_boundaries(self):
        guidance = " ".join(
            self.source("AGENTS.md").read_text(encoding="utf-8").split()
        )
        for required_text in [
            "make check",
            "tests/test_check_baseline.py",
            "orphaned legacy test source",
            "Do not commit Fabric API keys",
            "If a command above skips because a platform toolchain is missing",
            "record the skipped command and why",
            "later single-colon public recipe replacement",
            "caller-added double-colon recipes run with caller authority",
            "documented single-`-f` invocation",
            "Beacon publications must require a normalized Digits user ID",
        ]:
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, guidance)
        self.assertNotIn("legacy Xcode target", guidance)

    def test_checker_rejects_obsolete_ci_baseline_plan(self):
        obsolete_plan = self.source("docs/plans/2026-06-10-ci-baseline.md")
        obsolete_plan.write_text("# Obsolete CI Baseline\n", encoding="utf-8")
        self.assert_checker_rejects_with(
            "obsolete CI baseline plan must remain absent",
        )

    def test_swiftyjson_reference_uses_https_and_final_newline(self):
        source = self.source("WhineLocation/SwiftyJSON.swift").read_bytes()
        self.assertIn(
            b"https://datatracker.ietf.org/doc/html/rfc7231#section-4.3",
            source,
        )
        self.assertNotIn(b"http://tools.ietf.org/html/rfc7231#section-4.3", source)
        self.assertTrue(source.endswith(b"\n"))

    def test_current_owned_requests_validate_http_status_before_callback_publication(self):
        for relative_path, expected_chain in [
            ("WhineLocation/NewPartnerViewController.swift", PARTNER_VALIDATED_REQUEST),
            ("WhineLocation/PulseViewController.swift", PULSE_LIST_VALIDATED_REQUEST),
            ("WhineLocation/PulseViewController.swift", PULSE_SEND_VALIDATED_REQUEST),
            ("WhineLocation/WaitingViewController.swift", WAITING_VALIDATED_REQUEST),
        ]:
            with self.subTest(relative_path=relative_path):
                source = self.source(relative_path).read_text(encoding="utf-8")
                self.assertIn(expected_chain, source)

        return_code, _, standard_error = self.run_checker()
        self.assertEqual(0, return_code, standard_error)

    def test_checker_rejects_new_partner_request_without_status_validation(self):
        self.replace_source(
            "WhineLocation/NewPartnerViewController.swift",
            PARTNER_VALIDATED_REQUEST,
            PARTNER_REQUEST,
        )
        self.assert_checker_rejects_with(
            "New partner requests must validate HTTP 2xx status before navigation",
        )

    def test_checker_rejects_pulse_list_request_without_status_validation(self):
        self.replace_source(
            "WhineLocation/PulseViewController.swift",
            PULSE_LIST_VALIDATED_REQUEST,
            PULSE_LIST_REQUEST,
        )
        self.assert_checker_rejects_with(
            "Pulse list refresh must validate HTTP 2xx status before publishing rows",
        )

    def test_checker_rejects_pulse_send_request_without_status_validation(self):
        self.replace_source(
            "WhineLocation/PulseViewController.swift",
            PULSE_SEND_VALIDATED_REQUEST,
            PULSE_SEND_REQUEST,
        )
        self.assert_checker_rejects_with(
            "Pulse sends must validate HTTP 2xx status before clearing drafts",
        )

    def test_checker_rejects_waiting_request_without_status_validation(self):
        self.replace_source(
            "WhineLocation/WaitingViewController.swift",
            WAITING_VALIDATED_REQUEST,
            WAITING_REQUEST,
        )
        self.assert_checker_rejects_with(
            "Waiting match checks must validate HTTP 2xx status before navigation",
        )

    def test_checker_rejects_whole_method_block_comment_substitution(self):
        source_path = self.home_time_source()
        source = source_path.read_text(encoding="utf-8")
        current_method = send_time_method(source)
        unsafe_method = current_method.replace(
            "@IBAction func sendTime(sender: AnyObject)",
            "@IBAction func sendTime (sender: AnyObject)",
            1,
        ).replace(STATUS_VALIDATED_RESPONSE, UNVALIDATED_RESPONSE, 1)
        commented_decoy = "/*\n" + current_method + "*/\n"
        source_path.write_text(
            source.replace(current_method, commented_decoy + unsafe_method, 1),
            encoding="utf-8",
        )
        self.assert_checker_rejects()

    def test_checker_rejects_storyboard_action_rewired_to_btn_click(self):
        storyboard = self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard"
        data = storyboard.read_bytes()
        self.assertIn(b'selector="sendTime:"', data)
        storyboard.write_bytes(data.replace(b'selector="sendTime:"', b'selector="btnClick:"', 1))
        self.assert_checker_rejects()

    def test_checker_rejects_storyboard_duplicate_action(self):
        storyboard = self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard"
        data = storyboard.read_bytes()
        action = b'<action selector="sendTime:" destination="YKj-Cv-iAq" eventType="touchUpInside" id="42R-Z2-uwa"/>'
        self.assertIn(action, data)
        storyboard.write_bytes(data.replace(action, action + b'\n                                    ' + action, 1))
        self.assert_checker_rejects()

    def test_checker_rejects_storyboard_removed_action(self):
        storyboard = self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard"
        data = storyboard.read_bytes()
        action = b'<action selector="sendTime:" destination="YKj-Cv-iAq" eventType="touchUpInside" id="42R-Z2-uwa"/>'
        self.assertIn(action, data)
        storyboard.write_bytes(data.replace(action, b'', 1))
        self.assert_checker_rejects()

    def test_checker_rejects_storyboard_direct_segue_action(self):
        storyboard = self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard"
        data = storyboard.read_bytes()
        action = b'<action selector="sendTime:" destination="YKj-Cv-iAq" eventType="touchUpInside" id="42R-Z2-uwa"/>'
        direct = b'<segue destination="KJU-Rt-Qpp" kind="show" identifier="presentNav" id="unsafe-direct"/>'
        self.assertIn(action, data)
        storyboard.write_bytes(data.replace(action, direct, 1))
        self.assert_checker_rejects()

    def test_checker_rejects_added_interface_file(self):
        extra = self.snapshot_root / "WhineLocation/Unsafe.storyboard"
        extra.write_text("<?xml version=\"1.0\" encoding=\"UTF-8\"?><document/>", encoding="utf-8")
        self.assert_checker_rejects()

    def test_checker_rejects_alternate_interface_path(self):
        extra = self.snapshot_root / "WhineLocation/en.lproj/Main.storyboard"
        extra.parent.mkdir(parents=True)
        extra.write_bytes((self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard").read_bytes())
        self.assert_checker_rejects()

    def test_checker_rejects_case_variant_interface_file(self):
        extra = self.snapshot_root / "WhineLocation/MAIN.STORYBOARD"
        extra.write_bytes((self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard").read_bytes())
        self.assert_checker_rejects()

    def test_checker_rejects_storyboard_symlink(self):
        storyboard = self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard"
        target = self.snapshot_root / "storyboard-target"
        target.write_bytes(storyboard.read_bytes())
        storyboard.unlink()
        storyboard.symlink_to(target)
        self.assert_checker_rejects()

    def test_checker_rejects_swift_crlf_conversion(self):
        source_path = self.home_time_source()
        source_path.write_bytes(source_path.read_bytes().replace(b"\n", b"\r\n"))
        self.assert_checker_rejects()

    def test_checker_rejects_storyboard_encoding_change(self):
        storyboard = self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard"
        text = storyboard.read_text(encoding="utf-8")
        storyboard.write_bytes(text.encode("utf-16"))
        self.assert_checker_rejects()

    def test_checker_rejects_single_byte_mutation(self):
        source_path = self.home_time_source()
        data = bytearray(source_path.read_bytes())
        data[-2] ^= 1
        source_path.write_bytes(data)
        self.assert_checker_rejects()

    def test_independent_oracle_rejects_swift_hash_self_update(self):
        source_path = self.home_time_source()
        source_path.write_bytes(source_path.read_bytes() + b"\n")
        new_hash = openssl_sha256(source_path.read_bytes()).hexdigest()
        checker_path = self.snapshot_root / "scripts/check-baseline.py"
        checker = checker_path.read_text(encoding="utf-8")
        checker_path.write_text(
            checker.replace(PROTECTED_HASHES["WhineLocation/HomeTimeViewController.swift"], new_hash, 1),
            encoding="utf-8",
        )
        return_code, _, standard_error = self.run_snapshot_checker()
        self.assertEqual(0, return_code, standard_error)
        self.assert_independent_contract_rejects()

    def test_independent_oracle_rejects_storyboard_hash_self_update(self):
        storyboard = self.snapshot_root / "WhineLocation/Base.lproj/Main.storyboard"
        storyboard.write_bytes(storyboard.read_bytes() + b"\n")
        new_hash = openssl_sha256(storyboard.read_bytes()).hexdigest()
        checker_path = self.snapshot_root / "scripts/check-baseline.py"
        checker = checker_path.read_text(encoding="utf-8")
        checker_path.write_text(
            checker.replace(PROTECTED_HASHES["WhineLocation/Base.lproj/Main.storyboard"], new_hash, 1),
            encoding="utf-8",
        )
        return_code, _, standard_error = self.run_snapshot_checker()
        self.assertEqual(0, return_code, standard_error)
        self.assert_independent_contract_rejects()

    def test_checker_rejects_makefile_skipping_tests(self):
        makefile = self.snapshot_root / "Makefile"
        command = '\t/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test\n'
        mutation = EXPECTED_MAKEFILE.replace(command, "", 1)
        self.assertNotEqual(EXPECTED_MAKEFILE, mutation)
        makefile.write_text(mutation, encoding="utf-8")
        return_code, _, standard_error = self.run_snapshot_checker()
        self.assertEqual(1, return_code)
        self.assertIn(
            "Makefile must exactly preserve rooted lint, test, build, and check gates",
            standard_error,
        )

    def test_checker_rejects_makefile_ignoring_test_failure(self):
        makefile = self.snapshot_root / "Makefile"
        command = '/usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test'
        mutation = EXPECTED_MAKEFILE.replace(command, command + " || true", 1)
        self.assertNotEqual(EXPECTED_MAKEFILE, mutation)
        makefile.write_text(mutation, encoding="utf-8")
        return_code, _, standard_error = self.run_snapshot_checker()
        self.assertEqual(1, return_code)
        self.assertIn(
            "Makefile must exactly preserve rooted lint, test, build, and check gates",
            standard_error,
        )

    def test_checker_rejects_noncanonical_multiline_status_validation(self):
        self.replace_status_validation(
            REQUEST
            + "\n            .validate(statusCode: 200..<300)"
            + "\n            .responseJSON"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_comments_between_chain_tokens(self):
        self.replace_status_validation(
            REQUEST
            + " /* status-only */ .validate(statusCode: 200..<300)"
            + " // response follows\n            .responseJSON"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_removed_status_validation(self):
        self.replace_status_validation(UNVALIDATED_RESPONSE)
        self.assert_checker_rejects()

    def test_checker_rejects_parameterless_validation(self):
        self.replace_status_validation(PARAMETERLESS_VALIDATED_RESPONSE)
        self.assert_checker_rejects()

    def test_checker_rejects_mime_only_validation(self):
        self.replace_status_validation(
            REQUEST
            + '.validate(contentType: ["application/json"])'
            + ".responseJSON"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_wrong_status_range(self):
        self.replace_status_validation(
            REQUEST + ".validate(statusCode: 200..<400).responseJSON"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_closed_status_range(self):
        self.replace_status_validation(
            REQUEST + ".validate(statusCode: 200...299).responseJSON"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_full_chain_line_comment_bypass(self):
        self.replace_status_validation(
            "// " + STATUS_VALIDATED_RESPONSE + "\n        " + UNVALIDATED_RESPONSE
        )
        self.assert_checker_rejects()

    def test_checker_rejects_full_chain_block_comment_bypass(self):
        self.replace_status_validation(
            "/* " + STATUS_VALIDATED_RESPONSE + " */\n        " + UNVALIDATED_RESPONSE
        )
        self.assert_checker_rejects()

    def test_checker_rejects_full_chain_string_literal_bypass(self):
        escaped_chain = STATUS_VALIDATED_RESPONSE.replace('"', '\\"')
        self.replace_status_validation(
            'let validationDecoy = "'
            + escaped_chain
            + '"\n        '
            + UNVALIDATED_RESPONSE
        )
        self.assert_checker_rejects()

    def test_checker_rejects_unreachable_status_validation_bypass(self):
        self.replace_status_validation(
            "if false {\n"
            + "            "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n"
            + "        }\n        "
            + UNVALIDATED_RESPONSE
        )
        self.assert_checker_rejects()

    def test_checker_rejects_parenthesized_false_block(self):
        self.replace_status_validation(
            "if (false) {\n"
            + "            "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n"
            + "        }\n        "
            + UNVALIDATED_RESPONSE
        )
        self.assert_checker_rejects()

    def test_checker_rejects_nested_false_block(self):
        self.replace_status_validation(
            "if true {\n"
            + "            if false {\n"
            + "                "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n"
            + "            }\n"
            + "        }\n        "
            + UNVALIDATED_RESPONSE
        )
        self.assert_checker_rejects()

    def test_checker_rejects_while_false_decoy(self):
        self.replace_status_validation(
            "while false {\n            "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n        }"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_constant_false_expression_decoy(self):
        self.replace_status_validation(
            "if 1 == 0 {\n            "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n        }"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_uninvoked_closure_decoy(self):
        self.replace_status_validation(
            "let neverCalled = {\n            "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n        }"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_uncalled_local_function_decoy(self):
        self.replace_status_validation(
            "func neverCalled() {\n            "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n        }"
        )
        self.assert_checker_rejects()

    def test_checker_rejects_second_executable_request_decoy(self):
        self.replace_status_validation(
            STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n        "
            + UNVALIDATED_RESPONSE
        )
        self.assert_checker_rejects()

    def test_checker_rejects_manager_shared_instance_duplicate(self):
        manager_request = (
            'Alamofire.Manager.sharedInstance.request(.POST, getInfo("newHometimeUrl"), '
            'parameters: ["userId": userId, "homeTime": dateString]).responseJSON'
        )
        self.replace_status_validation(
            STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n        "
            + manager_request
        )
        self.assert_checker_rejects()

    def test_checker_rejects_custom_manager_duplicate(self):
        manager_request = (
            'manager.request(.POST, getInfo("newHometimeUrl"), '
            'parameters: ["userId": userId, "homeTime": dateString]).responseJSON'
        )
        self.replace_status_validation(
            "let manager = Alamofire.Manager.sharedInstance\n        "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n        "
            + manager_request
        )
        self.assert_checker_rejects()

    def test_checker_rejects_navigation_after_empty_callback(self):
        replacement = CANONICAL_SEND_TIME_METHOD.replace(
            '''request.responseJSON { (req, res, json, error) in
            dispatch_async(dispatch_get_main_queue()) {
                guard self.homeTimeRequest === request else {
                    return
                }

                self.homeTimeRequest = nil
                guard self.isHomeTimeViewActive &&
                    requestGeneration == self.homeTimeViewGeneration else {
                        return
                }

                guard error == nil else {
                    return
                }

                self.performSegueWithIdentifier("presentNav", sender: self)
            }
        }''',
            '''request.responseJSON { (req, res, json, error) in
        }

        let error: NSError? = nil
        guard error == nil else {
            return
        }
        self.performSegueWithIdentifier("presentNav", sender: self)''',
        )
        self.replace_send_time_method(replacement)
        self.assert_checker_rejects()

    def test_checker_rejects_extra_navigation_after_callback(self):
        replacement = CANONICAL_SEND_TIME_METHOD.replace(
            "        }\n    }\n",
            "        }\n        self.performSegueWithIdentifier(\"presentNav\", sender: self)\n    }\n",
            1,
        )
        self.replace_send_time_method(replacement)
        self.assert_checker_rejects()

    def test_checker_rejects_status_validation_in_unrelated_method(self):
        source_path = self.home_time_source()
        source = source_path.read_text(encoding="utf-8")
        self.assertIn(STATUS_VALIDATED_RESPONSE, source)
        source = source.replace(STATUS_VALIDATED_RESPONSE, UNVALIDATED_RESPONSE, 1)
        decoy_method = (
            "    func validationDecoy() {\n"
            + "        "
            + STATUS_VALIDATED_RESPONSE
            + " { (_, _, _, _) in }\n"
            + "    }\n\n"
        )
        source = source.replace(
            "    @IBAction func sendTime",
            decoy_method + "    @IBAction func sendTime",
            1,
        )
        source_path.write_text(source, encoding="utf-8")
        self.assert_checker_rejects()

    def test_checker_rejects_project_source_rewiring(self):
        project = self.snapshot_root / "WhineLocation.xcodeproj/project.pbxproj"
        data = project.read_bytes()
        self.assertIn(b"HomeTimeViewController.swift", data)
        project.write_bytes(data.replace(b"HomeTimeViewController.swift", b"UnsafeTimeViewController.swift", 1))
        self.assert_checker_rejects()

    def test_checker_rejects_project_storyboard_rewiring(self):
        project = self.snapshot_root / "WhineLocation.xcodeproj/project.pbxproj"
        data = project.read_bytes()
        self.assertIn(b"Main.storyboard", data)
        project.write_bytes(data.replace(b"Main.storyboard", b"Generated.storyboard", 1))
        self.assert_checker_rejects()

    def test_checker_rejects_workspace_graph_mutation(self):
        workspace = self.snapshot_root / "WhineLocation.xcworkspace/contents.xcworkspacedata"
        workspace.write_bytes(workspace.read_bytes() + b"\n")
        self.assert_checker_rejects()

    def test_checker_rejects_added_scheme_graph_file(self):
        scheme = self.snapshot_root / "WhineLocation.xcodeproj/xcshareddata/xcschemes/Unsafe.xcscheme"
        scheme.parent.mkdir(parents=True)
        scheme.write_text("<Scheme/>\n", encoding="utf-8")
        self.assert_checker_rejects()

    def test_checker_rejects_graph_symlink(self):
        project = self.snapshot_root / "WhineLocation.xcodeproj/project.pbxproj"
        target = self.snapshot_root / "project-copy.pbxproj"
        project.rename(target)
        project.symlink_to(target)
        self.assert_checker_rejects()

    def test_checker_rejects_workflow_make_dry_run_bypass(self):
        workflow = self.snapshot_root / ".github/workflows/check.yml"
        data = workflow.read_text(encoding="utf-8")
        mutation = data.replace("jobs:\n", "jobs:\n  # MAKEFLAGS=-n bypass\n", 1)
        self.assertNotEqual(data, mutation)
        workflow.write_text(mutation, encoding="utf-8")
        self.assert_checker_rejects_with(
            "protected workflow must execute isolated tests and checker directly",
        )

    def test_checker_rejects_workflow_make_check_indirection(self):
        workflow = self.snapshot_root / ".github/workflows/check.yml"
        data = workflow.read_text(encoding="utf-8")
        command = "/usr/bin/python3 -I scripts/run-isolated-tests.py test --require-clean --state /tmp/messaging-ios-integrity-state.json"
        mutation = data.replace(command, "make check", 1)
        self.assertNotEqual(data, mutation)
        workflow.write_text(mutation, encoding="utf-8")
        self.assert_checker_rejects_with(
            "protected workflow must execute isolated tests and checker directly",
        )

    def test_checker_rejects_workflow_without_validation_root_even_if_hash_is_self_updated(self):
        workflow = self.snapshot_root / ".github/workflows/check.yml"
        data = workflow.read_text(encoding="utf-8")
        validation_command = "      - run: " + self.first_hosted_workflow_command() + "\n"
        self.assertIn(validation_command, data)
        workflow.write_text(data.replace(validation_command, "", 1), encoding="utf-8")
        old_hash = openssl_sha256(data.encode("utf-8")).hexdigest()
        new_hash = openssl_sha256(workflow.read_bytes()).hexdigest()
        checker_path = self.snapshot_root / "scripts/check-baseline.py"
        checker = checker_path.read_text(encoding="utf-8")
        checker_path.write_text(
            checker.replace(old_hash, new_hash, 1),
            encoding="utf-8",
        )
        return_code, _, standard_error = self.run_snapshot_checker()
        self.assertEqual(1, return_code)
        self.assertIn(
            "workflow must authenticate the validation chain before isolated runner preflight",
            standard_error,
        )

    def test_integrity_rejects_added_test_file(self):
        extra = self.snapshot_root / "tests/test_decoy.py"
        extra.write_text("raise SystemExit(0)\n", encoding="utf-8")
        result = self.run_integrity("pre")
        self.assertEqual(1, result.returncode)
        self.assertIn("test inventory mismatch", result.stderr)

    def test_integrity_rejects_test_symlink(self):
        extra = self.snapshot_root / "tests/test-decoy.py"
        extra.symlink_to(self.snapshot_root / "tests/test_check_baseline.py")
        result = self.run_integrity("pre")
        self.assertEqual(1, result.returncode)
        self.assertIn("test inventory mismatch", result.stderr)

    def test_integrity_rejects_test_case_variant(self):
        extra = self.snapshot_root / "tests/Test_Check_Baseline.py"
        extra.write_text("raise SystemExit(0)\n", encoding="utf-8")
        result = self.run_integrity("pre")
        self.assertEqual(1, result.returncode)
        self.assertTrue(
            "test inventory mismatch" in result.stderr
            or "tests/test_check_baseline.py hash mismatch" in result.stderr,
            result.stderr,
        )

    def test_validation_root_rejects_runner_restore_self_authorization_before_execution(self):
        runner = self.snapshot_root / "scripts/run-isolated-tests.py"
        original_runner = runner.read_text(encoding="utf-8")
        marker = self.snapshot_root / "runner-executed"
        hostile_runner = (
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            "import sys\n"
            "Path(" + repr(str(marker)) + ").write_text('executed', encoding='utf-8')\n"
            "Path(__file__).write_text(" + repr(original_runner) + ", encoding='utf-8')\n"
            "print('Messaging app iOS integrity pre passed.')\n"
            "raise SystemExit(0)\n"
        )
        runner.write_text(hostile_runner, encoding="utf-8")
        subprocess.run(["git", "add", "scripts/run-isolated-tests.py"], cwd=self.snapshot_root, check=True)
        subprocess.run(
            [
                "git", "-c", "user.name=validation",
                "-c", "user.email=validation@example.invalid",
                "commit", "--quiet", "-m", "hostile runner",
            ],
            cwd=self.snapshot_root,
            check=True,
        )

        result = self.run_validation_root(require_clean=True)

        self.assertEqual(1, result.returncode)
        self.assertIn("scripts/run-isolated-tests.py hash mismatch", result.stderr)
        self.assertNotIn("Messaging app iOS integrity pre passed.", result.stdout)
        self.assertFalse(marker.exists())
        self.assertEqual(hostile_runner, runner.read_text(encoding="utf-8"))

    def test_integrity_rejects_checker_restore_before_execution(self):
        checker = self.snapshot_root / "scripts/check-baseline.py"
        original_checker = checker.read_text(encoding="utf-8")
        marker = self.snapshot_root / "checker-executed"
        hostile_checker = (
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            "Path(" + repr(str(marker)) + ").write_text('executed', encoding='utf-8')\n"
            "Path(__file__).write_text(" + repr(original_checker) + ", encoding='utf-8')\n"
            "raise SystemExit(0)\n"
        )
        checker.write_text(hostile_checker, encoding="utf-8")

        result = self.run_integrity("pre")

        self.assertEqual(1, result.returncode)
        self.assertIn("scripts/check-baseline.py hash mismatch", result.stderr)
        self.assertFalse(marker.exists())
        self.assertEqual(hostile_checker, checker.read_text(encoding="utf-8"))

    def test_hosted_workflow_authenticates_validation_root_before_execution(self):
        validation_root = self.snapshot_root / "scripts/verify-validation-chain.py"
        original_validation_root = validation_root.read_text(encoding="utf-8")
        marker = self.snapshot_root / "validation-root-executed"
        hostile_validation_root = (
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            "import os\n"
            "import subprocess\n"
            "import sys\n"
            "ROOT = Path(__file__).resolve().parents[1]\n"
            "Path(" + repr(str(marker)) + ").write_text('executed', encoding='utf-8')\n"
            "self_path = ROOT / 'scripts/verify-validation-chain.py'\n"
            "self_path.write_text(" + repr(original_validation_root) + ", encoding='utf-8')\n"
            "subprocess.run(['git', 'update-index', '--assume-unchanged', "
            "'scripts/verify-validation-chain.py'], cwd=ROOT, check=True)\n"
            "os.execv(sys.executable, [sys.executable, '-I', str(self_path), *sys.argv[1:]])\n"
        )
        validation_root.write_text(hostile_validation_root, encoding="utf-8")
        subprocess.run(
            ["git", "add", "scripts/verify-validation-chain.py"],
            cwd=self.snapshot_root,
            check=True,
        )
        subprocess.run(
            [
                "git", "-c", "user.name=validation",
                "-c", "user.email=validation@example.invalid",
                "commit", "--quiet", "-m", "hostile validation root",
            ],
            cwd=self.snapshot_root,
            check=True,
        )

        result = self.run_first_hosted_workflow_command()

        self.assertNotEqual(0, result.returncode)
        self.assertFalse(marker.exists())
        self.assertEqual(hostile_validation_root, validation_root.read_text(encoding="utf-8"))

    def test_integrity_rejects_source_laundering_test_before_execution(self):
        source = self.home_time_source()
        canonical = source.read_bytes()
        source.write_bytes(canonical.replace(
            b".validate(statusCode: 200..<300)",
            b"",
            1,
        ))
        test_file = self.snapshot_root / "tests/test_check_baseline.py"
        laundering = (
            "from pathlib import Path\n"
            "Path('WhineLocation/HomeTimeViewController.swift').write_bytes(" + repr(canonical) + ")\n"
        ).encode("utf-8")
        test_file.write_bytes(laundering + test_file.read_bytes())
        result = self.run_integrity("pre")
        self.assertEqual(1, result.returncode)
        self.assertIn("HomeTimeViewController.swift hash mismatch", result.stderr)
        self.assertIn("tests/test_check_baseline.py hash mismatch", result.stderr)
        self.assertNotEqual(canonical, source.read_bytes())

    def test_integrity_rejects_mutate_then_restore_test_startup(self):
        test_file = self.snapshot_root / "tests/test_check_baseline.py"
        original = test_file.read_bytes()
        startup = (
            b"from pathlib import Path\n"
            b"_p = Path('WhineLocation/HomeTimeViewController.swift')\n"
            b"_b = _p.read_bytes()\n"
            b"_p.write_bytes(_b + b' ')\n"
            b"_p.write_bytes(_b)\n"
        )
        test_file.write_bytes(startup + original)
        result = self.run_integrity("pre")
        self.assertEqual(1, result.returncode)
        self.assertIn("tests/test_check_baseline.py hash mismatch", result.stderr)

    def test_integrity_ignores_pythonpath_sitecustomize_and_import_decoys(self):
        attacker = Path(self.temporary_directory.name).parent / (self.snapshot_root.name + "-attacker")
        marker = attacker / "executed"
        attacker.mkdir()
        payload = "from pathlib import Path; Path(" + repr(str(marker)) + ").write_text('executed')\n"
        (attacker / "sitecustomize.py").write_text(payload, encoding="utf-8")
        (attacker / "json.py").write_text(payload + "raise RuntimeError('import hijacked')\n", encoding="utf-8")
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(attacker)
        result = self.run_integrity("pre", require_clean=True, environment=environment)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(marker.exists())
        shutil.rmtree(attacker)

    def test_copied_test_tree_cannot_mutate_candidate_tree(self):
        copied = Path(self.temporary_directory.name).parent / (self.snapshot_root.name + "-copy")
        copied.mkdir()
        with mock.patch.object(RUNNER, "ROOT", self.snapshot_root):
            RUNNER.copy_candidate_tree(copied)
        original = self.home_time_source().read_bytes()
        copied_source = copied / "WhineLocation/HomeTimeViewController.swift"
        copied_source.write_bytes(b"unsafe")
        self.assertEqual(original, self.home_time_source().read_bytes())
        shutil.rmtree(copied)

    def test_integrity_post_rejects_candidate_tree_change(self):
        pre = self.run_integrity("pre", require_clean=True)
        self.assertEqual(0, pre.returncode, pre.stderr)
        readme = self.snapshot_root / "README.md"
        readme.write_bytes(readme.read_bytes() + b"\n")
        post = self.run_integrity("post")
        self.assertEqual(1, post.returncode)
        self.assertIn("candidate tree changed", post.stderr)

    def test_integrity_default_state_is_checkout_specific(self):
        states = []
        for index in range(2):
            checkout = Path(self.temporary_directory.name) / f"checkout-{index}"
            runner = checkout / "scripts/run-isolated-tests.py"
            runner.parent.mkdir(parents=True)
            shutil.copy2(RUNNER_PATH, runner)
            specification = importlib.util.spec_from_file_location(
                f"checkout_specific_runner_{index}",
                runner,
            )
            module = importlib.util.module_from_spec(specification)
            specification.loader.exec_module(module)
            states.append(module.DEFAULT_STATE)

        self.assertNotEqual(states[0], states[1])
        self.assertEqual(states[0].parent, Path(tempfile.gettempdir()))
        self.assertEqual(states[1].parent, Path(tempfile.gettempdir()))


if __name__ == "__main__":
    unittest.main()
