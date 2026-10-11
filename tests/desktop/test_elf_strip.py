#!/usr/bin/env python3
"""Unit tests for ELF detection in the Linux runtime-strip helper."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PROJECT_ROOT / "desktop" / "tools" / "strip-elf-debug-symbols.py"
SPEC = importlib.util.spec_from_file_location("webedyts_elf_strip", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {SCRIPT}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ElfDetectionTests(unittest.TestCase):
    def test_finds_only_regular_elf_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "app").write_bytes(b"\x7fELF" + b"\x00" * 32)
            (root / "notes.txt").write_text("not a binary", encoding="utf-8")
            nested = root / "lib"
            nested.mkdir()
            (nested / "libcef.so").write_bytes(b"\x7fELF" + b"\x01" * 32)
            found = MODULE.find_elf_files(root)
            self.assertEqual(found, [root / "app", nested / "libcef.so"])

    def test_does_not_follow_symlink_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / "real-binary"
            binary.write_bytes(b"\x7fELF" + b"\x00" * 32)
            link = root / "linked-binary"
            try:
                link.symlink_to(binary)
            except OSError:
                self.skipTest("Symlink creation is unavailable on this runner")
            self.assertEqual(MODULE.find_elf_files(root), [binary])


if __name__ == "__main__":
    unittest.main()
