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
            if path.is_file() and not path.is_symlink():
                total += path.stat().st_size
        except OSError:
            continue
    return total


def runtime_files(root: Path) -> tuple[list[Path], list[tuple[Path, ...]], Path | None]:
    required = [
        root / "resources" / "app" / "index.html",
        root / "resources.pak",
        root / "icudtl.dat",
        root / "locales",
    ]
    alternatives: list[tuple[Path, ...]] = []
    pak_directory = root

    if root.name.endswith(".app"):
        framework = (
            root / "Contents" / "Frameworks" /
            "Chromium Embedded Framework.framework" / "Versions" / "A"
        )
        pak_directory = framework / "Resources"
        required = [
            root / "Contents" / "Resources" / "app" / "index.html",
            framework / "Chromium Embedded Framework",
            pak_directory / "icudtl.dat",
            pak_directory / "locales",
        ]
        return required, alternatives, pak_directory

    alternatives.append((root / "libcef.dll", root / "libcef.so"))
    return required, alternatives, pak_directory


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

    required, alternatives, pak_directory = runtime_files(root)
    missing = [path for path in required if not path.exists()]
    missing_groups = [
        group for group in alternatives
        if not any(path.is_file() for path in group)
    ]
    missing_packs = not pak_directory or not any(pak_directory.glob("*.pak"))
    if missing or missing_groups or missing_packs:
        print("Required app or Chromium files are missing:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        for group in missing_groups:
            print("  - one of: " + ", ".join(str(path) for path in group), file=sys.stderr)
        if missing_packs:
            print(f"  - at least one Chromium .pak resource in {pak_directory}", file=sys.stderr)
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
