#!/usr/bin/env python3
"""Tests for the native application's staged-runtime checker."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = PROJECT_ROOT / "desktop" / "tools" / "report-bundle-size.py"

spec = importlib.util.spec_from_file_location("webedyts_bundle_checker", CHECKER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load bundle checker: {CHECKER_PATH}")

checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def touch(path: Path, contents: bytes = b"runtime file") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(contents)


class BundleSizeTests(unittest.TestCase):
    def run_checker(
        self,
        bundle: Path,
        minimum_mib: int = 0,
        fail_below_minimum: bool = False,
    ) -> tuple[int, str, str]:
        old_argv = sys.argv
        stdout = io.StringIO()
        stderr = io.StringIO()
        sys.argv = [
            str(CHECKER_PATH),
            str(bundle),
            "--minimum-mib",
            str(minimum_mib),
        ]
        if fail_below_minimum:
            sys.argv.append("--fail-below-minimum")
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = checker.main()
        finally:
            sys.argv = old_argv
        return result, stdout.getvalue(), stderr.getvalue()

    def test_cef_downloader_rejects_malformed_versions_before_network_access(self) -> None:
        module_path = PROJECT_ROOT / "desktop" / "cmake" / "DownloadCEF.cmake"
        test_script = PROJECT_ROOT / "tests" / "desktop" / "test_cef_invalid_version.cmake"
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [
                    "cmake",
                    f"-DCEF_TEST_DOWNLOAD_DIRECTORY={temp}",
                    "-DCEF_TEST_VERSION=not-a-cef-version",
                    f"-DCEF_TEST_MODULE={module_path}",
                    "-P",
                    str(test_script),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CEF version must look like", result.stderr)

    def test_linux_or_windows_runtime_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            touch(root / "resources" / "app" / "index.html", b"<html></html>")
            touch(root / "resources.pak")
            touch(root / "icudtl.dat")
            touch(root / "locales" / "en-US.pak")
            touch(root / "libcef.so")

            result, output, error = self.run_checker(root)

            self.assertEqual(result, 0)
            self.assertIn("Installed footprint:", output)
            self.assertIn("Chromium runtime checks passed.", output)
            self.assertEqual(error, "")

    def test_missing_core_runtime_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            touch(root / "resources" / "app" / "index.html", b"<html></html>")
            touch(root / "icudtl.dat")
            (root / "locales").mkdir()
            touch(root / "libcef.dll")

            result, output, error = self.run_checker(root)

            self.assertEqual(result, 2)
            self.assertIn("Required app or Chromium files are missing:", error)
            self.assertIn("resources.pak", error)
            self.assertEqual(output, "")

    def test_package_can_reject_a_runtime_below_the_minimum(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            touch(root / "resources" / "app" / "index.html", b"<html></html>")
            touch(root / "resources.pak")
            touch(root / "icudtl.dat")
            touch(root / "locales" / "en-US.pak")
            touch(root / "libcef.so")

            result, output, error = self.run_checker(
                root, minimum_mib=1, fail_below_minimum=True
            )

            self.assertEqual(result, 3)
            self.assertIn("Installed footprint:", output)
            self.assertIn("below 1 MiB", error)

    def test_default_package_size_threshold_is_200_mib(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            touch(root / "resources" / "app" / "index.html", b"<html></html>")
            touch(root / "resources.pak")
            touch(root / "icudtl.dat")
            touch(root / "locales" / "en-US.pak")
            touch(root / "libcef.so")

            old_argv = sys.argv
            stdout = io.StringIO()
            stderr = io.StringIO()
            sys.argv = [str(CHECKER_PATH), str(root), "--fail-below-minimum"]
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = checker.main()
            finally:
                sys.argv = old_argv

            self.assertEqual(result, 3)
            self.assertIn("below 200 MiB", stderr.getvalue())

    def test_macos_checks_framework_resources(self) -> None:
        with tempfile.TemporaryDirectory(suffix=".app") as temp:
            root = Path(temp)
            resources = (
                root / "Contents" / "Frameworks" /
                "Chromium Embedded Framework.framework" / "Versions" / "A" /
                "Resources"
            )
            touch(root / "Contents" / "Resources" / "app" / "index.html")
            touch(
                resources.parent / "Chromium Embedded Framework",
                b"framework binary",
            )
            touch(resources / "icudtl.dat")
            touch(resources / "en.lproj" / "locale.pak")
            touch(resources / "cef.pak")

            result, output, error = self.run_checker(root)

            self.assertEqual(result, 0)
            self.assertIn("Chromium runtime checks passed.", output)
            self.assertEqual(error, "")

    @unittest.skipIf(os.name == "nt", "Symlink creation may require Windows developer mode")
    def test_bundle_size_does_not_count_symlink_targets_twice(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual_dir = root / "Versions" / "A" / "Resources"
            touch(actual_dir / "resource.pak", b"abc")
            (root / "Resources").symlink_to(actual_dir, target_is_directory=True)

            self.assertEqual(checker.installed_size(root), len(b"abc"))


if __name__ == "__main__":
    unittest.main()
