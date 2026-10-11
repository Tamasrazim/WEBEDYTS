# Release process

The first release target is 0.1.0 (early access). Do not create its tag until the checklist below is complete.

## Before creating a version tag
1. Fix all failing native tests, especially the Windows startup smoke test.
2. Run source and packaging checks and the full Windows, Linux, and macOS build matrix.
3. Install each generated package on a clean target machine or virtual machine. Test launch, import, selection and property edits, media insertion, preview, export, and uninstall.
4. Check Chromium runtime contents, third-party notices, package names, version strings, and all SHA-256 sidecars.
5. Decide on signing. For broad public distribution, configure Windows code signing and Apple's Developer ID signing and notarization. Never claim a package is signed when it is not.
6. Confirm that release notes accurately describe the tested build and limitations.

## Versioning
- The root VERSION file is the single version source for native binary metadata and installers.
- A release tag must match VERSION exactly, with a leading v: VERSION=0.1.0 means tag v0.1.0.
- Push a tag only after its exact commit is ready for review. The release workflow rebuilds from the tag instead of reusing main-branch artifacts.

## What CI does
A matching version tag builds and tests the complete runtime on Windows, Linux, and macOS. Each job produces its installer, portable package, and SHA-256 files only after the platform's native tests pass. A separate job checks all sidecars and assembles a draft prerelease only when the full platform matrix succeeds.

The workflow does not publish the release automatically. Review the draft, assets, install behavior, and release notes in GitHub before publishing it.
