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

A matching CEF binary distribution is required. It contains the headers,
wrapper library, native runtime, resource packs, locale data, and its licence
notice. Keep it outside the WEBEDYTS source repository.

Download a CEF binary distribution for the target operating system and
architecture from the [official CEF project](https://github.com/chromiumembedded/cef).
Extract it and pass the extracted directory as `CEF_ROOT`.

### Windows

Use a supported Visual Studio C++ toolchain and a CEF distribution that matches
the selected target architecture.

```powershell
cmake -S . -B build-desktop -DWEBEDYTS_BUILD_DESKTOP=ON -DCEF_ROOT="C:/SDKs/cef_binary"
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
  -DCEF_ROOT="$HOME/SDKs/cef_binary" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build-desktop --parallel
cmake --build build-desktop --target webedyts_report_bundle_size
```

CEF's Linux sandbox helper may require owner and permission setup for the
chosen installation format. The CMake build prints the required command; do
not silently disable the sandbox to get around a packaging problem.

### macOS

Build on macOS with Xcode and a matching CEF distribution for Intel x64 or
Apple Silicon arm64. The bundle includes the Chromium framework and a separate
helper application for Chromium child processes.

```sh
cmake -S . -B build-desktop -G Xcode \
  -DWEBEDYTS_BUILD_DESKTOP=ON \
  -DCEF_ROOT="$HOME/SDKs/cef_binary" \
  -DPROJECT_ARCH=arm64
cmake --build build-desktop --config Release
```

The finished application bundle is `WEBEDYTS.app`.

## Runtime and size checks

The build stages CEF's native binaries, resource packs, locale directory, the
WEBEDYTS editor, and CEF's licence file. It does not download the runtime at
application startup. A shipped app should run locally with its bundled runtime.

Use `desktop/tools/report-bundle-size.py` to inspect the staged package. The
check verifies key Chromium files and reports the installed footprint; a
small output folder is a sign that required runtime files may be missing. It
does not generate extra data to hit a target size.

## Security boundary

The browser shell starts the existing monochrome editor inside CEF. The
editor continues to disable scripts and external network access in its
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
