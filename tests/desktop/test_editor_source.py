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

    def test_animation_presets_are_available_in_both_preview_modes(self) -> None:
        presets = (
            "fade", "slide", "pop", "pulse", "wiggle", "blur",
            "rise", "drift", "rotate", "spring", "wipe",
            "float", "glow", "flip", "zoom",
        )
        for preset in presets:
            self.assertIn(f'data-preset="{preset}"', self.source)
            self.assertIn(f'value="{preset}"', self.source)
            self.assertIn(f"'{preset}'", self.source)

        for keyframe in (
            "@keyframes wiRise", "@keyframes wiDrift", "@keyframes wiRotate",
            "@keyframes wiSpring", "@keyframes wiWipe", "@keyframes wiFloat",
            "@keyframes wiGlow", "@keyframes wiFlip", "@keyframes wiZoom",
            ".wi-anim-rise", ".wi-anim-wipe", ".wi-anim-flip",
        ):
            self.assertIn(keyframe, self.source)

        self.assertIn(
            ".asset-card:focus-visible { outline: 2px solid #eee;",
            self.source,
        )

        # The library should demonstrate the selected motion before it is applied.
        for preset in presets:
            self.assertIn(
                f'.asset-card[data-preset="{preset}"]:is(:hover,:focus-visible) .anim-preview::before',
                self.source,
            )

    def test_zip_export_uses_canonical_serializer(self) -> None:
        start = self.source.index("async function exportImportedProject()")
        end = self.source.index("document.getElementById('import-media')", start)
        export_code = self.source[start:end]

        self.assertIn(
            "elementsIncludingRoot(importedDoc.documentElement, '[data-webedyts-asset-path]')",
            export_code,
        )
        self.assertIn("let output = serializeImportedPage();", export_code)
        self.assertNotIn(
            "const clone = importedDoc.documentElement.cloneNode(true)",
            export_code,
        )
        self.assertIn("attribute.name === 'data-webedyts-asset-path'", self.source)
        self.assertIn("attribute.name === 'data-webedyts-asset-style'", self.source)

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
            "function elementsIncludingRoot(root, selector)",
            "function serializeImportedPage()",
            "runPreviewSafetyRegressionTests()",
            "WEBEDYTS_PREVIEW_TEST_RESULT:",
        ):
            self.assertIn(expected, self.source)


if __name__ == "__main__":
    unittest.main()
