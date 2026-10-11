#!/usr/bin/env python3
"""Remove ELF debug sections from staged Linux runtime binaries before packaging.

This preserves dynamic symbols and relocations needed to run the application. It
does not compress assets, remove runtime libraries, or add filler files.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ELF_MAGIC = b"\x7fELF"


def find_elf_files(root: Path) -> list[Path]:
    """Return regular ELF files below root without following symlinks."""
    result: list[Path] = []
    for path in root.rglob("*"):
        try:
            if path.is_symlink() or not path.is_file():
                continue
            with path.open("rb") as stream:
                if stream.read(4) == ELF_MAGIC:
                    result.append(path)
        except OSError as error:
            raise RuntimeError(f"Could not inspect runtime file {path}: {error}") from error
    return sorted(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path, help="Staged Linux CEF runtime directory")
    args = parser.parse_args()
    root = args.runtime.resolve()
    if not root.is_dir():
        print(f"Runtime directory not found: {root}", file=sys.stderr)
        return 2
    strip = shutil.which("strip")
    if not strip:
        print("The GNU-compatible 'strip' utility is required.", file=sys.stderr)
        return 2

    try:
        binaries = find_elf_files(root)
        if not binaries:
            print(f"No ELF binaries were found in {root}.", file=sys.stderr)
            return 2
        before = sum(path.stat().st_size for path in binaries)
        for binary in binaries:
            result = subprocess.run(
                [strip, "--strip-debug", str(binary)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode:
                details = (result.stderr or result.stdout).strip()
                raise RuntimeError(f"strip failed for {binary}: {details}")
        after = sum(path.stat().st_size for path in binaries)
    except (OSError, RuntimeError) as error:
        print(f"Could not strip ELF debug sections: {error}", file=sys.stderr)
        return 3

    saved = before - after
    print(
        f"Stripped debug sections from {len(binaries)} ELF runtime files; "
        f"saved {saved / (1024 * 1024):,.1f} MiB "
        f"({max(saved, 0):,} bytes)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
