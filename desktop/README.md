# WEBEDYTS desktop application

WEBEDYTS is being built as a native desktop application around the Chromium
Embedded Framework (CEF), not as a thin wrapper around the computer's existing
browser. The packaged application includes the Chromium engine, its renderer
processes, GPU support files, resource packs, locale data, the native window
shell, and the visual editor.

That runtime is intentionally substantial. The installed application is
expected to occupy **hundreds of megabytes**, depending on operating system,
architecture, CEF version, and package format. That size must come from the
actual browser engine and required resources—not duplicate files, dummy assets,
or artificial padding. Do not remove Chromium resource packs or locale files
just to make the package appear smaller.

## Build requirements

A full CEF binary distribution is required. It contains the headers,
wrapper library, native Chromium runtime, resource packs, locale data, and its
licence notice. Keep it outside the WEBEDYTS source repository.

The simplest path is to let CMake download the official **standard**
distribution from the [CEF downloads page](https://cef-builds.spotifycdn.com/index.html).
The current default is pinned to CEF
`154.0.34+g14c5a08+chromium-154.0.8037.98`; the version can be overridden
with `WEBEDYTS_CEF_VERSION`, and each version uses a separate download folder.
Configure with `-DWEBEDYTS_DOWNLOAD_CEF=ON`. The bootstrap retrieves the
official `.sha1` file, checks the downloaded archive, and extracts it under
`build-desktop/_deps/cef`. This is a substantial download and requires extra
disk space for both the archive and extracted build SDK.

To supply a distribution you have already downloaded, omit
`WEBEDYTS_DOWNLOAD_CEF` and pass its extracted directory through `CEF_ROOT`.
Both paths bundle the real Chromium runtime; WEBEDYTS never substitutes the
system browser or inflates the app with dummy data.

### Windows

Use a supported Visual Studio C++ toolchain and a CEF distribution that matches
the selected target architecture.

```powershell
cmake -S . -B build-desktop -DWEBEDYTS_BUILD_DESKTOP=ON -DWEBEDYTS_DOWNLOAD_CEF=ON
cmake --build build-desktop --config Release
```

When the CEF package is configured with sandbox/bootstrap support, the native
WEBEDYTS client DLL is launched by CEF's bootstrap executable.

### Linux

Install CMake, a supported C++ toolchain, GTK development dependencies, and
the runtime libraries required by the selected CEF distribution.

```sh
cmake -S . -B build-desktop \
  -DWEBEDYTS_BUILD_DESKTOP=ON \
  -DWEBEDYTS_DOWNLOAD_CEF=ON \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build-desktop --parallel
cmake --build build-desktop --target webedyts_report_bundle_size
```

CEF's Linux sandbox helper needs the correct owner and SUID permissions
for the installed location. CEF's CMake macro prints the command during the
build. For a portable tar archive, apply it to the extracted app's
`chrome-sandbox` file after installation:

```sh
sudo chown root:root /path/to/WEBEDYTS/chrome-sandbox
sudo chmod 4755 /path/to/WEBEDYTS/chrome-sandbox
```

Use the actual installation path, keep the sandbox enabled, and do not launch
the app until the helper has been configured. A future system package/installer
should apply the permissions in its installation step rather than asking users
to repeat these commands manually.

### macOS

Build on macOS with Xcode and a matching CEF distribution for Intel x64 or
Apple Silicon arm64. The app has its own Cocoa entry point, implements CEF's
event-dispatch protocol, and packages the helper-app variants requested by the
selected CEF runtime. The main app bundle includes the Chromium framework and
its resources as well as the standalone WEBEDYTS editor.

```sh
cmake -S . -B build-desktop -G Xcode \
  -DWEBEDYTS_BUILD_DESKTOP=ON \
  -DWEBEDYTS_DOWNLOAD_CEF=ON \
  -DPROJECT_ARCH=arm64
cmake --build build-desktop --config Release
```

The finished application bundle is `WEBEDYTS.app`.

## Runtime and size checks

The build stages CEF's native binaries, resource packs, locale directory, the
WEBEDYTS editor, and CEF's licence file. It does not download the runtime at
application startup. A shipped app should run locally with its bundled runtime.

Use `desktop/tools/report-bundle-size.py` to inspect the staged package. The
check verifies key Chromium files, resource packs, ICU data, locale data, and
reports the installed footprint; it does not generate extra data to hit a
target size. Packaging requires at least 200 MiB of installed runtime files, so
a build missing a substantial part of Chromium will not produce a package.

Build a portable archive after the app has built:

```sh
cmake --build build-desktop --target webedyts_package --config Release
```

The output is written to `build-desktop/packages/`. Windows uses ZIP; Linux
and macOS use gzip-compressed tar archives. The archive contains the actual
staged app and browser runtime—no placeholder files. A focused test suite covers
complete Linux/Windows-style output, missing runtime files, macOS framework
resources, symlink size accounting, the package size requirement, and the CEF
bootstrap's Linux x64 path selection without downloading the SDK. Run the tests
with `ctest --test-dir build-desktop -C Release --output-on-failure` (use the
matching build directory and configuration for your generator).

## Build packages on GitHub

The repository also has a manual [Native desktop build workflow](https://github.com/Tamasrazim/WEBEDYTS/actions/workflows/native-desktop-build.yml).
Open it in GitHub Actions, select **Run workflow**, and keep the pinned CEF
version unless you deliberately need another supported release. Choose Windows
x64, x86, or ARM64; macOS can use the runner-native architecture or an explicit
Intel x64/Apple Silicon ARM64 target. Linux currently builds for the hosted
runner's native architecture. Each job runs the available tests, enforces the
200 MiB runtime check, and uploads a package artifact for 14 days. The archive's
filename identifies the architecture. These artifacts are for testing; the
workflow does not publish a production release or sign/notarize the app.

## Security boundary

The browser shell starts the existing monochrome editor inside CEF. Exported
HTML, ZIP, and media downloads are routed through the operating system's Save
As dialog, instead of being silently canceled by Alloy-style CEF. CEF warnings
are written to the user's WEBEDYTS log directory rather than the install folder.
The editor continues to disable scripts and external network access in its
imported-page preview. That preview policy is separate from CEF's OS-level
sandbox: release packaging must preserve the browser sandbox configuration
provided by the selected CEF distribution.

## Current status

This is the first native CEF shell and packaging foundation, not a released
installer. The repository does not include hundreds of megabytes of CEF
binaries; you supply the official binary distribution at build time. Until a
package has been built and exercised on each target OS, no downloadable binary
or cross-platform build should be advertised as finished.

CEF's current upstream platform matrix also has limits. In particular, its
current CMake setup says Linux x86 32-bit builds are discontinued; current
desktop macOS targets are x64 and arm64, not 32-bit. WEBEDYTS must not ship an
obsolete 32-bit browser runtime merely to claim that every architecture is
supported. See the [CEF project build notes](https://github.com/chromiumembedded/cef-project#build).
