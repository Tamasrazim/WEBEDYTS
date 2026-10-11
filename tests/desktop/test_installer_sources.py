#!/usr/bin/env python3
"""Source-level checks for WEBEDYTS platform installer definitions."""

from __future__ import annotations

import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PACKAGING = ROOT / "packaging"


class InstallerSourceTests(unittest.TestCase):
    def test_windows_setup_is_branded_and_per_user(self) -> None:
        source = (PACKAGING / "windows" / "WEBEDYTS.iss").read_text(encoding="utf-8")
        for expected in (
            "WizardStyle=modern",
            "PrivilegesRequired=lowest",
            r"DefaultDirName={localappdata}\Programs\WEBEDYTS",
            r"LicenseFile=..\..\LICENSE",
            r"SetupIconFile=..\branding\webedyts.ico",
            r"UninstallDisplayIcon={app}\WEBEDYTS.exe",
            "SolidCompression=yes",
            r'Filename: "{app}\WEBEDYTS.exe"',
            "WEBEDYTS-Setup-",
        ):
            self.assertIn(expected, source)

    def test_brand_icon_is_valid_svg_and_ico(self) -> None:
        root = ET.parse(PACKAGING / "branding" / "webedyts.svg").getroot()
        self.assertTrue(root.tag.endswith("svg"))
        ico = (PACKAGING / "branding" / "webedyts.ico").read_bytes()
        self.assertGreater(len(ico), 100)
        self.assertEqual(ico[:4], b"\x00\x00\x01\x00")

    def test_debian_package_preserves_runtime_and_sandbox(self) -> None:
        source = (PACKAGING / "linux" / "build-deb.sh").read_text(encoding="utf-8")
        for expected in (
            "resources/app/index.html",
            "chrome-sandbox",
            "dpkg-deb --build -Zxz -z5 --root-owner-group",
            "chmod 4755",
            "usr/share/applications/webedyts.desktop",
            "write-package-checksum.py",
        ):
            self.assertIn(expected, source)

    def test_macos_image_uses_drag_install_and_integrity_check(self) -> None:
        source = (PACKAGING / "macos" / "build-dmg.sh").read_text(encoding="utf-8")
        for expected in (
            'ln -s /Applications "$staging/Applications"',
            "hdiutil create",
            "hdiutil verify",
            "write-package-checksum.py",
            "not Developer ID signed or notarized yet",
        ):
            self.assertIn(expected, source)


if __name__ == "__main__":
    unittest.main()
