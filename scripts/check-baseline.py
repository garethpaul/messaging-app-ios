#!/usr/bin/env python3
from pathlib import Path
import json
import plistlib
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
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "Podfile",
        "Podfile.lock",
        "docs/plans/2026-06-08-messaging-app-ios-baseline.md",
        "docs/readme-overview.svg",
        "scripts/check-baseline.py",
        "WhineLocation/Info.plist",
        "WhineLocation/ServiceKeys.xcconfig.example",
        "WhineLocation/User.swift",
        "WhineLocation/ShareLocation.swift",
        "WhineLocation/CoreLocationController.swift",
        "WhineLocation/HomeTimeViewController.swift",
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
    share_location = read("WhineLocation/ShareLocation.swift")
    home_time = read("WhineLocation/HomeTimeViewController.swift")
    core_location = read("WhineLocation/CoreLocationController.swift")
    readme = read("README.md")
    vision = read("VISION.md")
    security = read("SECURITY.md")
    changes = read("CHANGES.md")

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
    require('Alamofire.request(.POST, "https://requestlabs.appspot.com/whine/location"' in share_location,
            "location sharing must use POST",
            failures)
    require('Alamofire.request(.POST, getInfo("newHometimeUrl")' in home_time,
            "hometime updates must use POST",
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

    for forbidden in ["Info.plist\n", "*.plist"]:
        require(forbidden not in gitignore, ".gitignore must not ignore committed plist baselines", failures)
    for expected in ["*.local.xcconfig", "*.secrets.xcconfig", "*.local.plist", "*.secrets.plist", ".env"]:
        require(expected in gitignore, f".gitignore must include {expected}", failures)

    tracked = tracked_files()
    generated = [path for path in tracked if "xcuserdata" in path or path.endswith(".xcuserstate")]
    require(not generated, "generated Xcode user state must not be tracked: " + ", ".join(generated), failures)

    for path, content in [("README.md", readme), ("VISION.md", vision), ("SECURITY.md", security)]:
        require("make check" in content and "ServiceKeys.xcconfig.example" in content,
                f"{path} must document static checks and local credential setup",
                failures)
        require("message" in content.lower() and "location" in content.lower(),
                f"{path} must document messaging/location privacy posture",
                failures)
    require("Fabric/Crashlytics" in changes and "POST" in changes,
            "CHANGES must record credential and request-method hardening",
            failures)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Messaging app iOS baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
