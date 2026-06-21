#!/usr/bin/env python3
from _hashlib import openssl_sha256
from pathlib import Path
import argparse
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HASHES = {
    ".github/workflows/check.yml": "883dd06542e5e21d21fc87885ac198101d78ae9e2e9250255ea9a6190131066c",
    "Makefile": "184cc525c798c29514e616f29b219fa2b951d911d857b1ddef1f0eed412f32f6",
    "scripts/run-isolated-tests.py": "0594d7c91ae5585153f5732d13a396d5e53226a1683d79914ea0c532c8407a19",
}


def sha256_file(path):
    return openssl_sha256(path.read_bytes()).hexdigest()


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
    if failures:
        for failure in failures:
            print("validation-root: " + failure, file=sys.stderr)
        return 1
    print("Messaging app iOS validation chain authenticated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
