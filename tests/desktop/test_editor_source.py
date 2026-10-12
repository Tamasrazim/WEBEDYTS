#!/usr/bin/env python3
# Checks important parts of the editor interface source without needing to launch the full desktop app.
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


    def test_preview_test_url_is_built_after_cef_reads_command_line(self) -> None:
        # CEF processes switches during startup, so build the final URL afterwards.
        native_source = (PROJECT_ROOT / "desktop" / "src" / "webedyts_desktop.cpp").read_text(
            encoding="utf-8"
        )
        setter_start = native_source.index("void SetStartUrl(const CefString& start_url)")
        setter_end = native_source.index("CefString GetLaunchUrl() const", setter_start)
        setter = native_source[setter_start:setter_end]
        self.assertIn("start_url_ = start_url;", setter)
        self.assertNotIn("webedyts_preview_safety_test=1", setter)

        launch_start = native_source.index("CefString GetLaunchUrl() const")
        launch_end = native_source.index(
            "CefRefPtr<CefBrowserProcessHandler> GetBrowserProcessHandler()", launch_start
        )
        launch_method = native_source[launch_start:launch_end]
        self.assertIn("preview_safety_test_", launch_method)
        self.assertIn("webedyts_preview_safety_test=1", launch_method)

        context_start = native_source.index("void OnContextInitialized() override")
        context_end = native_source.index("\n private:", context_start)
        context = native_source[context_start:context_end]
        self.assertIn("const CefString launch_url = GetLaunchUrl();", context)
        self.assertIn(
            "new EditorClient(smoke_test_, smoke_marker_path_, launch_url)", context
        )
        self.assertIn("            launch_url));", context)

    def test_macos_smoke_test_closes_the_window_after_the_browser_callback(self) -> None:
        # Deferring close avoids re-entering CEF window teardown from OnTitleChange.
        native_source = (PROJECT_ROOT / "desktop" / "src" / "webedyts_desktop.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn('#include "include/cef_task.h"', native_source)
        self.assertIn("class CloseSmokeTestWindowTask final : public CefTask", native_source)
        self.assertIn("CefPostTask(TID_UI, new CloseSmokeTestWindowTask());", native_source)

        close_start = native_source.index("void FinishSmokeTest(")
        close_end = native_source.index("bool smoke_test_ = false;", close_start)
        close_handler = native_source[close_start:close_end]
        self.assertIn("#if defined(__APPLE__)", close_handler)
        self.assertIn("Closing inside OnTitleChange can re-enter CEF window teardown", close_handler)

    def test_imported_preview_neutralizes_active_content_and_preserves_export(self) -> None:
        for expected in (
            "setAttribute('sandbox', 'allow-same-origin')",
            "script-src 'none'",
            "suspendUnsafePreviewMarkup(parsed, Boolean(preserveEditorMetadata))",
            "restorePreviewSafetyEdits(clone)",
            "data-webedyts-preview-original-attrs",
            "data-webedyts-preview-original-node",
            "data-webedyts-preview-original-html",
            "parsed.createElement('meta')",
            "placeholder.setAttribute('data-webedyts-preview-original-html', node.outerHTML);",
            "elementsIncludingRoot(clone, '[data-webedyts-preview-original-node]')",
            "holder.innerHTML = node.getAttribute('data-webedyts-preview-original-html') || '';",
            "meta-refresh",
            "isEventHandler",
            "isScriptUrl",
            "prop-animation-duration",
            "prop-animation-delay",
            "prop-animation-easing",
            "cssTimeToMilliseconds",
            "bindAnimationMilliseconds('prop-animation-duration', 'animationDuration', 1, 10000)",
            "bindAnimationMilliseconds('prop-animation-delay', 'animationDelay', 0, 30000)",
            "node.style.animationTimingFunction = saved.animationTimingFunction || '';",
        ):
            self.assertIn(expected, self.source)

    def test_local_recovery_copy_is_bounded_and_avoids_temporary_project_assets(self) -> None:
        # Recovery helps only when the restored page can work without missing local files.
        for expected in (
            "webedyts.recovery.v1",
            "RECOVERY_ENABLED_STORAGE_KEY = 'webedyts.recovery.enabled.v1'",
            "function isAutomaticRecoveryEnabled()",
            "function toggleRecoveryPreference()",
            "Automatic local recovery', shortcut: '', action: 'toggle-recovery'",
            "action === 'toggle-recovery'",
            "RECOVERY_MAX_CHARACTERS = 1500000",
            "RECOVERY_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000",
            "function saveRecoveryCopyNow()",
            "if (projectMode)",
            "function hasTemporaryMediaReference(markup)",
            "hasTemporaryMediaReference(data.html)",
            "data.html",
            "function scheduleRecoverySave()",
            "window.confirm('WEBEDYTS found unfinished work saved on this computer",
            "function offerRecoveryCopy(allowDuringRegressionTest)",
            "scheduleRecoverySave();",
            "saveRecoveryCopyNow(), 'The local recovery copy did not store unsaved edits.'",
            "const originalConfirm = window.confirm",
            "window.confirm = function () { return true; };",
            "offerRecoveryCopy();",
            "offerRecoveryCopy(true);",
            "Local recovery did not restore the previous editing snapshot.",
            "Turning recovery off left an old recovery copy.",
            "clearRecoveryCopy();",
        ):
            self.assertIn(expected, self.source)

    def test_selected_elements_can_be_nudged_with_arrow_keys(self) -> None:
        # Position adjustments should be possible without dragging a mouse.
        for expected in (
            "function nudgeSelectedElement(dx, dy)",
            "const step = event.shiftKey ? 10 : 1;",
            "nudgeSelectedElement(direction[0] * step, direction[1] * step)",
            "The right-arrow nudge did not move the selected element by one pixel.",
            "The shifted down-arrow nudge did not move the selected element by ten pixels.",
            "Arrow keys nudge 1 px · Shift+Arrow nudge 10 px",
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

        # Switching drawer tabs must not hide the other nine supported presets.
        drawer_start = self.source.index("if (mode === 'animations')")
        drawer_end = self.source.index("} else if (mode === 'components')", drawer_start)
        drawer_source = self.source[drawer_start:drawer_end]
        for preset in presets:
            self.assertIn(f"['{preset}'", drawer_source)

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

    def test_animation_timing_controls_are_saved_and_accessible(self) -> None:
        # Timing changes should persist in the normal session format and remain exportable.
        for expected in (
            'id="prop-animation-duration"',
            'id="prop-animation-delay"',
            'id="prop-animation-easing"',
            "animationDuration: node.style.animationDuration || ''",
            "animationDelay: node.style.animationDelay || ''",
            "animationTimingFunction: node.style.animationTimingFunction || ''",
            "node.style.animationDuration = saved.animationDuration || '';",
            "node.style.animationDelay = saved.animationDelay || '';",
            "bindSelectStyle('prop-animation-easing', 'animationTimingFunction');",
            "The timing fields must change the real animation and remain in exported HTML.",
            "Export lost the custom animation duration.",
            "Export lost the custom animation delay.",
            "Export lost the custom animation timing.",
        ):
            self.assertIn(expected, self.source)

    def test_animation_drawer_gives_clear_selection_feedback(self) -> None:
        # A clicked preset should remain visibly selected after its animation is applied.
        start = self.source.index("function bindPresetCards()")
        end = self.source.index("document.getElementById('toggle-drawer')", start)
        binding = self.source[start:end]
        self.assertIn("propertyAnimation.value = animation;", binding)
        self.assertIn("syncPresetSelection();", binding)

        apply_start = self.source.index("document.getElementById('apply-animation').addEventListener('click'")
        apply_end = self.source.index("document.querySelectorAll('[data-preset]')", apply_start)
        apply_handler = self.source[apply_start:apply_end]
        self.assertIn("syncPresetSelection();", apply_handler)

        selection_start = self.source.index("function syncPresetSelection()")
        selection_end = self.source.index("function saveHistory()", selection_start)
        selection = self.source[selection_start:selection_end]
        self.assertIn("Boolean(animation) && card.dataset.preset === animation", selection)

        select_start = self.source.index("function selectNode(id)")
        select_end = self.source.index("function syncPresetSelection()", select_start)
        select_node = self.source[select_start:select_end]
        self.assertIn("syncPresetSelection();", select_node)

        card_start = self.source.index("function makePresetCard(item)")
        card_end = self.source.index("function makeSimpleCard(item)", card_start)
        card_builder = self.source[card_start:card_end]
        self.assertIn("button.type = 'button';", card_builder)

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
