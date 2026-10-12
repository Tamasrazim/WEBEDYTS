# Changelog

All notable, user-facing changes to WEBEDYTS are recorded here. Release entries are added only after a release has actually been published.

## Unreleased

- Add Ctrl/Cmd+Shift+S as a direct Export draft shortcut, with a regression check that avoids starting a real download in tests.
- Nudge the selected page element with arrow keys (1 px) or Shift+Arrow (10 px), with keyboard help and browser regression coverage.
- Add bounded local recovery for unsaved single-page edits, a File-menu privacy toggle that clears stored drafts when disabled, and a native regression that exercises backup restoration.
- Route single-page ZIP exports through the same safe serializer as plain HTML exports, restoring original suspended markup and stripping editor/media metadata before packaging.
- Add a regression check to keep ZIP and plain HTML export cleanup aligned.

- Expand the animation drawer from six to fifteen searchable presets, including rise, drift, spring, wipe, float, glow, flip, and zoom; wire the same effects into the imported-page preview and the bundled demo, with reduced-motion handling.
- Animate each preset thumbnail only while its card is hovered or keyboard-focused, so motion can be previewed without keeping the entire library in constant motion.
- Make panel controls usable from the interface and remove decorative window buttons that did not control the native window.
- Respect the operating system's reduced-motion preference and announce editor messages to assistive technology.
- Neutralize imported inline event handlers, script URLs, base elements, and refresh redirects inside the isolated preview while preserving original markup for export.
- Include the HTML root during preview sanitization and export restoration; add a native-browser regression run for import, edit, duplicate, delete, undo, and export round-tripping.
- Remove ELF debug sections from the Linux runtime before testing and packaging.
- Extend SHA-256 tests with multi-block and million-byte input vectors.
- Keep the first public release gated on manual editor-workflow validation and platform signing requirements.
