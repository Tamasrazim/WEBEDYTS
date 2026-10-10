#!/usr/bin/env python3
"""Check that a packaged WEBEDYTS app contains the real Chromium runtime."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MIB = 1024 * 1024


def installed_size(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        try:
            if path.is_file():
                total += path.stat().st_size
        except OSError:
            continue
    return total


def runtime_files(root: Path) -> list[Path]:
    checks = [
        root / "resources" / "app" / "index.html",
        root / "resources.pak",
        root / "icudtl.dat",
        root / "locales",
    ]

    if root.name.endswith(".app"):
        checks = [
            root / "Contents" / "Resources" / "app" / "index.html",
            root / "Contents" / "Frameworks" /
            "Chromium Embedded Framework.framework" / "Versions" / "A" /
            "Chromium Embedded Framework",
        ]
    else:
        checks.extend(
            [
                root / "libcef.dll",
                root / "libcef.so",
            ]
        )

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Staged output folder or .app bundle")
    parser.add_argument(
        "--minimum-mib",
        type=int,
        default=120,
        help="Warn below this installed size (default: 120 MiB)",
    )
    args = parser.parse_args()

    root = args.bundle.resolve()
    if not root.is_dir():
        print(f"Bundle directory not found: {root}", file=sys.stderr)
        return 2

    missing = [path for path in runtime_files(root) if not path.exists()]
    if missing:
        print("Required app or Chromium files are missing:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        return 2

    total = installed_size(root)
    print(f"Bundle: {root}")
    print(f"Installed footprint: {total / MIB:,.1f} MiB ({total:,} bytes)")

    if total < args.minimum_mib * MIB:
        print(
            f"Warning: footprint is below {args.minimum_mib} MiB. "
            "Check that the complete CEF runtime, locales, and resources are staged.",
            file=sys.stderr,
        )
    else:
        print("Chromium runtime checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
