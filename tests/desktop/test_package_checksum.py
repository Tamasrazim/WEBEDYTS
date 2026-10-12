# Verifies the package checksum file is written correctly and can be used to detect changes to a built package.

#!/usr/bin/env python3
"""Tests for desktop archive checksum generation."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKSUM_TOOL = PROJECT_ROOT / "desktop" / "tools" / "write-package-checksum.py"


class PackageChecksumTests(unittest.TestCase):
    def test_checksum_sidecar_matches_archive_bytes(self) -> None:
        payload = (b"WEBEDYTS desktop package test\n" * 4096) + bytes(range(256))
        expected = hashlib.sha256(payload).hexdigest()

        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "WEBEDYTS-test.tar.gz"
            archive.write_bytes(payload)

            result = subprocess.run(
                [sys.executable, str(CHECKSUM_TOOL), str(archive)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"SHA-256: {expected}", result.stdout)
            sidecar = archive.with_name(archive.name + ".sha256")
            self.assertEqual(sidecar.read_text(encoding="utf-8"), f"{expected}  {archive.name}\n")

    def test_missing_archive_returns_a_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "missing.zip"
            result = subprocess.run(
                [sys.executable, str(CHECKSUM_TOOL), str(archive)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Archive not found:", result.stderr)


if __name__ == "__main__":
    unittest.main()
