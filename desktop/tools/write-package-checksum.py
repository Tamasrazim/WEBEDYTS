#!/usr/bin/env python3
# Writes a SHA-256 checksum for a finished package so the downloaded file can be checked for accidental damage.
"""Write a SHA-256 sidecar for a completed WEBEDYTS desktop archive."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

CHUNK_SIZE = 8 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while True:
            chunk = source.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Completed ZIP or tar.gz archive")
    args = parser.parse_args()

    archive = args.archive.resolve()
    if not archive.is_file():
        print(f"Archive not found: {archive}", file=sys.stderr)
        return 2

    try:
        checksum = sha256_file(archive)
        sidecar = archive.with_name(archive.name + ".sha256")
        sidecar.write_text(
            f"{checksum}  {archive.name}\n",
            encoding="utf-8",
        )
    except OSError as error:
        print(f"Could not write archive checksum: {error}", file=sys.stderr)
        return 3

    print(f"SHA-256: {checksum}")
    print(f"Checksum file: {sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
