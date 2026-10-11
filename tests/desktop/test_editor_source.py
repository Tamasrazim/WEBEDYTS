#!/usr/bin/env python3
"""Fast checks for the editor shipped inside the native application."""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EDITOR_PATH = PROJECT_ROOT / "desktop" / "resources" / "app" / "index.html"


class EditorMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "id" and value:
                self.ids.append(value)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


class EditorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = EDITOR_PATH.read_text(encoding="utf-8")

    def test_native_build_uses_the_shipped_editor_source(self) -> None:
        cmake = (PROJECT_ROOT / "desktop" / "CMakeLists.txt").read_text(encoding="utf-8")
        native_source = (PROJECT_ROOT / "desktop" / "src" / "webedyts_desktop.cpp").read_text(encoding="utf-8")

        self.assertIn("resources/app/index.html", cmake)
        self.assertNotIn("prototype/index.html", cmake)
        self.assertIn("forward slashes in file URLs", native_source)
        self.assertIn("CefExecuteProcess(main_args, app, sandbox_info)", native_source)
        self.assertIn("CefInitialize(main_args, settings, app, sandbox_info)", native_source)
        self.assertIn("app->SetStartUrl(FileUrl(editor_html))", native_source)
    def test_editor_html_has_unique_ids(self) -> None:
        parser = EditorMarkupParser()
        parser.feed(self.source)
        duplicates = sorted(
            value for value in set(parser.ids) if parser.ids.count(value) > 1
        )
        self.assertEqual(duplicates, [], f"Duplicate HTML IDs: {duplicates}")

    def test_inline_editor_script_passes_node_syntax_check(self) -> None:
        scripts = re.findall(
            r"<script\b[^>]*>([\s\S]*?)</script\s*>",
            self.source,
            flags=re.IGNORECASE,
        )
        self.assertEqual(len(scripts), 1, "Expected one inline editor script")

        with tempfile.TemporaryDirectory() as temp:
            script_path = Path(temp) / "editor.js"
            script_path.write_text(scripts[0], encoding="utf-8")
            result = subprocess.run(
                ["node", "--check", str(script_path)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(
            result.returncode,
            0,
            f"JavaScript syntax check failed:\n{result.stdout}\n{result.stderr}",
        )


    def test_imported_preview_neutralizes_active_content_and_preserves_export(self) -> None:
        for expected in (
            "setAttribute('sandbox', 'allow-same-origin')",
            "script-src 'none'",
            "suspendUnsafePreviewMarkup(parsed, Boolean(preserveEditorMetadata))",
            "restorePreviewSafetyEdits(clone)",
            "data-webedyts-preview-original-attrs",
            "data-webedyts-preview-original-node",
            "meta-refresh",
            "isEventHandler",
            "isScriptUrl",
        ):
            self.assertIn(expected, self.source)

    def test_motion_settings_and_panel_controls_are_accessible(self) -> None:
        for expected in (
            "@media (prefers-reduced-motion: reduce)",
            "toast.setAttribute('aria-live', 'polite')",
            'id="toggle-outliner-panel"',
            'id="toggle-details-panel"',
            "Show / hide page outliner",
            "Show / hide details panel",
        ):
            self.assertIn(expected, self.source)
        self.assertNotIn("Minimize concept window", self.source)
        self.assertNotIn("Maximize concept window", self.source)

    def test_imported_element_actions_are_wired(self) -> None:
        for expected in (
            'id="duplicate-element"',
            'id="delete-element"',
            'id="prop-height"',
            'id="prop-display"',
            'id="prop-margin"',
            'id="prop-font-weight"',
            "bindSelectStyle('prop-display', 'display')",
            "function duplicateSelectedElement()",
            "function deleteSelectedElement()",
            "document.getElementById('duplicate-element').addEventListener",
            "document.getElementById('delete-element').addEventListener",
            "node === importedDoc.body",
        ):
            self.assertIn(expected, self.source)


if __name__ == "__main__":
    unittest.main()
