# Native desktop checks

The desktop CI build validates more than compilation. After building against the pinned CEF distribution, it runs the automated CTest suite and packages the complete runtime.

The tests cover:

- The embedded SHA-256 implementation and proprietary notice consistency.
- Required Chromium runtime files and the staged application footprint.
- SHA-256 sidecar generation for finished archives.
- CEF platform selection without downloading an SDK a second time.
- A native startup smoke test that launches WEBEDYTS, waits for the bundled `index.html` to finish loading in the main CEF frame, and verifies that the app shuts down cleanly.

Linux runs CTest inside Xvfb because CI agents do not provide a physical display. The startup test uses a temporary marker file and is time-limited; it does not publish a special mode in normal use. It verifies the CEF window and local editor page startup, but it is not a substitute for manually testing editing, import, preview, and export workflows.

To run the same native checks in a configured CEF build directory:

```sh
ctest --test-dir build-desktop -C Release --output-on-failure
```

On Linux, install `xvfb` and `xauth`, then run:

```sh
xvfb-run -a ctest --test-dir build-desktop -C Release --output-on-failure
```
