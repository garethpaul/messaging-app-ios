#!/usr/bin/env python3
from pathlib import Path
from _hashlib import openssl_sha256
import json
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OLD_FABRIC_API_KEY = "abb870ac2c6cd77fc0a3ee166f786a86748f4eb9"
OLD_CRASHLYTICS_SECRET = "47d331d25396fd56e08c5c5891c16a003ba5647e584bf8fc07feb0e8ae92ab92"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PROTECTED_CONTRACT_HASHES = {
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
    "scripts/run-isolated-tests.py": "3188fb6a11ee233bd1b6439010dfa94552a23bf68b4b8cd59152eb965de98b92",
    "tests/test_check_baseline.py": "2549d2fa4bb41b6eb5176f6f695ee842fc77a61f84b9d3eb16ccc6efec1f4ca2",
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
EXPECTED_MAKEFILE = '''ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint test

lint test build: check

check:
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/check-baseline.py"
\tenv -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
'''


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def sha256_file(path):
    return openssl_sha256(path.read_bytes()).hexdigest()


def interface_files():
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.suffix.lower() in {".storyboard", ".xib"}
    )


def xcode_graph_files():
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and (
            ".xcodeproj/" in path.as_posix()
            or ".xcworkspace/" in path.as_posix()
            or path.name.lower().endswith(".xcconfig")
            or path.name.lower().endswith(".xcconfig.example")
        )
    )


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def parse_xml(relative_path, failures):
    try:
        ET.parse(ROOT / relative_path)
    except ET.ParseError as error:
        failures.append(f"{relative_path} is not well-formed XML: {error}")


def parse_json(relative_path, failures):
    try:
        json.loads(read(relative_path))
    except json.JSONDecodeError as error:
        failures.append(f"{relative_path} is not valid JSON: {error}")


def parse_plist(relative_path, failures):
    try:
        with (ROOT / relative_path).open("rb") as file:
            return plistlib.load(file)
    except Exception as error:
        failures.append(f"{relative_path} is not a readable plist: {error}")
        return {}


def check_png(relative_path, failures):
    path = ROOT / relative_path
    with path.open("rb") as file:
        signature = file.read(len(PNG_SIGNATURE))
    require(signature == PNG_SIGNATURE, f"{relative_path} must be a PNG image", failures)
    require(path.stat().st_size > 100, f"{relative_path} must not be empty", failures)


def tracked_files():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.splitlines()


def main():
    failures = []
    required_files = [
        ".gitignore",
        ".github/workflows/check.yml",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "Podfile",
        "Podfile.lock",
        "docs/plans/2026-06-08-messaging-app-ios-baseline.md",
        "docs/plans/2026-06-08-message-read-state-guards.md",
        "docs/plans/2026-06-08-digits-user-id-normalization.md",
        "docs/plans/2026-06-09-digits-login-success-guard.md",
        "docs/plans/2026-06-09-location-share-user-guard.md",
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-09-partner-prefix-preservation.md",
        "docs/plans/2026-06-09-new-partner-user-guard.md",
        "docs/plans/2026-06-09-pulse-send-throttle.md",
        "docs/plans/2026-06-10-pulse-list-user-guard.md",
        "docs/plans/2026-06-10-hosted-project-validation.md",
        "docs/plans/2026-06-10-home-time-submission-guard.md",
        "docs/plans/2026-06-12-checkout-credential-boundary.md",
        "docs/plans/2026-06-13-location-independent-make.md",
        "docs/plans/2026-06-14-pulse-send-session-guard.md",
        "docs/plans/2026-06-14-pulse-refresh-timer-lifecycle.md",
        "docs/plans/2026-06-14-waiting-session-response-guard.md",
        "docs/plans/2026-06-15-waiting-concurrent-check-guard.md",
        "docs/plans/2026-06-15-waiting-view-activity-guard.md",
        "docs/plans/2026-06-15-waiting-appearance-generation-guard.md",
        "docs/plans/2026-06-15-waiting-active-check-entry.md",
        "docs/plans/2026-06-15-waiting-request-cancellation.md",
        "docs/plans/2026-06-16-pulse-row-integrity.md",
        "docs/plans/2026-06-16-pulse-request-ownership.md",
        "docs/plans/2026-06-16-pulse-publication-ownership.md",
        "docs/plans/2026-06-17-pulse-send-request-ownership.md",
        "docs/plans/2026-06-17-partner-request-ownership.md",
        "docs/readme-overview.svg",
        "scripts/check-baseline.py",
        "scripts/run-isolated-tests.py",
        "tests/test_check_baseline.py",
        "WhineLocation/Info.plist",
        "WhineLocation/ServiceKeys.xcconfig.example",
        "WhineLocation/User.swift",
        "WhineLocation/Messages.swift",
        "WhineLocation/LoginViewcontroller.swift",
        "WhineLocation/NewPartnerViewController.swift",
        "WhineLocation/ShareLocation.swift",
        "WhineLocation/CoreLocationController.swift",
        "WhineLocation/HomeTimeViewController.swift",
        "WhineLocation/WaitingViewController.swift",
        "WhineLocation/PulseViewController.swift",
        "WhineLocation/Dictionary.swift",
        "WhineLocation/Base.lproj/Main.storyboard",
        "WhineLocation/Base.lproj/LaunchScreen.xib",
        "WhineLocation/Images.xcassets/AppIcon.appiconset/Contents.json",
        "WhineLocation.xcodeproj/project.pbxproj",
        "WhineLocation.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
    ]
    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    for relative_path, expected_hash in PROTECTED_CONTRACT_HASHES.items():
        path = ROOT / relative_path
        require(not path.is_symlink() and path.is_file(),
                f"protected home-time contract must be a regular file: {relative_path}",
                failures)
        if not path.is_symlink() and path.is_file():
            require(sha256_file(path) == expected_hash,
                    f"protected home-time contract hash mismatch: {relative_path}",
                    failures)

    actual_interface_files = interface_files()
    require(actual_interface_files == EXPECTED_INTERFACE_FILES,
            "protected home-time contract interface inventory mismatch",
            failures)
    for relative_path in actual_interface_files:
        path = ROOT / relative_path
        require(not path.is_symlink() and path.is_file(),
                f"protected home-time contract interface must be a regular file: {relative_path}",
                failures)
    require(xcode_graph_files() == EXPECTED_XCODE_GRAPH_FILES,
            "protected home-time contract Xcode graph inventory mismatch",
            failures)

    for xml_file in [
        "docs/readme-overview.svg",
        "WhineLocation/Base.lproj/Main.storyboard",
        "WhineLocation/Base.lproj/LaunchScreen.xib",
        "WhineLocation.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
    ]:
        parse_xml(xml_file, failures)

    for json_file in [
        "WhineLocation/Images.xcassets/AppIcon.appiconset/Contents.json",
        "WhineLocation/Images.xcassets/locationIcon.imageset/Contents.json",
        "WhineLocation/Images.xcassets/messageIcon.imageset/Contents.json",
    ]:
        parse_json(json_file, failures)

    for image_file in [
        "WhineLocation/Images.xcassets/locationIcon.imageset/locationIcon.png",
        "WhineLocation/Images.xcassets/messageIcon.imageset/messageIcon.png",
        "WhineLocation/Images.xcassets/miniLogo.imageset/miniLogo.png",
    ]:
        check_png(image_file, failures)

    project = read("WhineLocation.xcodeproj/project.pbxproj")
    gitignore = read(".gitignore")
    info = parse_plist("WhineLocation/Info.plist", failures)
    service_keys = read("WhineLocation/ServiceKeys.xcconfig.example")
    user = read("WhineLocation/User.swift")
    messages = read("WhineLocation/Messages.swift")
    login = read("WhineLocation/LoginViewcontroller.swift")
    new_partner = read("WhineLocation/NewPartnerViewController.swift")
    share_location = read("WhineLocation/ShareLocation.swift")
    home_time = read("WhineLocation/HomeTimeViewController.swift")
    core_location = read("WhineLocation/CoreLocationController.swift")
    waiting = read("WhineLocation/WaitingViewController.swift")
    pulse = read("WhineLocation/PulseViewController.swift")
    readme = read("README.md")
    vision = read("VISION.md")
    security = read("SECURITY.md")
    changes = read("CHANGES.md")
    makefile = read("Makefile")
    read_state_plan = read("docs/plans/2026-06-08-message-read-state-guards.md")
    user_id_plan_path = ROOT / "docs/plans/2026-06-08-digits-user-id-normalization.md"
    user_id_plan = user_id_plan_path.read_text(encoding="utf-8") if user_id_plan_path.exists() else ""
    login_plan = read("docs/plans/2026-06-09-digits-login-success-guard.md")
    location_share_plan = read("docs/plans/2026-06-09-location-share-user-guard.md")
    make_gate_plan = read("docs/plans/2026-06-09-make-gate-aliases.md")
    partner_prefix_plan = read("docs/plans/2026-06-09-partner-prefix-preservation.md")
    new_partner_plan = read("docs/plans/2026-06-09-new-partner-user-guard.md")
    pulse_send_throttle_plan = read("docs/plans/2026-06-09-pulse-send-throttle.md")
    pulse_list_plan = read("docs/plans/2026-06-10-pulse-list-user-guard.md")
    hosted_validation_plan = read("docs/plans/2026-06-10-hosted-project-validation.md")
    home_time_plan = read("docs/plans/2026-06-10-home-time-submission-guard.md")
    checkout_plan = read("docs/plans/2026-06-12-checkout-credential-boundary.md")
    location_independent_make_plan = read("docs/plans/2026-06-13-location-independent-make.md")
    pulse_send_session_plan = read("docs/plans/2026-06-14-pulse-send-session-guard.md")
    pulse_timer_plan = read("docs/plans/2026-06-14-pulse-refresh-timer-lifecycle.md")
    waiting_guard_plan = read("docs/plans/2026-06-14-waiting-session-response-guard.md")
    waiting_concurrent_plan = read("docs/plans/2026-06-15-waiting-concurrent-check-guard.md")
    waiting_activity_plan = read("docs/plans/2026-06-15-waiting-view-activity-guard.md")
    waiting_generation_plan = read("docs/plans/2026-06-15-waiting-appearance-generation-guard.md")
    waiting_active_entry_plan = read("docs/plans/2026-06-15-waiting-active-check-entry.md")
    waiting_request_cancellation_plan = read("docs/plans/2026-06-15-waiting-request-cancellation.md")
    pulse_row_integrity_plan = read("docs/plans/2026-06-16-pulse-row-integrity.md")
    pulse_request_ownership_plan = read("docs/plans/2026-06-16-pulse-request-ownership.md")
    pulse_publication_ownership_plan = read("docs/plans/2026-06-16-pulse-publication-ownership.md")
    pulse_send_ownership_plan = read("docs/plans/2026-06-17-pulse-send-request-ownership.md")
    partner_request_ownership_plan = read("docs/plans/2026-06-17-partner-request-ownership.md")
    workflow = read(".github/workflows/check.yml")
    workflow_files = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        *sorted((ROOT / ".github/workflows").glob("*.yaml")),
    ]

    require(OLD_FABRIC_API_KEY not in project and OLD_CRASHLYTICS_SECRET not in project,
            "project must not contain the old committed Fabric/Crashlytics values",
            failures)
    require("FABRIC_API_KEY" in project and "CRASHLYTICS_BUILD_SECRET" in project,
            "Fabric build phase must use environment placeholders",
            failures)
    require("Desktop/DigitsKit.framework" not in project,
            "Xcode project must not point at a developer Desktop framework path",
            failures)
    require("INFOPLIST_FILE = WhineLocation/Info.plist;" in project,
            "Xcode project must preserve app Info.plist wiring",
            failures)

    for key in ["FABRIC_API_KEY", "CRASHLYTICS_BUILD_SECRET", "TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET"]:
        require(key in service_keys, f"ServiceKeys template must include {key}", failures)
    require(info.get("Fabric", {}).get("APIKey") == "$(FABRIC_API_KEY)",
            "Info.plist must use FABRIC_API_KEY placeholder",
            failures)
    require(info.get("TwitterKitConsumerKey") == "$(TWITTER_CONSUMER_KEY)",
            "Info.plist must use TWITTER_CONSUMER_KEY placeholder",
            failures)
    require(info.get("TwitterKitConsumerSecret") == "$(TWITTER_CONSUMER_SECRET)",
            "Info.plist must use TWITTER_CONSUMER_SECRET placeholder",
            failures)
    for key in ["waitingUrl", "pulseListUrl", "pulseListSendUrl", "newpartnerUrl", "beaconUrl", "newHometimeUrl"]:
        require(info.get(key, "").startswith("https://"),
                f"Info.plist must define HTTPS backend key {key}",
                failures)
    require("NSLocationAlwaysUsageDescription" in info and "NSLocationWhenInUseUsageDescription" in info,
            "Info.plist must document location permissions",
            failures)

    require('Alamofire.request(.POST, "https://requestlabs.appspot.com/whine/user"' in user,
            "user registration must use POST",
            failures)
    require('Alamofire.request(.POST' in messages and 'messages/read"' in messages,
            "message read-state updates must use POST",
            failures)
    require("currentDigitsUserID()" in messages and "as? NSArray" in messages and "as! NSArray" not in messages,
            "message read-state handling must guard Digits sessions and array casts",
            failures)
    require("func normalizedDigitsUserID(userID: String?) -> String?" in messages and
            "stringByTrimmingCharactersInSet(NSCharacterSet.whitespaceAndNewlineCharacterSet())" in messages,
            "message read-state handling must normalize blank Digits user IDs",
            failures)
    require("return normalizedDigitsUserID(session.userID)" in messages,
            "currentDigitsUserID must use the normalized Digits user ID helper",
            failures)
    require("session().userID" not in messages,
            "message read-state handling must not force a Digits session user ID",
            failures)
    require("session != nil && error == nil" in login and
            "guard let userID = normalizedDigitsUserID(session.userID)" in login and
            "setObject(userID, forKey: \"user\")" in login,
            "Digits login must require a successful session and normalized user ID before storing identity",
            failures)
    require("else {\n                self.performSegueWithIdentifier(\"NewPartner\"" not in login,
            "Digits login must not segue into the partner flow after failed authentication",
            failures)
    require("func normalizedPartnerNumber(partnerNumber: String?) -> String?" in new_partner and
            "trimmedPartnerNumber.characters.count == 0" in new_partner,
            "new partner flow must normalize and reject blank partner numbers",
            failures)
    phone_editing_method = new_partner.split("@IBAction func phoneEditingDidBegin", 1)[1].split("@IBAction func findPartnerBtn", 1)[0]
    require("applyPartnerNumberPrefixIfNeeded()" in phone_editing_method and
            'partnerNumber.text = "+1"' not in phone_editing_method and
            "func applyPartnerNumberPrefixIfNeeded()" in new_partner and
            "existingPartnerNumber.characters.count == 0" in new_partner,
            "new partner phone prefix helper must preserve existing partner input",
            failures)
    require("guard let partner = normalizedPartnerNumber(self.partnerNumber.text)" in new_partner and
            "let userId = currentDigitsUserID()" in new_partner and
            "let digitsSession = Digits.sharedInstance().session()" in new_partner,
            "new partner flow must require a normalized current user and Digits session before posting",
            failures)
    require("digitsSession.userID" not in new_partner and "session().userID" not in new_partner,
            "new partner flow must not bypass normalized Digits user ID lookup",
            failures)
    partner_appear_start = new_partner.find("override func viewWillAppear")
    partner_appear_end = new_partner.find("override func viewWillDisappear", partner_appear_start)
    partner_disappear_end = new_partner.find("@IBAction func phoneEditingDidBegin", partner_appear_end)
    partner_appear_body = new_partner[partner_appear_start:partner_appear_end]
    partner_disappear_body = new_partner[partner_appear_end:partner_disappear_end]
    require("private var partnerRequest: Request?" in new_partner and
            "private var isPartnerViewActive = false" in new_partner and
            "private var partnerViewGeneration = 0" in new_partner and
            "isPartnerViewActive = true" in partner_appear_body and
            "partnerViewGeneration += 1" in partner_appear_body,
            "new partner flow must retain requests and activate a new appearance generation",
            failures)
    partner_disappear_inactive = partner_disappear_body.find("isPartnerViewActive = false")
    partner_disappear_generation = partner_disappear_body.find("partnerViewGeneration += 1")
    partner_disappear_cancel = partner_disappear_body.find("partnerRequest?.cancel()")
    partner_disappear_clear = partner_disappear_body.find("partnerRequest = nil")
    require(-1 not in (partner_disappear_inactive, partner_disappear_generation,
                       partner_disappear_cancel, partner_disappear_clear) and
            partner_disappear_inactive < partner_disappear_generation <
            partner_disappear_cancel < partner_disappear_clear,
            "new partner disappearance must invalidate, cancel, and clear request ownership",
            failures)
    partner_action_start = new_partner.find("@IBAction func findPartnerBtn")
    partner_action_end = new_partner.find("override func viewDidLoad", partner_action_start)
    partner_action = new_partner[partner_action_start:partner_action_end]
    partner_replace_cancel = partner_action.find("partnerRequest?.cancel()")
    partner_replace_clear = partner_action.find("partnerRequest = nil")
    partner_generation_capture = partner_action.find("let requestGeneration = partnerViewGeneration")
    partner_request_create = partner_action.find("let request = Alamofire.request")
    partner_request_retain = partner_action.find("partnerRequest = request")
    partner_response = partner_action.find("request.responseJSON")
    partner_main_queue = partner_action.find("dispatch_async(dispatch_get_main_queue())", partner_response)
    partner_identity = partner_action.find("guard self.partnerRequest === request", partner_main_queue)
    partner_owned_clear = partner_action.find("self.partnerRequest = nil", partner_identity)
    partner_activity = partner_action.find("guard self.isPartnerViewActive &&", partner_owned_clear)
    partner_generation = partner_action.find("requestGeneration == self.partnerViewGeneration", partner_activity)
    partner_success = partner_action.find("error == nil else", partner_generation)
    partner_segue = partner_action.find('self.performSegueWithIdentifier("waiting", sender: self)', partner_success)
    require(-1 not in (partner_replace_cancel, partner_replace_clear, partner_generation_capture,
                       partner_request_create, partner_request_retain, partner_response,
                       partner_main_queue, partner_identity, partner_owned_clear,
                       partner_activity, partner_generation, partner_success, partner_segue) and
            partner_replace_cancel < partner_replace_clear < partner_generation_capture <
            partner_request_create < partner_request_retain < partner_response < partner_main_queue <
            partner_identity < partner_owned_clear < partner_activity < partner_generation <
            partner_success < partner_segue and
            new_partner.count("partnerRequest?.cancel()") == 2,
            "new partner navigation must require current request and appearance ownership after replacement cancellation",
            failures)
    require('Alamofire.request(.POST, "https://requestlabs.appspot.com/whine/location"' in share_location,
            "location sharing must use POST",
            failures)
    require("guard let userId = currentDigitsUserID() else" in share_location and
            'userId = ""' not in share_location and
            "session().userID" not in share_location,
            "location sharing must require a normalized Digits user ID before posting",
            failures)
    require('Alamofire.request(.POST, getInfo("beaconUrl")' in core_location,
            "beacon updates must use POST",
            failures)
    require("println(" not in core_location,
            "CoreLocationController must not log location/beacon debug output",
            failures)
    require("as? CLBeacon" in core_location and "locations.last as? CLLocation" in core_location,
            "CoreLocationController must guard beacon and location casts",
            failures)
    for path, source in [
        ("WhineLocation/WaitingViewController.swift", waiting),
        ("WhineLocation/PulseViewController.swift", pulse),
    ]:
        require("println(" not in source, f"{path} must not log message, phone, or network data", failures)
    waiting_check = waiting.split("func check()", 1)[1].split("private func finishWaitingCheck", 1)[0]
    waiting_entry_guard = "guard isWaitingViewActive && !isChecking && !hasMatched else"
    waiting_guard_index = waiting_check.find(waiting_entry_guard)
    waiting_start_index = waiting_check.find("isChecking = true")
    waiting_generation_capture_index = waiting_check.find("let checkGeneration = waitingViewGeneration")
    waiting_loading_index = waiting_check.find("self.spinner.hidden = false")
    waiting_session_index = waiting_check.find("guard let digitsSession = Digits.sharedInstance().session()")
    waiting_normalized_user_index = waiting_check.find("let userId = normalizedDigitsUserID(digitsSession.userID)")
    waiting_request_index = waiting_check.find('Alamofire.request(.POST, getInfo("waitingUrl")')
    waiting_response_index = waiting_check.find(".responseJSON")
    waiting_request_identity_index = waiting_check.find("guard self.waitingRequest === request else")
    waiting_request_clear_index = waiting_check.find("self.waitingRequest = nil", waiting_response_index)
    waiting_response_finish_index = waiting_check.find("self.finishWaitingCheck()", waiting_response_index)
    waiting_json_guard_index = waiting_check.find("guard error == nil, let jsonValue = json else")
    waiting_parse_index = waiting_check.find("var responseJSON = JSON(jsonValue)")
    waiting_matched_index = waiting_check.find("self.hasMatched = true")
    waiting_segue_index = waiting_check.find('self.performSegueWithIdentifier("NavigationViewController", sender: self)')
    waiting_generation_guard = "guard self.isWaitingViewActive && checkGeneration == self.waitingViewGeneration else"
    waiting_generation_guards = waiting_check.count(waiting_generation_guard)
    waiting_side_effect_free_generation_exits = len(re.findall(
        re.escape(waiting_generation_guard) + r"\s*\{\s*return\s*\}",
        waiting_check,
    ))
    require("private var isChecking = false" in waiting and
            "private var hasMatched = false" in waiting and
            0 <= waiting_guard_index < waiting_start_index < waiting_generation_capture_index < waiting_loading_index,
            "Waiting match checks must reject overlapping and post-match refreshes before loading starts",
            failures)
    require(waiting_check.count(waiting_entry_guard) == 1 and
            waiting_guard_index < waiting_start_index and
            waiting_guard_index < waiting_loading_index,
            "Waiting checks must reject inactive entry before request or UI state mutation",
            failures)
    require(0 <= waiting_session_index < waiting_normalized_user_index < waiting_request_index and
            '"userId": userId' in waiting_check and
            '"phoneNumber": digitsSession.phoneNumber' in waiting_check and
            "Digits.sharedInstance().session()." not in waiting_check,
            "Waiting match checks must resolve one normalized Digits session before requesting",
            failures)
    require(0 <= waiting_response_index < waiting_response_finish_index < waiting_json_guard_index < waiting_parse_index and
            "JSON(json!)" not in waiting_check and
            waiting_check.count("self.finishWaitingCheck()") == 2,
            "Waiting match checks must finish UI state and guard response JSON before parsing",
            failures)
    require("private func finishWaitingCheck()" in waiting and
            waiting.find("self.isChecking = false", waiting.find("private func finishWaitingCheck()")) >= 0 and
            "self.spinner.hidden = true" in waiting and
            "self.waitingText.hidden = false" in waiting,
            "Waiting match checks must centralize loading-state completion",
            failures)
    require(0 <= waiting_matched_index < waiting_segue_index,
            "Waiting match checks must mark terminal match state before navigation",
            failures)
    waiting_appear_start = waiting.find("override func viewWillAppear")
    waiting_disappear_start = waiting.find("override func viewWillDisappear")
    waiting_appear_body = waiting[waiting_appear_start:waiting_disappear_start]
    waiting_disappear_end = waiting.find("\n    @IBAction func refreshBtnClick", waiting_disappear_start)
    waiting_disappear_body = waiting[waiting_disappear_start:waiting_disappear_end]
    require("private var isWaitingViewActive = false" in waiting and
            "isWaitingViewActive = true" in waiting_appear_body and
            "isWaitingViewActive = false" in waiting_disappear_body and
            "finishWaitingCheck()" in waiting_disappear_body,
            "WaitingViewController must track visible lifecycle and release retry state",
            failures)
    require("private var waitingViewGeneration = 0" in waiting and
            "override func viewDidLoad" not in waiting and
            waiting_appear_body.find("isWaitingViewActive = true") < waiting_appear_body.find("waitingViewGeneration += 1") < waiting_appear_body.find("check()") and
            waiting_disappear_body.find("isWaitingViewActive = false") < waiting_disappear_body.find("waitingViewGeneration += 1") < waiting_disappear_body.find("finishWaitingCheck()"),
            "WaitingViewController must start checks in and invalidate checks across appearance generations",
            failures)
    require(waiting_generation_guards == 2 and
            waiting_side_effect_free_generation_exits == 2 and
            waiting_check.find(waiting_generation_guard) < waiting_session_index and
            waiting_check.rfind(waiting_generation_guard) < waiting_response_finish_index,
            "Waiting checks must reject stale appearance work without mutating current state",
            failures)
    waiting_cancel_index = waiting_disappear_body.find("waitingRequest?.cancel()")
    waiting_disappear_clear_index = waiting_disappear_body.find("waitingRequest = nil")
    waiting_disappear_finish_index = waiting_disappear_body.find("finishWaitingCheck()")
    require("private var waitingRequest: Request?" in waiting and
            0 <= waiting_cancel_index < waiting_disappear_clear_index < waiting_disappear_finish_index and
            waiting_check.find("let request = Alamofire.request(.POST") < waiting_check.find("self.waitingRequest = request") < waiting_response_index and
            waiting_response_index < waiting_request_identity_index < waiting_check.rfind(waiting_generation_guard) < waiting_request_clear_index < waiting_response_finish_index,
            "Waiting transport work must be retained, cancelled on disappearance, and identity-bound before callback cleanup",
            failures)
    send_msg_method = pulse.split("@IBAction func sendMsg", 1)[1].split("func refresh", 1)[0]
    get_data_method = pulse.split("func getData()", 1)[1].split("// move bar up", 1)[0]
    pulse_cancel_index = get_data_method.find("pulseRequest?.cancel()")
    pulse_initial_clear_index = get_data_method.find("pulseRequest = nil")
    pulse_user_guard_index = get_data_method.find("guard let userId = currentDigitsUserID() else")
    pulse_request_index = get_data_method.find('let request = Alamofire.request(.POST, getInfo("pulseListUrl")')
    pulse_retain_index = get_data_method.find("pulseRequest = request")
    pulse_response_index = get_data_method.find("request.responseJSON")
    pulse_identity_index = get_data_method.find("guard self.pulseRequest === request else")
    pulse_callback_clear_index = get_data_method.find("self.pulseRequest = nil", pulse_identity_index)
    pulse_error_index = get_data_method.find("if (error != nil)")
    require("private var pulseRequest: Request?" in pulse and
            get_data_method.count("pulseRequest?.cancel()") == 1 and
            get_data_method.count("pulseRequest = nil") == 3 and
            0 <= pulse_cancel_index < pulse_initial_clear_index < pulse_user_guard_index < pulse_request_index < pulse_retain_index < pulse_response_index < pulse_identity_index < pulse_error_index < pulse_callback_clear_index,
            "Pulse list transport must cancel replacements and identity-bind callbacks before state mutation",
            failures)
    require("guard let userId = currentDigitsUserID() else" in get_data_method and
            'parameters: ["userId": userId]' in get_data_method and
            "session().userID" not in get_data_method,
            "Pulse list refresh must require a normalized Digits user ID before loading messages",
            failures)
    require("guard let jsonValue = json else" in get_data_method and
            "var json = JSON(jsonValue)" in get_data_method and
            "JSON(json!)" not in get_data_method,
            "Pulse list refresh must guard missing JSON before parsing messages",
            failures)
    pulse_row_fields = ["dataType", "dataInfo", "dataDate", "dataId", "dataRead"]
    pulse_row_sources = ["dataType", "dataInfo", "date", "rndId", "isRead"]
    require(all(f"var next{field[0].upper() + field[1:]}: [String] = []" in get_data_method
                for field in pulse_row_fields) and
            all(f'let {field} = subJson["{source}"].string' in get_data_method
                for field, source in zip(pulse_row_fields, pulse_row_sources)) and
            "else {\n                            continue\n                    }" in get_data_method and
            all(f"next{field[0].upper() + field[1:]}.append({field})" in get_data_method
                for field in pulse_row_fields) and
            all(f"self.{field}.append" not in get_data_method for field in pulse_row_fields),
            "Pulse list refresh must accept only complete rows into local replacement arrays",
            failures)
    pulse_publish = get_data_method.split("dispatch_async(dispatch_get_main_queue()", 1)[-1]
    pulse_assignment_indexes = [
        pulse_publish.find(f"self.{field} = next{field[0].upper() + field[1:]}")
        for field in pulse_row_fields
    ]
    pulse_reload_index = pulse_publish.find("self.tableView.reloadData()")
    pulse_compare_index = pulse_publish.find("compareRead(self.dataId)")
    pulse_refresh_end_index = pulse_publish.find("self.endRefreshingIfNeeded()")
    require("dispatch_async(dispatch_get_main_queue()" in get_data_method and
            all(index >= 0 for index in pulse_assignment_indexes) and
            max(pulse_assignment_indexes) < pulse_reload_index < pulse_compare_index < pulse_refresh_end_index and
            all(f"{field}.removeAll" not in get_data_method for field in pulse_row_fields) and
            "func endRefreshingIfNeeded()" in pulse and
            "refreshControl?.endRefreshing()" in pulse,
            "Pulse list refresh must publish aligned rows before reload, read-state comparison, and refresh completion",
            failures)
    require("if sendAvailable {" in send_msg_method and
            "sendAvailable = false" in send_msg_method and
            "self.sendAvailable = true" in send_msg_method and
            "sendAvailable == false" not in send_msg_method and
            "sendAvailable == true" not in send_msg_method,
            "Pulse send throttle must assign cooldown state instead of comparing it",
            failures)
    session_guard_index = send_msg_method.find("guard let digitsSession = Digits.sharedInstance().session()")
    normalized_user_index = send_msg_method.find("let userId = normalizedDigitsUserID(digitsSession.userID)")
    throttle_index = send_msg_method.find("if sendAvailable {")
    request_index = send_msg_method.find('Alamofire.request(.POST, getInfo("pulseListSendUrl")')
    require(0 <= session_guard_index < normalized_user_index < throttle_index < request_index and
            '"userId": userId' in send_msg_method and
            '"phoneNumber": digitsSession.phoneNumber' in send_msg_method and
            "Digits.sharedInstance().session()." not in send_msg_method,
            "Pulse send must resolve one valid session before throttle, UI, and request mutation",
            failures)
    send_request_index = send_msg_method.find('let request = Alamofire.request(.POST, getInfo("pulseListSendUrl")')
    send_retain_index = send_msg_method.find("pulseSendRequest = request")
    send_response_index = send_msg_method.find("request.responseJSON")
    send_finish_call_index = send_msg_method.find("self.finishPulseSendRequest(request, succeeded: error == nil)")
    send_finish_start = pulse.find("func finishPulseSendRequest(request: Request, succeeded: Bool)")
    send_finish_end = pulse.find("\n    func resetPulseSendUI", send_finish_start)
    send_finish_body = pulse[send_finish_start:send_finish_end]
    send_identity_index = send_finish_body.find("guard self.pulseSendRequest === request")
    send_clear_index = send_finish_body.find("self.pulseSendRequest = nil")
    send_success_index = send_finish_body.find("if succeeded")
    send_text_clear_index = send_finish_body.find('self.textField.text = ""')
    send_refresh_index = send_finish_body.find("self.getData()")
    send_reset_index = send_finish_body.find("self.resetPulseSendUI()")
    require("private var pulseSendRequest: Request?" in pulse and
            0 <= send_request_index < send_retain_index < send_response_index < send_finish_call_index and
            send_finish_start >= 0 and send_finish_end > send_finish_start and
            0 <= send_identity_index < send_clear_index < send_success_index < send_text_clear_index < send_refresh_index < send_reset_index,
            "Pulse sends must retain exact request ownership through success-only publication",
            failures)
    require("dispatch_after" not in send_msg_method and
            send_msg_method.count('self.textField.text = ""') == 1 and
            "sendBtn.enabled = false" in send_msg_method and
            "textField.enabled = false" in send_msg_method and
            "self.sendBtn.enabled = true" in send_msg_method and
            "self.textField.enabled = true" in send_msg_method,
            "Pulse send UI must follow request completion instead of a fixed delay",
            failures)

    for forbidden in ["Info.plist\n", "*.plist"]:
        require(forbidden not in gitignore, ".gitignore must not ignore committed plist baselines", failures)
    for expected in ["*.local.xcconfig", "*.secrets.xcconfig", "*.local.plist", "*.secrets.plist", ".env"]:
        require(expected in gitignore, f".gitignore must include {expected}", failures)

    require(makefile == EXPECTED_MAKEFILE,
            "Makefile must exactly preserve rooted lint, test, build, and check gates",
            failures)
    require("make -f /path/to/messaging-app-ios/Makefile check" in readme,
            "README must document location-independent Makefile invocation",
            failures)
    require("status: completed" in location_independent_make_plan and
            "root and external-directory" in location_independent_make_plan and
            "five isolated hostile mutations" in location_independent_make_plan,
            "location-independent Make plan must record completed root, external, and mutation verification",
            failures)
    require("status: completed" in pulse_send_session_plan and
            "hostile mutations" in pulse_send_session_plan and
            "all four Make gates" in pulse_send_session_plan,
            "pulse send session plan must record completed status and verification",
            failures)
    require("Status: completed" in waiting_guard_plan and
            "All four Make gates passed" in waiting_guard_plan and
            "Six isolated hostile mutations were rejected" in waiting_guard_plan and
            "external directory" in waiting_guard_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(waiting_guard_plan, "Verification Completed")),
            "waiting session and response guard plan must record completed verification",
            failures)
    require("Status: completed" in waiting_concurrent_plan and
            "All four Make gates passed" in waiting_concurrent_plan and
            "Six isolated hostile mutations were rejected" in waiting_concurrent_plan and
            "external directory" in waiting_concurrent_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(waiting_concurrent_plan, "Verification Completed")),
            "waiting concurrent check guard plan must record completed verification",
            failures)
    require("Status: completed" in waiting_activity_plan and
            "All four Make gates passed" in waiting_activity_plan and
            "Six isolated hostile mutations were rejected" in waiting_activity_plan and
            "external directory" in waiting_activity_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(waiting_activity_plan, "Verification Completed")),
            "waiting view activity guard plan must record completed verification",
            failures)
    require("Status: completed" in waiting_generation_plan and
            "All four Make gates passed" in waiting_generation_plan and
            "Eight isolated hostile mutations were rejected" in waiting_generation_plan and
            "external directory" in waiting_generation_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(waiting_generation_plan, "Verification Completed")),
            "waiting appearance generation guard plan must record completed verification",
            failures)
    require("Status: completed" in waiting_active_entry_plan and
            "All four Make gates passed" in waiting_active_entry_plan and
            "Five isolated hostile mutations were rejected" in waiting_active_entry_plan and
            "external directory" in waiting_active_entry_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(waiting_active_entry_plan, "Verification Completed")),
            "waiting active check entry guard plan must record completed verification",
            failures)
    require("Status: completed" in waiting_request_cancellation_plan and
            "All four Make gates passed" in waiting_request_cancellation_plan and
            "Seven isolated hostile mutations were rejected" in waiting_request_cancellation_plan and
            "external directory" in waiting_request_cancellation_plan and
            "Xcode is unavailable on Linux" in waiting_request_cancellation_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(waiting_request_cancellation_plan, "Verification Completed")),
            "waiting request cancellation plan must record completed verification",
            failures)
    require("Status: completed" in pulse_row_integrity_plan and
            "All four Make gates passed" in pulse_row_integrity_plan and
            "Eight isolated hostile mutations were rejected" in pulse_row_integrity_plan and
            "external directory" in pulse_row_integrity_plan and
            "Xcode is unavailable on Linux" in pulse_row_integrity_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(pulse_row_integrity_plan, "Verification Completed")),
            "pulse row integrity plan must record completed verification",
            failures)
    require("Status: completed" in pulse_request_ownership_plan and
            "All four Make gates passed" in pulse_request_ownership_plan and
            "Six isolated hostile mutations were rejected" in pulse_request_ownership_plan and
            "external directory" in pulse_request_ownership_plan and
            "Xcode is unavailable on Linux" in pulse_request_ownership_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(pulse_request_ownership_plan, "Verification Completed")),
            "pulse request ownership plan must record completed verification",
            failures)
    require("Status: completed" in pulse_publication_ownership_plan and
            "All four Make gates passed" in pulse_publication_ownership_plan and
            "Seven isolated hostile mutations were rejected" in pulse_publication_ownership_plan and
            "external directory" in pulse_publication_ownership_plan and
            "Xcode is unavailable on Linux" in pulse_publication_ownership_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(pulse_publication_ownership_plan, "Verification Completed")),
            "pulse publication ownership plan must record completed verification",
            failures)
    response_start = pulse.find("request.responseJSON")
    response_end = pulse.find("\n    func finishPulseRequest", response_start)
    response_body = pulse[response_start:response_end]
    row_parse_start = response_body.find("var nextDataType")
    publication_start = response_body.find("dispatch_async(dispatch_get_main_queue()", row_parse_start)
    publication_body = response_body[publication_start:]
    publication_guard = publication_body.find("guard self.pulseRequest === request")
    publication_clear = publication_body.find("self.pulseRequest = nil")
    publication_write = publication_body.find("self.dataType = nextDataType")
    require(response_start >= 0 and response_end > response_start and
            row_parse_start >= 0 and publication_start > row_parse_start and
            0 <= publication_guard < publication_clear < publication_write,
            "pulse success publication must revalidate and clear exact request ownership before row mutation",
            failures)
    require("self.pulseRequest = nil" not in response_body[:row_parse_start],
            "pulse success response must retain request ownership through row parsing",
            failures)
    finish_start = pulse.find("func finishPulseRequest(request: Request)")
    finish_end = pulse.find("\n    func endRefreshingIfNeeded", finish_start)
    finish_body = pulse[finish_start:finish_end]
    finish_guard = finish_body.find("guard self.pulseRequest === request")
    finish_clear = finish_body.find("self.pulseRequest = nil")
    finish_refresh = finish_body.find("self.endRefreshingIfNeeded()")
    require(finish_start >= 0 and finish_end > finish_start and
            0 <= finish_guard < finish_clear < finish_refresh,
            "pulse failure completion must revalidate and clear exact request ownership before ending refresh",
            failures)
    appear_start = pulse.find("override func viewWillAppear")
    disappear_start = pulse.find("override func viewWillDisappear")
    appear_body = pulse[appear_start:disappear_start]
    disappear_end = pulse.find("\n    func keyboardWillShow", disappear_start)
    disappear_body = pulse[disappear_start:disappear_end]
    require("var refreshTimer: NSTimer?" in pulse and
            appear_body.find("refreshTimer?.invalidate()") >= 0 and
            appear_body.find("refreshTimer = NSTimer.scheduledTimerWithTimeInterval(") > appear_body.find("refreshTimer?.invalidate()") and
            disappear_body.find("refreshTimer?.invalidate()") >= 0 and
            disappear_body.find("refreshTimer = nil") > disappear_body.find("refreshTimer?.invalidate()"),
            "PulseViewController must own and invalidate its repeating refresh timer",
            failures)
    pulse_disappear_cancel_index = disappear_body.find("pulseRequest?.cancel()")
    pulse_disappear_clear_index = disappear_body.find("pulseRequest = nil")
    require(pulse.count("pulseRequest?.cancel()") == 2 and
            pulse.count("pulseRequest = nil") == 4 and
            0 <= pulse_disappear_cancel_index < pulse_disappear_clear_index,
            "PulseViewController must cancel and clear its retained request on disappearance",
            failures)
    pulse_send_disappear_cancel_index = disappear_body.find("pulseSendRequest?.cancel()")
    pulse_send_disappear_clear_index = disappear_body.find("pulseSendRequest = nil")
    pulse_send_disappear_reset_index = disappear_body.find("resetPulseSendUI()")
    require(0 <= pulse_send_disappear_cancel_index < pulse_send_disappear_clear_index < pulse_send_disappear_reset_index,
            "PulseViewController must cancel and clear its retained send before releasing send UI state",
            failures)
    require("pulse refresh timer" in readme.lower() and
            "pulse refresh timer" in vision.lower() and
            "pulse refresh timer" in security.lower() and
            "pulse refresh timer" in changes.lower(),
            "project guidance must document pulse refresh timer lifecycle",
            failures)
    require("pulse request ownership" in readme.lower() and
            "pulse request ownership" in vision.lower() and
            "pulse request ownership" in security.lower() and
            "pulse request ownership" in changes.lower(),
            "project guidance must document pulse request ownership",
            failures)
    require("pulse publication ownership" in readme.lower() and
            "pulse publication ownership" in vision.lower() and
            "pulse publication ownership" in security.lower() and
            "pulse publication ownership" in changes.lower(),
            "project guidance must document pulse publication ownership",
            failures)
    require("pulse send request ownership" in readme.lower() and
            "pulse send request ownership" in vision.lower() and
            "pulse send request ownership" in security.lower() and
            "pulse send request ownership" in changes.lower(),
            "project guidance must document pulse send request ownership",
            failures)
    require("partner request ownership" in readme.lower() and
            "partner request ownership" in vision.lower() and
            "partner request ownership" in security.lower() and
            "partner request ownership" in changes.lower(),
            "project guidance must document partner request ownership",
            failures)
    require("Status: completed" in pulse_timer_plan and
            "Five isolated hostile mutations were rejected" in pulse_timer_plan and
            "All four Make gates passed" in pulse_timer_plan,
            "pulse refresh timer plan must record completed status and verification",
            failures)
    require("status: completed" in pulse_send_ownership_plan and
            "All four Make gates passed" in pulse_send_ownership_plan and
            "Eight isolated hostile mutations were rejected" in pulse_send_ownership_plan and
            "external directory" in pulse_send_ownership_plan and
            "Xcode is unavailable on Linux" in pulse_send_ownership_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(pulse_send_ownership_plan, "Verification Completed")),
            "pulse send request ownership plan must record completed verification",
            failures)
    require("status: completed" in partner_request_ownership_plan and
            "All four Make gates passed" in partner_request_ownership_plan and
            "Nine isolated hostile mutations were rejected" in partner_request_ownership_plan and
            "external directory" in partner_request_ownership_plan and
            "Xcode is unavailable on Linux" in partner_request_ownership_plan and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", markdown_section(partner_request_ownership_plan, "Verification Completed")),
            "partner request ownership plan must record completed verification",
            failures)

    tracked = tracked_files()
    generated = [path for path in tracked if "xcuserdata" in path or path.endswith(".xcuserstate")]
    require(not generated, "generated Xcode user state must not be tracked: " + ", ".join(generated), failures)

    for path, content in [("README.md", readme), ("VISION.md", vision), ("SECURITY.md", security)]:
        require("make lint" in content and "make test" in content and "make build" in content and
                "make check" in content and "ServiceKeys.xcconfig.example" in content,
                f"{path} must document static checks and local credential setup",
                failures)
        require("message" in content.lower() and "location" in content.lower(),
                f"{path} must document messaging/location privacy posture",
                failures)
        require("read-state" in content.lower(),
                f"{path} must document message read-state guardrails",
                failures)
        require("digits user id normalization" in content.lower(),
                f"{path} must document Digits user ID normalization",
                failures)
        require("digits login success guard" in content.lower(),
                f"{path} must document the Digits login success guard",
                failures)
        require("location share user guard" in content.lower(),
                f"{path} must document the location share user guard",
                failures)
        require("new partner user guard" in content.lower(),
                f"{path} must document the new partner user guard",
                failures)
        require("partner prefix preservation" in content.lower(),
                f"{path} must document partner prefix preservation",
                failures)
        require("pulse send throttle" in content.lower(),
                f"{path} must document pulse send throttle",
                failures)
        require("pulse send session guard" in content.lower(),
                f"{path} must document pulse send session guard",
                failures)
        require("pulse list user guard" in content.lower(),
                f"{path} must document pulse list user guard",
                failures)
        require("pulse row integrity" in content.lower(),
                f"{path} must document pulse row integrity",
                failures)
        require("pulse request ownership" in content.lower(),
                f"{path} must document pulse request ownership",
                failures)
        require("pulse publication ownership" in content.lower(),
                f"{path} must document pulse publication ownership",
                failures)
        require("waiting session and response guard" in content.lower(),
                f"{path} must document the waiting session and response guard",
                failures)
        require("waiting concurrent check guard" in content.lower(),
                f"{path} must document the waiting concurrent check guard",
                failures)
        require("waiting view activity guard" in content.lower(),
                f"{path} must document the waiting view activity guard",
                failures)
        require("waiting appearance generation guard" in content.lower(),
                f"{path} must document the waiting appearance generation guard",
                failures)
        require("waiting active check entry guard" in content.lower(),
                f"{path} must document the waiting active check entry guard",
                failures)
        require("waiting request cancellation" in content.lower(),
                f"{path} must document waiting request cancellation",
                failures)
        require("home time submission guard" in content.lower(),
                f"{path} must document home time submission guard",
                failures)
    require("Fabric/Crashlytics" in changes and "POST" in changes and "read-state" in changes,
            "CHANGES must record credential, request-method, and read-state hardening",
            failures)
    require("digits user id normalization" in changes.lower(),
            "CHANGES must record Digits user ID normalization",
            failures)
    require("digits login success guard" in changes.lower(),
            "CHANGES must record Digits login success guard hardening",
            failures)
    require("location share user guard" in changes.lower(),
            "CHANGES must record location share user guard hardening",
            failures)
    require("new partner user guard" in changes.lower(),
            "CHANGES must record new partner user guard hardening",
            failures)
    require("partner prefix preservation" in changes.lower(),
            "CHANGES must record partner prefix preservation",
            failures)
    require("pulse send throttle" in changes.lower(),
            "CHANGES must record pulse send throttle",
            failures)
    require("pulse send session guard" in changes.lower(),
            "CHANGES must record pulse send session guard",
            failures)
    require("pulse list user guard" in changes.lower(),
            "CHANGES must record pulse list user guard",
            failures)
    require("pulse row integrity" in changes.lower(),
            "CHANGES must record pulse row integrity",
            failures)
    require("pulse request ownership" in changes.lower(),
            "CHANGES must record pulse request ownership",
            failures)
    require("pulse publication ownership" in changes.lower(),
            "CHANGES must record pulse publication ownership",
            failures)
    require("waiting session and response guard" in changes.lower(),
            "CHANGES must record waiting session and response guard hardening",
            failures)
    require("waiting concurrent check guard" in changes.lower(),
            "CHANGES must record waiting concurrent check guard hardening",
            failures)
    require("waiting view activity guard" in changes.lower(),
            "CHANGES must record waiting view activity guard hardening",
            failures)
    require("waiting appearance generation guard" in changes.lower(),
            "CHANGES must record waiting appearance generation guard hardening",
            failures)
    require("waiting active check entry guard" in changes.lower(),
            "CHANGES must record waiting active check entry guard hardening",
            failures)
    require("waiting request cancellation" in changes.lower(),
            "CHANGES must record waiting request cancellation hardening",
            failures)
    require("home time submission guard" in changes.lower(),
            "CHANGES must record home time submission guard",
            failures)
    require("make lint" in changes and "make test" in changes and "make build" in changes and "make check" in changes,
            "CHANGES must record Make gate aliases",
            failures)
    require("status: completed" in read_state_plan,
            "message read-state guard plan must be marked completed",
            failures)
    require("status: completed" in user_id_plan,
            "Digits user ID normalization plan must be marked completed",
            failures)
    require("status: completed" in login_plan,
            "Digits login success guard plan must be marked completed",
            failures)
    require("status: completed" in location_share_plan,
            "location share user guard plan must be marked completed",
            failures)
    require("status: completed" in make_gate_plan,
            "Make gate alias plan must be marked completed",
            failures)
    require("status: completed" in partner_prefix_plan,
            "partner prefix preservation plan must be marked completed",
            failures)
    require("status: completed" in new_partner_plan,
            "new partner user guard plan must be marked completed",
            failures)
    require("status: completed" in pulse_send_throttle_plan,
            "pulse send throttle plan must be marked completed",
            failures)
    require("status: completed" in pulse_list_plan,
            "pulse list user guard plan must be marked completed",
            failures)
    require("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
            "hosted project validation plan must be marked completed",
            failures)
    home_time_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", home_time_plan)
    home_time_work = markdown_section(home_time_plan, "Work Completed")
    home_time_verification = markdown_section(home_time_plan, "Verification Completed")
    checkout_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", checkout_plan)
    checkout_work = markdown_section(checkout_plan, "Work Completed")
    checkout_verification = markdown_section(
        checkout_plan, "Verification Completed"
    )
    require(home_time_status == ["completed"],
            "home time submission guard plan must record exactly one completed status",
            failures)
    require(bool(home_time_work),
            "home time submission guard plan must record completed work",
            failures)
    require(bool(home_time_verification) and not re.search(
                r"(?i)\b(pending|todo|tbd|not run)\b", home_time_verification),
            "home time submission guard plan must record completed verification",
            failures)
    for evidence in [
        "make check",
        "make lint",
        "make test",
        "make build",
        "python3 -m py_compile scripts/check-baseline.py",
        "python3 -I scripts/run-isolated-tests.py test",
        "git diff --check",
        "27287606534",
        "27402324851",
        "854a1c6566e359a602b1582cdd106a1cfb5b4242",
        "guard let userId = currentDigitsUserID() else",
        ".validate(statusCode: 200..<300).responseJSON",
        "guard error == nil else",
        'performSegueWithIdentifier("presentNav", sender: self)',
    ]:
        require(evidence in home_time_verification,
                f"home time submission guard verification must record {evidence}",
                failures)
    require("MAKEFLAGS" not in workflow and "make check" not in workflow,
            "protected workflow must execute isolated tests and checker directly",
            failures)
    checkout_action = (
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
    )
    checkout_blocks = re.findall(
        rf"(?m)^(?P<indent> *)- +uses: +{re.escape(checkout_action)}[^\n]*\n"
        rf"(?P=indent)  with:\n"
        rf"(?P=indent)    persist-credentials: +false *$",
        workflow,
    )
    checkout_actions = re.findall(
        r"(?m)^\s*-\s+uses:\s+actions/checkout@",
        workflow,
    )
    require(len(workflow_files) == 1 and
            workflow.count("permissions:") == 1 and
            workflow.count("contents: read") == 1 and
            not re.search(r"(?m)^\s*[A-Za-z-]+:\s*write\s*$", workflow) and
            len(checkout_actions) == 1 and
            workflow.count(checkout_action) == 1 and
            len(checkout_blocks) == 1 and
            workflow.count("persist-credentials: false") == 1 and
            "persist-credentials: true" not in workflow,
            "Check workflow must keep one read-only permission block and one "
            "pinned, credential-free checkout",
            failures)
    require(checkout_status == ["completed"] and checkout_work and
            "make check" in checkout_verification,
            "checkout credential plan must record one completed status, "
            "completed work, and make check verification",
            failures)

    if shutil.which("xcodebuild"):
        result = subprocess.run(
            ["xcodebuild", "-list", "-project", "WhineLocation.xcodeproj"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        require(result.returncode == 0,
                "xcodebuild could not parse WhineLocation.xcodeproj: " + result.stderr.strip(), failures)
    else:
        print("xcodebuild unavailable; static iOS baseline only.")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Messaging app iOS baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
