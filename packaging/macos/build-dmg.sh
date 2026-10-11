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

mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd -P)"
staging="$(mktemp -d)"
cleanup() { rm -rf "$staging"; }
trap cleanup EXIT

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

dmg_path="$output_dir/WEBEDYTS-$version-macOS-$architecture.dmg"
hdiutil create -volname "WEBEDYTS" -srcfolder "$staging" -ov \
  -format UDZO -imagekey zlib-level=9 "$dmg_path"

# Some macOS runners leave the newly-created image attached. hdiutil verify
# needs an exclusive handle, so detach this exact image before checking it.
python3 - "$dmg_path" <<'PY'
import os
import plistlib
import re
import subprocess
import sys

target = os.path.realpath(sys.argv[1])
result = subprocess.run(
    ["hdiutil", "info", "-plist"],
    check=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
info = plistlib.loads(result.stdout)

for image in info.get("images", []):
    image_path = image.get("image-path", "")
    if not image_path or os.path.realpath(image_path) != target:
        continue

    devices = []
    for entity in image.get("system-entities", []):
        device = entity.get("dev-entry", "")
        if re.fullmatch(r"/dev/disk[0-9]+", device) and device not in devices:
            devices.append(device)

    for device in devices:
        detached = subprocess.run(
            ["hdiutil", "detach", device, "-force"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if detached.returncode != 0:
            detail = (detached.stderr or detached.stdout).strip()
            print(f"Could not detach {device}: {detail}", file=sys.stderr)
PY

# Retry verification for transient DiskImages locks, but never skip verification.
python3 - "$dmg_path" <<'PY'
import subprocess
import sys
import time

image = sys.argv[1]
last_output = ""
for attempt in range(1, 5):
    result = subprocess.run(
        ["hdiutil", "verify", image],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    last_output = result.stdout
    if result.returncode == 0:
        print(last_output, end="" if last_output.endswith("\n") else "\n")
        print(f"Disk image verification passed on attempt {attempt}.")
        break
    print(f"Disk image verification attempt {attempt}/4 failed:")
    print(last_output, end="" if last_output.endswith("\n") else "\n")
    if attempt < 4:
        time.sleep(attempt * 2)
else:
    print("Disk image verification failed after four attempts.", file=sys.stderr)
    raise SystemExit(1)
PY

python "$repo_root/desktop/tools/write-package-checksum.py" "$dmg_path"
echo "Created macOS disk image: $dmg_path"
