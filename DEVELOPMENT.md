# Development Rules

These rules apply to anyone changing WEBEDYTS, including automated coding tools.

## 1. Write understandable code

Write code the next developer can read and maintain without needing to reverse-engineer the author's intent.

- Prefer straightforward logic over clever tricks.
- Keep functions focused and reasonably small.
- Don't add layers, frameworks, classes, factories, registries, or generic helper systems unless the project has a real need for them.
- Don't turn a simple operation into a chain of abstractions.
- Avoid huge functions that try to run the whole application by themselves.
- Use clear names that describe what a value or function actually does.
- Add comments when they explain a non-obvious decision, a limitation, or a tricky section. Don't narrate every line.
- Follow the conventions already used in the surrounding code unless there is a good reason to change them.
- Don't add dependencies for work that can be handled clearly with the platform or existing code.
- Don't generate large amounts of boilerplate just to make a feature look complete.
- Prefer code that can be debugged by a person with ordinary development tools.
- Keep error handling useful and specific. Don't hide failures behind empty catch blocks or vague success messages.

## 2. Keep automation reasonable

Automation is useful when it removes repeated work, not when it makes the project harder to understand.

Before adding an automated helper, ask whether a straightforward function or a few explicit lines would be easier to maintain. Avoid systems that rewrite, scan, modify, or generate unrelated project files without a clear requirement. Never claim broad or universal support when the implementation only handles known cases.

## 3. Be honest about testing

Run the checks that are available for the change. Report what was actually tested and what could not be tested. Never claim that code compiled, passed tests, or worked on an operating system unless that result was verified.

## 4. Write commit messages like a person

Commit messages should be short, natural, and specific. Describe the change in ordinary language.

Good examples:
- `Add the license check`
- `Fix the mobile layout`
- `Document supported platforms`
- `Handle missing image files`

Avoid long, robotic summaries, marketing language, unnecessary prefixes, and lists of every tiny implementation detail. Add a commit body only when context is genuinely useful.

## 5. Keep repository workflow simple

- Commit directly to `main`.
- Do not create branches or pull requests.
- Do not add GitHub Actions workflows or bot-driven contribution systems.
- Keep changes focused and avoid unrelated rewrites.
- Preserve the proprietary license and respect third-party licenses.

The goal is practical, readable software—not code that looks impressive because it is unnecessarily complicated.
