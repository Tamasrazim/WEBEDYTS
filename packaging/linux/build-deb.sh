#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <cef-stage-dir> <output-dir> <version> <debian-architecture>" >&2
  exit 2
fi
stage_dir="$(cd "$1" && pwd -P)"
output_dir="$2"
version="$3"
architecture="$4"
repo_root="$(cd "$(dirname "$0")/../.." && pwd -P)"
if [[ ! "$version" =~ ^[0-9]+(\.[0-9]+){1,3}([+-][A-Za-z0-9.~-]+)?$ ]]; then
  echo "Invalid Debian package version: $version" >&2
  exit 2
fi
if [[ ! "$architecture" =~ ^(amd64|arm64|i386|armhf)$ ]]; then
  echo "Unsupported Debian package architecture: $architecture" >&2
  exit 2
fi
if [[ ! -f "$stage_dir/chrome-sandbox" ]]; then
  echo "The staged CEF runtime is missing chrome-sandbox; refusing to create an incomplete package." >&2
  exit 2
fi
app_binary=""
for candidate in WEBEDYTS webedyts_desktop; do
  if [[ -x "$stage_dir/$candidate" && -f "$stage_dir/$candidate" ]]; then
    app_binary="$candidate"
    break
  fi
done
if [[ -z "$app_binary" ]]; then
  echo "Could not find the WEBEDYTS Linux executable in: $stage_dir" >&2
  exit 2
fi
if [[ ! -f "$stage_dir/resources/app/index.html" || ! -d "$stage_dir/locales" ]]; then
  echo "The staged directory does not contain the full CEF runtime." >&2
  exit 2
fi
package_root="$(mktemp -d)"
cleanup() { rm -rf "$package_root"; }
trap cleanup EXIT
install_root="$package_root/usr/lib/webedyts"
mkdir -p "$install_root" "$package_root/usr/bin" \
  "$package_root/usr/share/applications" \
  "$package_root/usr/share/icons/hicolor/scalable/apps" \
  "$package_root/usr/share/doc/webedyts" "$package_root/DEBIAN"
cp -a "$stage_dir/." "$install_root/"
chmod 0755 "$install_root/chrome-sandbox"
cp "$repo_root/packaging/branding/webedyts.svg" \
  "$package_root/usr/share/icons/hicolor/scalable/apps/webedyts.svg"
cp "$repo_root/LICENSE" "$package_root/usr/share/doc/webedyts/copyright"
cp "$repo_root/desktop/THIRD-PARTY-NOTICES.md" \
  "$package_root/usr/share/doc/webedyts/THIRD-PARTY-NOTICES.md"
cat > "$package_root/usr/bin/webedyts" <<EOF
#!/bin/sh
set -eu
APP_DIR="/usr/lib/webedyts"
cd "\$APP_DIR"
exec "\$APP_DIR/$app_binary" "\$@"
EOF
chmod 0755 "$package_root/usr/bin/webedyts"
cat > "$package_root/usr/share/applications/webedyts.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=WEBEDYTS
GenericName=Website Design Editor
Comment=Visually edit and rebuild website projects
Exec=webedyts
TryExec=webedyts
Icon=webedyts
Terminal=false
Categories=Graphics;Development;WebDevelopment;
StartupWMClass=WEBEDYTS
EOF
cat > "$package_root/DEBIAN/control" <<EOF
Package: webedyts
Version: $version
Section: graphics
Priority: optional
Architecture: $architecture
Maintainer: Robiul Rumman Razim <211502422+Tamasrazim@users.noreply.github.com>
Installed-Size: $(du -sk "$install_root" | awk '{print $1}')
Depends: libc6, libstdc++6, libgcc-s1, libasound2 | libasound2t64, libatk-bridge2.0-0 | libatk-bridge2.0-0t64, libatk1.0-0 | libatk1.0-0t64, libatspi2.0-0 | libatspi2.0-0t64, libcairo2, libdrm2, libgbm1, libgtk-3-0 | libgtk-3-0t64, libnss3, libpango-1.0-0, libx11-6, libx11-xcb1, libxcomposite1, libxdamage1, libxfixes3, libxkbcommon0, libxrandr2, libxshmfence1
Description: Visual-first desktop website design editor
 WEBEDYTS is a native desktop application for visually editing website layouts,
 content, styles, media assets, and supported animation effects.
EOF
cat > "$package_root/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
sandbox="/usr/lib/webedyts/chrome-sandbox"
if [ -f "$sandbox" ]; then
  chown root:root "$sandbox"
  chmod 4755 "$sandbox"
fi
exit 0
EOF
chmod 0755 "$package_root/DEBIAN/postinst"
mkdir -p "$output_dir"
output_path="$output_dir/WEBEDYTS_"$version"_"$architecture".deb"
dpkg-deb --build -Zxz -z5 --root-owner-group "$package_root" "$output_path"
python "$repo_root/desktop/tools/write-package-checksum.py" "$output_path"
echo "Created Debian installer: $output_path"
