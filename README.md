# Website Indexer

**A visual index editor for websites — redesign pages without hand-editing HTML, CSS, or JavaScript.**

Website Indexer is planned as a designer-style workspace for opening a website project, understanding its page structure, and reshaping the result visually. It aims to combine the familiarity of a design application with the real files of a website: select an element, change its text, position, size, spacing, style, or animation, preview the result across screen sizes, and export the updated website.

The goal is to make website redesign accessible to people who think visually rather than in code, while keeping the exported project usable and inspectable by developers.

> **Project status:** This repository has just been created. The description below is the product vision and intended specification, not a claim that these features are already implemented. Features will be marked as available only after they exist and have been tested.

## The idea

Redesigning an existing website often means manually editing markup, stylesheets, scripts, and asset paths—or rebuilding the page in a separate design tool and then recreating it in code. Website Indexer aims to provide a visual alternative.

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
- **Local control:** Users should know which project files are opened, changed, and exported.

## Planned features

### 1. Open, import, and create projects

Website Indexer is intended to support two main starting points.

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

For remote URLs, availability will depend on access and browser security restrictions. A URL may be previewable without granting permission to rewrite the remote server's files. To edit a site, users will need an editable local project or another explicitly supported import method.

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

### Phase 1 — Reliable project foundation
- Define the project/import format.
- Open local website files and select an entry page.
- Build a contained preview environment.
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

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full terms.

## Current status and contributions

Website Indexer is at the project-definition stage. Features in this README describe the intended direction and will be updated as the implementation becomes available.

Before contributing, check the repository's current files and documented scope. Changes should favor maintainability, safe project handling, accessible editing, and tested output. Avoid claiming support for a feature unless it has been implemented and verified.

---

**Website Indexer — open the project, redesign visually, export the website.**
