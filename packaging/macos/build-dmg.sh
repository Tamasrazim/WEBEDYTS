#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <WEBEDYTS.app> <output-dir> <version> <architecture>" >&2
  exit 2
fi
app_bundle="$(cd "$(dirname "$1")" && pwd -P)/$(basename "$1")"
output_dir="$2"
version="$3"
architecture="$4"
repo_root="$(cd "$(dirname "$0")/../.." && pwd -P)"
if [[ ! -d "$app_bundle/Contents" || ! -x "$app_bundle/Contents/MacOS/WEBEDYTS" ]]; then
  echo "The WEBEDYTS.app bundle is missing its native executable." >&2
  exit 2
fi
if [[ "$architecture" == "aarch64" ]]; then architecture="arm64"; fi
if [[ "$architecture" != "arm64" && "$architecture" != "x86_64" ]]; then
  echo "Unsupported macOS architecture: $architecture" >&2
  exit 2
fi
staging="$(mktemp -d)"
cleanup() { rm -rf "$staging"; }
trap cleanup EXIT
mkdir -p "$output_dir"
ditto --rsrc --extattr "$app_bundle" "$staging/WEBEDYTS.app"
ln -s /Applications "$staging/Applications"
cat > "$staging/READ ME FIRST.txt" <<'EOF'
WEBEDYTS for macOS

INSTALL
1. Drag WEBEDYTS.app onto the Applications shortcut in this window.
2. Open WEBEDYTS from your Applications folder.

UNINSTALL
Quit WEBEDYTS, then move WEBEDYTS.app from Applications to the Trash.
Your user settings are stored separately from the application.

SIGNING STATUS
This CI-built package is not Developer ID signed or notarized yet. A public
release should be signed and notarized before broad distribution.
EOF
dmg_path="$output_dir/WEBEDYTS-"$version"-macOS-"$architecture".dmg"
hdiutil create -volname "WEBEDYTS" -srcfolder "$staging" -ov \
  -format UDZO -imagekey zlib-level=9 "$dmg_path"
hdiutil verify "$dmg_path"
python "$repo_root/desktop/tools/write-package-checksum.py" "$dmg_path"
echo "Created macOS disk image: $dmg_path"
