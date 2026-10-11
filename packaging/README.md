# WEBEDYTS desktop installers

The native desktop CI builds a platform-specific installer only after the
compiled application passes that platform's native CTest suite.

| Platform | Installer | Installation model |
| --- | --- | --- |
| Windows | \`WEBEDYTS-Setup-<arch>-v<version>.exe\` | Per-user Inno Setup installer, Start Menu shortcut, optional desktop shortcut, and uninstaller |
| macOS | \`WEBEDYTS-<version>-macOS-<arch>.dmg\` | Drag \`WEBEDYTS.app\` into Applications |
| Debian / Ubuntu | \`WEBEDYTS_<version>_<arch>.deb\` | Native package manager installation, application-menu entry, and CEF sandbox helper permissions |

Each installer has a neighboring \`.sha256\` file. Verify it before installing
with a SHA-256 tool supported by the target operating system.

## Build locally

From the repository root after a successful native CEF build:

- Windows: install Inno Setup 6, then compile \`packaging/windows/WEBEDYTS.iss\` with the
  \`AppVersion\`, \`AppArch\`, \`StageDir\`, and \`OutputDir\` preprocessor definitions.
- macOS: run \`packaging/macos/build-dmg.sh <path-to-WEBEDYTS.app> <output-dir> 0.1.0 "$(uname -m)"\`.
- Debian / Ubuntu: run \`packaging/linux/build-deb.sh <cef-stage-dir> <output-dir> 0.1.0 "$(dpkg --print-architecture)"\`.

The Linux package requires the complete staged CEF runtime, including
\`chrome-sandbox\`. The Debian installer sets that helper's ownership and mode
as required for Chromium's Linux sandbox. Do not remove the helper or disable
the sandbox as a packaging shortcut.

## Release limitations

Installer builds are not the same as signed public releases. Windows installers
are currently unsigned; macOS builds are not Developer ID signed or notarized.
A macOS \`.dmg\` may therefore trigger Gatekeeper warnings. Do not describe either
platform's installer as signed, verified by a publisher certificate, or ready
for broad public distribution until the signing and release checks are in place.

GitHub Actions artifacts are temporary inspection builds, not permanent
download links. A Windows installer is deliberately withheld when the Windows
native startup smoke test fails.
