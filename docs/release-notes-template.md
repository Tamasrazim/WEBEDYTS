# WEBEDYTS @VERSION@ — Early Access

This is an early-access preview, not a claim that every planned feature is complete.

## Included
- Native desktop builds using the pinned Chromium Embedded Framework runtime.
- Platform packages for Windows x64, Debian/Ubuntu x64, and macOS on the CI runner's native architecture.
- Portable runtime archives with SHA-256 sidecar files.
- A per-user Windows installer, a macOS drag-and-drop disk image, and a Debian package.

## Before installing
- Verify the downloaded file against its accompanying SHA-256 sidecar.
- Keep a backup of each website project before editing or exporting it.
- Review the included license and third-party notices.

## Known limitations
- Installers are not code-signed; the macOS disk image is not Developer ID signed or notarized.
- Platform support reflects the OS and architectures in the build matrix, not every CPU or Linux distribution.
- Automated startup checks do not replace testing website import, editing, media insertion, preview, export, upgrade, and uninstall.
- WEBEDYTS does not automatically rewrite a live website on its hosting server.

This is a prerelease while native behavior and the installation experience continue to receive testing.
