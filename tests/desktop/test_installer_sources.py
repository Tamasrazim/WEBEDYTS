#!/usr/bin/env python3

# Checks the installer definitions and the files they are expected to include.

"""Source-level checks for WEBEDYTS platform installer definitions."""

from __future__ import annotations

import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PACKAGING = ROOT / "packaging"


class InstallerSourceTests(unittest.TestCase):
    def test_release_version_has_one_source_of_truth(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")

        cmake = (ROOT / "desktop" / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn('file(STRINGS "${CMAKE_SOURCE_DIR}/VERSION" WEBEDYTS_VERSION LIMIT_COUNT 1)', cmake)

        native_workflow = (ROOT / ".github" / "workflows" / "native-desktop-build.yml").read_text(encoding="utf-8")
        self.assertIn("WEBEDYTS_VERSION=$APP_VERSION", native_workflow)
        self.assertIn('      - "v*"', native_workflow)
        self.assertNotIn("/DAppVersion=0.1.0", native_workflow)

    def test_official_release_is_gated_and_draft_only(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "native-desktop-build.yml").read_text(encoding="utf-8")
        self.assertIn("needs: build", workflow)
        self.assertIn("needs.build.result == \'success\'", workflow)
        self.assertIn("--verify-tag", workflow)
        self.assertIn("--draft", workflow)
        self.assertIn("--prerelease", workflow)

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


    def test_windows_shell_uses_native_window_path(self) -> None:
        source = (ROOT / "desktop" / "src" / "webedyts_desktop.cpp").read_text(encoding="utf-8")
        self.assertIn("CefBrowserHost::CreateBrowser", source)
        self.assertIn("window_info.SetAsChild(window, browser_rect)", source)
        self.assertIn("case WM_SIZE:", source)
        self.assertIn("case WM_CLOSE:", source)
        self.assertIn("#if !defined(_WIN32)\n      // CEF Views powers the Linux/macOS shell.", source)
        self.assertIn("CreateNativeMainWindow(", source)

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
