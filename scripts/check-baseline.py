#!/usr/bin/env python3
from pathlib import Path
import json
import plistlib
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OLD_FABRIC_API_KEY = "abb870ac2c6cd77fc0a3ee166f786a86748f4eb9"
OLD_CRASHLYTICS_SECRET = "47d331d25396fd56e08c5c5891c16a003ba5647e584bf8fc07feb0e8ae92ab92"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


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
    workflow = read(".github/workflows/check.yml")

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

    for forbidden in ["Info.plist\n", "*.plist"]:
        require(forbidden not in gitignore, ".gitignore must not ignore committed plist baselines", failures)
    for expected in ["*.local.xcconfig", "*.secrets.xcconfig", "*.local.plist", "*.secrets.plist", ".env"]:
        require(expected in gitignore, f".gitignore must include {expected}", failures)

    require(".PHONY: build check lint test" in makefile and "lint test build: check" in makefile,
            "Makefile must expose lint, test, build, and check gate targets",
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
        require("pulse list user guard" in content.lower(),
                f"{path} must document pulse list user guard",
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
    require("pulse list user guard" in changes.lower(),
            "CHANGES must record pulse list user guard",
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
    require("status: completed" in home_time_plan and "currentDigitsUserID" in home_time_plan and
            "successful Alamofire response" in home_time_plan,
            "home time submission guard plan must be completed and document both guards",
            failures)
    require("permissions:\n  contents: read" in workflow and "cancel-in-progress: true" in workflow and
            "runs-on: macos-15" in workflow and "timeout-minutes: 10" in workflow and
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow and
            "run: make check" in workflow,
            "Check workflow must stay pinned, read-only, and bounded",
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
