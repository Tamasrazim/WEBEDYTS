# WEBEDYTS

**A cross-platform desktop design application for visually editing and rebuilding websites without hand-editing HTML, CSS, or JavaScript.**

WEBEDYTS is planned as a real, installable desktop application for Windows, Linux, and macOS—not merely a web page hosted in a browser. It will open website folders and supported project archives through native file pickers, inspect their pages and assets, and let users redesign them through a visual canvas. Users should be able to select an element, change its text, position, size, spacing, style, or animation, preview the result across screen sizes, and export the updated website project.

The goal is to make website redesign accessible to people who think visually rather than in code, while keeping the exported project usable and inspectable by developers.

> **Project status:** WEBEDYTS is at the specification stage; the desktop application has not been implemented yet. This README describes the intended product and platform targets, not features already available. Features will be marked as implemented only after they exist and have been tested.

## The idea

Redesigning an existing website often means manually editing markup, stylesheets, scripts, and asset paths—or rebuilding the page in a separate design tool and then recreating it in code. WEBEDYTS aims to provide a visual alternative.

Open a site project or create a blank one. The editor should display the actual page in a canvas, let the user select UI elements directly, and expose visual controls for changing the page. A change made in the editor should update the project files without requiring the user to write code.

The ambition is not merely to edit an HTML file. It is to offer a complete visual website-editing workflow, including layout, responsive behavior, assets, animation, preview, history, and export.

## Core principles

- **Visual-first editing:** Users work with the rendered page, selection handles, panels, and controls instead of having to edit source code manually.
- **Preserve the original project:** Imported projects should remain intact unless the user deliberately changes them. Backups, undo, and clear change tracking are essential.
- **No-code workflow:** Text, layout, styling, element order, and supported animations should be editable through the interface. Generated code is an implementation detail, not a requirement for the user.
- **Real website output:** The result should be an exportable website project—not just a screenshot, mockup, or locked-in image.
- **Searchable animation library:** Presets should be discoverable by natural keywords, categories, properties, and use cases.
- **Responsive by design:** Users should be able to inspect and tune desktop, tablet, and mobile layouts.
- **Honest compatibility:** Unsupported or risky project structures should be reported clearly instead of silently breaking the page.
- **Native desktop application:** The app should install and launch directly on each supported operating system, use OS file dialogs, and provide platform-appropriate packages.
- **Local control:** Users should know which project files are opened, changed, and exported.

## Planned features

### 1. Open, import, and create projects

WEBEDYTS is intended to support two main starting points.

**Edit an existing website**
- Open a local website folder or supported project archive.
- Identify HTML pages, stylesheets, scripts, images, fonts, icons, and other referenced assets.
- Choose an entry page such as index.html.
- Inspect the rendered page and its available elements.
- Keep a recoverable original copy before making changes.

**Create a website from scratch**
- Start with a blank canvas or a starter layout.
- Add sections and UI elements using visual controls.
- Build navigation, headers, hero areas, cards, galleries, forms, footers, and other common page structures.
- Apply themes, reusable components, and animation presets.
- Export the project as a website.

Because this is a desktop application, users can choose local project folders and files through OS-provided file dialogs and grant the app access to the selected locations. A remote URL alone still does not give the application permission to rewrite a website on its server. Remote-site editing must use a supported download/import workflow or an authorized integration; the original online site will not be changed automatically.

### 2. Visual page editor

The main workspace should be built around an interactive page canvas.

Expected editing operations include:
- Select elements directly on the page.
- Change text and supported content in context.
- Move, resize, align, distribute, group, and reorder elements.
- Adjust margins, padding, gaps, positioning, sizing, colors, borders, shadows, and typography.
- Change backgrounds, images, icons, and other supported assets.
- Duplicate, delete, hide, lock, group, or rename elements.
- Adjust stacking order and inspect parent-child relationships.
- Edit links and common element properties through forms.
- Undo and redo changes.
- Preview changes without publishing them to a live site.

The editor should provide sensible controls for non-technical users while offering optional advanced settings when needed.

### 3. Structure and layers panel

A visual layers panel should represent the page's element hierarchy and help users select items that are difficult to click directly on the canvas.

Planned capabilities:
- A navigable element tree.
- Search and selection by element name or visible text.
- Reordering where structurally safe.
- Parent and child selection.
- Visibility and locking controls.
- Clear indicators for elements that are detected but not safely editable.
- A way to identify where an element's styling comes from when the project structure permits it.

The panel should help users understand a page without requiring them to read its source code.

### 4. Large, searchable animation preset library

Animation discovery is a major part of the product concept. The long-term goal is a library containing **thousands of distinct presets**, searchable with keywords instead of requiring users to create animation code themselves.

Examples of searchable terms:
- fade, slide, reveal, scale, rotate, blur
- hover, click, scroll, entrance, exit, loop
- text, heading, button, card, image, background
- smooth, subtle, energetic, elastic, cinematic
- parallax, stagger, morph, spring, wave, glitch

Planned library tools:
- Keyword search, tags, categories, and filters.
- Live demonstrations and preview-before-apply.
- Adjustable duration, delay, easing, direction, intensity, and iteration where supported.
- Trigger selection for supported interactions, such as page load, hover, click, or scroll.
- Favorites, recently used presets, and user collections.
- Multi-selection and applying compatible presets to multiple elements.
- Clear indications of whether a preset requires a particular trigger or browser capability.
- Reduced-motion options and accessible alternatives.
- A consistent preset format that can be validated and extended over time.

**The thousands-of-presets target is a goal, not a current library count.** Presets should be distinct, documented, tested, and searchable—not duplicated merely to inflate the number.

### 5. Responsive design workspace

Users should be able to preview the site at different viewport sizes and adjust each layout visually.

Planned controls include:
- Desktop, tablet, and mobile preview sizes.
- Custom viewport dimensions.
- Responsive spacing and sizing controls.
- Breakpoint-aware overrides where supported.
- Visibility and layout adjustments per viewport.
- A way to compare layouts and spot overflow or broken arrangements.

The editor should preserve responsive behavior rather than assuming that a desktop layout can simply be shrunk to fit a phone.

### 6. Styling and design controls

Visual controls are intended to cover common website design needs:
- Typography, text alignment, line height, and letter spacing.
- Color, gradients, borders, radii, and shadows.
- Flex and grid layout controls where they can be mapped reliably.
- Spacing, dimensions, constraints, and positioning.
- Background images and supported media.
- Reusable colors, typography settings, and design tokens.
- Component-level styling and reusable patterns.
- Optional site-wide design settings.

Existing styles may be complex, shared, or driven by scripts. Where an edit could affect more than the selected element, the interface should explain the scope before applying it.

### 7. Assets and media

The planned asset manager should make it easier to find and replace files used by the project.

Expected functionality:
- Browse project images, icons, fonts, and supported media.
- Preview assets and search by filename.
- Replace an asset while updating supported references.
- Detect missing local assets and broken paths.
- Keep filenames and folder structure stable when possible.
- Help users avoid unintentionally exporting private or unrelated files.

### 8. Preview, history, and export

Before exporting, users should be able to review their work in a separate preview state.

The intended workflow is:

1. **Open or create** a website project.
2. **Inspect** the page and its structure.
3. **Select and edit** elements visually.
4. **Apply** styling, layout changes, and animation presets.
5. **Preview** the result across viewport sizes.
6. **Review** the change list and any compatibility warnings.
7. **Export** the modified website project.
8. **Test** the exported files before replacing a live deployment.

Undo/redo, recoverable backups, unsaved-change warnings, and export validation are core reliability requirements—not optional decoration.

## Intended workflow

A typical redesign should look like this:

1. Open a website project.
2. Select a heading on the canvas and change its text.
3. Drag a section into a new position or adjust its spacing from the properties panel.
4. Replace an image through the asset manager.
5. Search the preset library for an animation, preview it, and apply it to a button or section.
6. Switch to mobile preview and correct the layout.
7. Review changes, export the website, and test the exported project.

The user should not need to manually edit HTML, CSS, or JavaScript to perform these common operations. The application will still need to interpret and update project files internally, and advanced or unsupported cases may require a warning or a different workflow.

## Editor workspace direction

The editor should feel like a serious creative tool, with a dockable, multi-panel layout inspired by professional 3D and game-engine editors. The reference is the workflow—viewport in the center, a hierarchy on the left, properties on the right, and a searchable content drawer below—not a copy of another product's branding or artwork.

The planned workspace has:

- **Viewport:** A live page canvas where users select elements directly and preview the current design.
- **Page Outliner:** A tree of pages, sections, components, and individual elements.
- **Details panel:** Context-sensitive controls for text, dimensions, spacing, colors, typography, and supported animation settings.
- **Content Drawer:** Searchable animation presets, reusable components, images, fonts, icons, and other project assets.
- **Toolbar and status bar:** Project controls, viewport sizes, preview, save/export actions, and useful status information.
- **Responsive view controls:** Switch between desktop, tablet, and mobile sizes without leaving the editor.
- **Undo and redo:** Move backward and forward through recent visual edits.

### Interactive UI concept

An early, self-contained interface prototype is available at [prototype/index.html](prototype/index.html). It demonstrates the dark multi-panel workspace, element selection, basic property editing, viewport presets, simple animation effects, keyword search, and session save/load.

The prototype can also open a **single HTML file** in a contained preview, select its elements, drag them to reposition, edit eligible text, adjust width and X/Y offsets, change text and background colors, tune font size, padding, and opacity, apply a few sample animations, and export a new HTML file. Canvas moves are recorded in undo/redo history. Common shortcuts are `Ctrl/Cmd+S` to save or export, `Ctrl/Cmd+O` to open HTML, `Ctrl/Cmd+Shift+O` to open a session, `Ctrl/Cmd+Z` to undo, `Ctrl/Cmd+Shift+Z` or `Ctrl+Y` to redo, and `Esc` to exit preview. Try it with the [sample studio page](prototype/examples/studio-page.html).

This is deliberately a small first step, not full project importing. The preview blocks JavaScript and external network assets, so websites that depend on linked CSS, images, fonts, scripts, or backend services may not look or behave as they do when hosted. It does not yet load an entire website folder, keep linked assets together, or create a native desktop build. Those are still part of the planned application.

## Important technical boundaries

A visual editor must be transparent about what it can and cannot safely edit.

- **It cannot automatically rewrite every remote website.** Browser same-origin rules, cross-origin protections, authentication, and server permissions can prevent access. Editing should be based on files the user is authorized to modify or on a supported import workflow.
- **Arbitrary websites are not all structured alike.** Framework-generated pages, custom elements, dynamic content, canvas-rendered interfaces, and script-dependent interactions may not map cleanly to visual controls.
- **JavaScript should be preserved by default.** Common visual edits should not require users to write JavaScript. However, some behavior is implemented by scripts; the editor must not promise to change all behavior without touching or understanding those scripts.
- **Changes must be validated.** A visual edit can affect shared styles, responsive layouts, selectors, and interactions. The application should report detected risks and preserve a recoverable original.
- **Preview is not proof of production correctness.** Exported projects need testing in their intended browser and hosting environment.
- **Security matters.** Imported websites may contain untrusted HTML and scripts. Imported content should be handled cautiously and isolated where possible; it must not gain unrestricted access to local files or application privileges.

The product should prioritize safe, predictable edits over pretending to support every possible website implementation.

## Suggested development roadmap

This roadmap describes a possible build order; it is not a statement that the stages are complete.

### Phase 1 — Native desktop foundation
- Select an application framework only after validating the required operating systems and architectures.
- Build a real desktop shell with native file/folder pickers and a clear permission boundary.
- Define the project/import format and open local website files or supported archives.
- Build a contained preview environment that isolates imported website content from the app's privileged process.
- Discover common HTML elements and referenced assets.
- Make a small set of visual text and style edits.
- Save changes to a copy and export a working project.

### Phase 2 — Core visual editor
- Add canvas selection, element tree, property panels, and drag-based layout tools.
- Implement undo/redo, backups, and a change list.
- Support common layout and styling properties.
- Add responsive preview and validation warnings.

### Phase 3 — Animation engine and searchable presets
- Define and validate a consistent preset schema.
- Build the search, filter, preview, and apply experience.
- Add accessible reduced-motion handling.
- Expand the library through tested, distinct presets toward the thousands-of-presets goal.

### Phase 4 — Full website creation workflow
- Add blank-canvas creation, starter layouts, reusable components, and design tokens.
- Improve asset replacement and project organization.
- Add export validation and a clear compatibility report.

### Phase 5 — Compatibility and polish
- Test against a diverse set of real-world static website projects.
- Improve handling of shared styles, breakpoints, and dynamic pages.
- Improve recovery, accessibility, keyboard operation, and performance.
- Document supported project types and limitations.

Progress should be measured by tested capabilities and export quality, not by the number of buttons on the interface.

## Design and usability goals

The interface should feel like a dedicated design application rather than a raw code editor. A possible layout includes a project toolbar, central page canvas, left-side layers/assets navigation, and a right-side properties/animation panel.

The experience should emphasize:
- Direct manipulation and immediate visual feedback.
- Clear labels and predictable controls.
- Keyboard accessibility and sensible shortcuts.
- Responsive performance on ordinary hardware.
- Previewing before applying complex changes.
- Useful error messages and recoverable edits.
- A clear separation between project editing, preview, and export.

These are design goals; the final interface and implementation will be refined during development.

## Desktop platforms and architecture targets

WEBEDYTS is intended to ship as an installable desktop app for all three major desktop operating systems. These are **release targets, not available downloads yet**.

| Operating system | Intended release targets | Planned distribution |
|---|---|---|
| Windows | x86 (32-bit) and x64 (64-bit) | Native installer/package such as EXE or MSI |
| Linux | x86 (32-bit) and x64 (64-bit), where the selected runtime and dependencies support them | Appropriate formats such as AppImage, DEB, or RPM, chosen after distro testing |
| macOS | Intel x64 and Apple Silicon arm64; a universal 64-bit package may be considered | DMG or another standard macOS package |

### 32-bit compatibility on macOS

There is an important operating-system limitation: Apple states that macOS Catalina 10.15 and later cannot run 32-bit apps. A 32-bit macOS build would therefore only be useful for legacy macOS versions, not modern macOS installations. The practical current macOS target is 64-bit Intel and Apple Silicon; legacy 32-bit macOS support can only be considered as a separate historical compatibility target. See [Apple's 32-bit app compatibility guidance](https://support.apple.com/en-us/103076).

The 32-bit Windows and Linux targets must also be verified against the selected application framework, embedded browser/runtime, native dependencies, and packaging tools. The project must not claim an architecture as supported until an installable build has been produced and tested on that target. Framework selection should account for this requirement from the beginning rather than dropping x86 support accidentally.

### Native application requirements

- Installers or packages should be provided for supported OS/architecture combinations.
- The application should launch locally and should not require users to open a hosted web page to use the editor.
- Users choose which local folders or archives to open; the app must not scan or modify unrelated files without permission.
- Project editing, preview, save, and export should work offline for local projects wherever the features do not inherently need network access.
- Updates and optional network features must be clearly separated from core local editing.
- Release notes should identify the OS version, CPU architecture, package format, and known limitations for each download.

## Built-in SHA-256 license integrity

The repository includes a portable C++17 SHA-256 implementation and an embedded proprietary license notice:

- `src/security/sha256.hpp` implements SHA-256 without an external dependency.
- `src/security/license_guard.hpp` embeds the current license notice and verifies its SHA-256 digest.
- `tests/security/sha256_test.cpp` checks standard SHA-256 test vectors and validates the embedded notice.
- `CMakeLists.txt` provides a small build target for the security test.
- `src/security/README.md` explains what the check does and what it cannot protect against.

To build and run the test with CMake:

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

This is an integrity foundation, not unbreakable copy protection. A checksum stored alongside editable source can be changed by someone who modifies the source. Production releases should add signed release manifests and platform code-signing; the signing private key must stay outside the public repository. The verifier still needs to be called by the future desktop application's startup code before it becomes an app-wide check.

## AI and automated-code restrictions

See [AI-USE-POLICY.md](AI-USE-POLICY.md). The project explicitly withholds permission, absent prior written authorization, to use its protected source materials for AI/ML training and to use those materials as input for AI systems to produce rewrites, patches, ports, reconstructions, or derivative modifications of WEBEDYTS.

The policy states the copyright holder's intended terms; **a policy file or SHA-256 checksum cannot technically force third-party enterprise AI services to comply**. The policy does not claim ownership of general ideas or functionality, and legal effect depends on applicable law and circumstances.

## Copyright and usage

**Copyright (c) 2026 Robiul Rumman Razim. All rights reserved.**

WEBEDYTS is proprietary. Making this repository public allows people to view its contents on GitHub; it does **not** grant permission to copy, modify, redistribute, sublicense, sell, or use the project's original code and assets in other projects. Written permission from the copyright holder is required for those uses, except where applicable law provides otherwise.

Any third-party components or assets included in the project remain subject to their respective licenses. This notice does not override those licenses or rights that cannot legally be restricted.

## Current status and contributions

WEBEDYTS is in early prototyping. The repository has a working UI concept and a limited standalone-HTML editing demo, but the native desktop application, complete project importer, multi-file asset handling, and production export pipeline have not been implemented yet. This README distinguishes working prototype features from the larger plan.

Development should follow the project's [coding and commit rules](DEVELOPMENT.md): readable code, sensible-sized functions, no unnecessary automation or abstraction, honest testing, and short, natural commit messages.

Before contributing, check the repository's current files and documented scope. Changes should favor maintainability, safe project handling, accessible editing, and tested output. Avoid claiming support for a feature unless it has been implemented and verified.

---

**WEBEDYTS — open the project, redesign visually, export the website.**
