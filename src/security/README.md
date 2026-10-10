# Built-in license integrity check

`sha256.hpp` provides a dependency-free SHA-256 implementation in portable
C++17. `license_guard.hpp` embeds the WEBEDYTS proprietary notice and
checks its UTF-8 bytes against the expected SHA-256 digest. The test program
under `tests/security/sha256_test.cpp` validates standard SHA-256 test vectors
and confirms the embedded notice matches its digest.

## Important security boundary

The current check detects accidental edits or a notice/hash mismatch. Because
both the notice and expected digest live in source code, a determined person
who edits the source can change or remove both. SHA-256 is a hash, not a digital
signature, encryption, DRM, or a legal enforcement mechanism.

Before shipping release builds, the application startup should call
`verify_embedded_license_notice()` and handle a failed check clearly. Release
integrity for executable files and packaged resources should additionally use
OS-native code signing and a signed release manifest. The manifest should
contain SHA-256 digests for selected release files, and the verification public
key should be embedded in the app while the signing private key remains outside
the repository and build artifacts. Do not commit signing keys or secrets.

This module is a security foundation only. Until the desktop application's
entry point exists and calls the verifier, it is not an app-wide tamper
protection system. No local checker can force an external AI provider to
comply with `AI-USE-POLICY.md`.
