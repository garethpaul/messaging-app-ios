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
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPOSITORY_ROOT / "scripts/check-baseline.py"
RUNNER_PATH = REPOSITORY_ROOT / "scripts/run-isolated-tests.py"
REQUEST = (
    'Alamofire.request(.POST, getInfo("newHometimeUrl"), '
    'parameters: ["userId": userId, "homeTime": dateString])'
)
PARAMETERLESS_VALIDATED_RESPONSE = REQUEST + ".validate().responseJSON"
STATUS_VALIDATED_RESPONSE = REQUEST + ".validate(statusCode: 200..<300).responseJSON"
UNVALIDATED_RESPONSE = REQUEST + ".responseJSON"
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
PROTECTED_HASHES = {
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
    ".github/workflows/check.yml":
        "284a336a4bb5a9c4981ef3e1dd7dec5e2e63a3a80c7ed098c709e3a519331350",
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
EXPECTED_MAKEFILE = '''ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint test

lint test build: check

check:
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/check-baseline.py"
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
'''
CANONICAL_SEND_TIME_METHOD = '''    @IBAction func sendTime(sender: AnyObject) {
        guard let userId = currentDigitsUserID() else {
            return
        }

        let dateFormatter = NSDateFormatter()
        dateFormatter.dateFormat = "hh:mm a" //format style. Browse online to get a format that fits your needs.
        let dateString = dateFormatter.stringFromDate(uiPicker.date)

        Alamofire.request(.POST, getInfo("newHometimeUrl"), parameters: ["userId": userId, "homeTime": dateString]).validate(statusCode: 200..<300).responseJSON { (req, res, json, error) in
            guard error == nil else {
                return
            }

            self.performSegueWithIdentifier("presentNav", sender: self)
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
        self.temporary_directory.cleanup()

    def run_checker(self):
        standard_output = io.StringIO()
        standard_error = io.StringIO()
        with mock.patch.object(CHECKER, "ROOT", self.snapshot_root), mock.patch.object(
            CHECKER.shutil,
            "which",
            return_value=None,
        ), contextlib.redirect_stdout(standard_output), contextlib.redirect_stderr(
            standard_error
        ):
            return_code = CHECKER.main()
        return return_code, standard_output.getvalue(), standard_error.getvalue()

    def run_snapshot_checker(self):
        checker_path = self.snapshot_root / "scripts/check-baseline.py"
        specification = importlib.util.spec_from_file_location(
            "snapshot_messaging_app_ios_check_baseline",
            checker_path,
        )
        checker = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(checker)
        standard_output = io.StringIO()
        standard_error = io.StringIO()
        with mock.patch.object(checker, "ROOT", self.snapshot_root), mock.patch.object(
            checker.shutil,
            "which",
            return_value=None,
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
        makefile = self.snapshot_root / "Makefile"
        if makefile.read_text(encoding="utf-8") != EXPECTED_MAKEFILE:
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

    def test_repository_ownership_covers_all_paths(self):
        codeowners = self.source(".github/CODEOWNERS").read_text(encoding="utf-8")
        self.assertEqual("* @garethpaul\n", codeowners)

    def test_agent_guidance_preserves_validation_boundaries(self):
        guidance = self.source("AGENTS.md").read_text(encoding="utf-8")
        for required_text in [
            "make check",
            "tests/test_check_baseline.py",
            "orphaned legacy test source",
            "Do not commit Fabric API keys",
            "If a command above skips because a platform toolchain is missing",
            "record the skipped command and why",
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
        command = '\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test\n'
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
        command = 'python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test'
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
            '''.responseJSON { (req, res, json, error) in
            guard error == nil else {
                return
            }

            self.performSegueWithIdentifier("presentNav", sender: self)
        }''',
            '''.responseJSON { (req, res, json, error) in
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
        self.assert_checker_rejects()

    def test_checker_rejects_workflow_make_check_indirection(self):
        workflow = self.snapshot_root / ".github/workflows/check.yml"
        data = workflow.read_text(encoding="utf-8")
        command = "python3 -I scripts/run-isolated-tests.py test --require-clean --state /tmp/messaging-ios-integrity-state.json"
        mutation = data.replace(command, "make check", 1)
        self.assertNotEqual(data, mutation)
        workflow.write_text(mutation, encoding="utf-8")
        self.assert_checker_rejects()

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

    def test_integrity_rejects_source_laundering_test_before_execution(self):
        source = self.home_time_source()
        canonical = source.read_bytes()
        source.write_bytes(canonical.replace(
            b".validate(statusCode: 200..<300).responseJSON",
            b".responseJSON",
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


if __name__ == "__main__":
    unittest.main()
