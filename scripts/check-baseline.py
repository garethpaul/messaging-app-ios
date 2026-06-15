#!/usr/bin/env python3
from pathlib import Path
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
EXPECTED_MAKEFILE = """ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint test

lint test build: check

check:
\tpython3 "$(ROOT)/scripts/check-baseline.py"
"""


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


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
        "docs/readme-overview.svg",
        "scripts/check-baseline.py",
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
    require('Alamofire.request(.POST, "https://requestlabs.appspot.com/whine/location"' in share_location,
            "location sharing must use POST",
            failures)
    require("guard let userId = currentDigitsUserID() else" in share_location and
            'userId = ""' not in share_location and
            "session().userID" not in share_location,
            "location sharing must require a normalized Digits user ID before posting",
            failures)
    require('Alamofire.request(.POST, getInfo("newHometimeUrl")' in home_time,
            "hometime updates must use POST",
            failures)
    send_time_method = home_time.split("@IBAction func sendTime", 1)[1].split("override func prepareForSegue", 1)[0]
    require("guard let userId = currentDigitsUserID() else" in send_time_method and
            "session().userID" not in send_time_method,
            "home-time updates must require a normalized Digits user ID before posting",
            failures)
    response_index = send_time_method.find(".responseJSON")
    success_guard_index = send_time_method.find("guard error == nil else")
    segue_index = send_time_method.find('self.performSegueWithIdentifier("presentNav", sender: self)')
    require(0 <= response_index < success_guard_index < segue_index,
            "home-time navigation must occur only after a successful POST callback",
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
    waiting_guard_index = waiting_check.find("guard !isChecking && !hasMatched else")
    waiting_start_index = waiting_check.find("isChecking = true")
    waiting_loading_index = waiting_check.find("self.spinner.hidden = false")
    waiting_session_index = waiting_check.find("guard let digitsSession = Digits.sharedInstance().session()")
    waiting_normalized_user_index = waiting_check.find("let userId = normalizedDigitsUserID(digitsSession.userID)")
    waiting_request_index = waiting_check.find('Alamofire.request(.POST, getInfo("waitingUrl")')
    waiting_response_index = waiting_check.find(".responseJSON")
    waiting_response_finish_index = waiting_check.find("self.finishWaitingCheck()", waiting_response_index)
    waiting_json_guard_index = waiting_check.find("guard error == nil, let jsonValue = json else")
    waiting_parse_index = waiting_check.find("var responseJSON = JSON(jsonValue)")
    waiting_matched_index = waiting_check.find("self.hasMatched = true")
    waiting_segue_index = waiting_check.find('self.performSegueWithIdentifier("NavigationViewController", sender: self)')
    require("private var isChecking = false" in waiting and
            "private var hasMatched = false" in waiting and
            0 <= waiting_guard_index < waiting_start_index < waiting_loading_index,
            "Waiting match checks must reject overlapping and post-match refreshes before loading starts",
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
    send_msg_method = pulse.split("@IBAction func sendMsg", 1)[1].split("func refresh", 1)[0]
    get_data_method = pulse.split("func getData()", 1)[1].split("// move bar up", 1)[0]
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
    require("dataId.removeAll" in get_data_method and
            "dataRead.removeAll" in get_data_method and
            "func endRefreshingIfNeeded()" in pulse and
            "refreshControl?.endRefreshing()" in pulse,
            "Pulse list refresh must clear read-state arrays and end refreshes safely",
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
    require("pulse refresh timer" in readme.lower() and
            "pulse refresh timer" in vision.lower() and
            "pulse refresh timer" in security.lower() and
            "pulse refresh timer" in changes.lower(),
            "project guidance must document pulse refresh timer lifecycle",
            failures)
    require("Status: completed" in pulse_timer_plan and
            "Five isolated hostile mutations were rejected" in pulse_timer_plan and
            "All four Make gates passed" in pulse_timer_plan,
            "pulse refresh timer plan must record completed status and verification",
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
        require("waiting session and response guard" in content.lower(),
                f"{path} must document the waiting session and response guard",
                failures)
        require("waiting concurrent check guard" in content.lower(),
                f"{path} must document the waiting concurrent check guard",
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
    require("waiting session and response guard" in changes.lower(),
            "CHANGES must record waiting session and response guard hardening",
            failures)
    require("waiting concurrent check guard" in changes.lower(),
            "CHANGES must record waiting concurrent check guard hardening",
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
        "git diff --check",
        "27287606534",
        "27402324851",
        "854a1c6566e359a602b1582cdd106a1cfb5b4242",
        "guard let userId = currentDigitsUserID() else",
        "guard error == nil else",
        'performSegueWithIdentifier("presentNav", sender: self)',
    ]:
        require(evidence in home_time_verification,
                f"home time submission guard verification must record {evidence}",
                failures)
    require("permissions:\n  contents: read" in workflow and "cancel-in-progress: true" in workflow and
            "runs-on: macos-15" in workflow and "timeout-minutes: 10" in workflow and
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow and
            "run: make check" in workflow,
            "Check workflow must stay pinned, read-only, and bounded",
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
