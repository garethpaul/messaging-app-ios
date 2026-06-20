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
EXPECTED_TEST_FILES = ["tests/test_check_baseline.py"]
EXPECTED_TEST_HASHES = {
    "tests/test_check_baseline.py": "72d3799ac722cb61216b7110afa0e95352e04af4dc60e4f5bb463631f43580c2",
}
EXPECTED_PROTECTED_HASHES = {
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
    ".github/workflows/check.yml": "284a336a4bb5a9c4981ef3e1dd7dec5e2e63a3a80c7ed098c709e3a519331350",
    "Makefile": "a5d2fe9341ac00c7f297796cfac1576b9c3153537a5011b0facef20c668ad313",
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


def git_output(*arguments):
    return subprocess.run(
        ["git", *arguments],
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
        subprocess.run(["git", "init", "--quiet"], cwd=repository_copy, check=True)
        subprocess.run(["git", "add", "--all"], cwd=repository_copy, check=True)
        subprocess.run(
            ["git", "-c", "user.name=validation", "-c", "user.email=validation@example.invalid", "commit", "--quiet", "-m", "snapshot"],
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
