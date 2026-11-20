"""Verify the public baseline files or check the complete frozen research archive."""

import argparse
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name("baseline_sha256.csv")
FROZEN_MANIFEST_SHA256 = "b5042df83074e09180cef2fcc39ab47b2179f62c5453daf466f6283eea7cdc27"
PUBLIC_SCOPE = Path(__file__).with_name("public_baseline_scope.md")
REPLACED_ENTRY_POINTS = {"README.md", "README.zh-CN.md", "pytest.ini"}


def verify(archive_root=None):
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest() != FROZEN_MANIFEST_SHA256:
        raise ValueError("The frozen baseline manifest does not match its recorded SHA-256.")
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        entries = list(csv.DictReader(stream))

    public_checkout = archive_root is None and PUBLIC_SCOPE.is_file()
    root = ROOT if archive_root is None else Path(archive_root).resolve()
    errors = []
    checked = 0
    for row in entries:
        name = row["relative_path"]
        relative = Path(name)
        if public_checkout and (name in REPLACED_ENTRY_POINTS or
                                ("__pycache__" in relative.parts and relative.suffix == ".pyc")):
            continue
        checked += 1
        file = root / relative
        if not file.is_file():
            errors.append((name, "missing"))
        elif hashlib.sha256(file.read_bytes()).hexdigest() != row["sha256"]:
            errors.append((name, "changed"))

    scope = "PUBLIC_BASELINE_SUBSET" if public_checkout else "FULL_FROZEN_ARCHIVE"
    expected = 142 if public_checkout else 166
    if checked != expected:
        errors.append((scope, f"expected {expected} entries, checked {checked}"))
    return scope, checked, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, help="Path to the intact frozen LC1-main directory.")
    args = parser.parse_args()
    scope, checked, errors = verify(args.archive_root)
    print(f"SCOPE={scope} BASELINE_FILES_VERIFIED={checked - len(errors)} TOTAL={checked} ISSUES={len(errors)}")
    for name, reason in errors:
        print(name, reason)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
