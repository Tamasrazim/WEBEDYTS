#pragma once

// Embedded proprietary license and SHA-256 consistency check.
// This detects an accidental or unsynchronized edit to the embedded notice.
// It is not a substitute for signed release manifests or OS code signing.

#include "sha256.hpp"
#include <string_view>

namespace website_indexer::security {

inline constexpr std::string_view kEmbeddedLicenseNotice = R"WI_LICENSE(Copyright (c) 2026 Robiul Rumman Razim. All rights reserved.

PROPRIETARY PROJECT — NO OPEN-SOURCE LICENSE GRANTED

No permission is granted to use, copy, modify, prepare derivative works from,
merge, publish, distribute, sublicense, or sell this project's original source
code, documentation, designs, animation presets, or assets without prior
written permission from the copyright holder, except where applicable law
provides otherwise.

NO AI/ML PERMISSION IS GRANTED. Without prior written permission, this project
may not be used to train, fine-tune, evaluate, benchmark, or improve an AI/ML
model; create datasets, embeddings, or retrieval indexes from it; or use its
protected contents as input for a generative system to produce rewrites,
patches, ports, reconstructions, or derivative implementations of Website
Indexer. These restrictions state the copyright holder's permission terms and
apply only to the extent permitted by applicable law.

Viewing this public repository on GitHub does not grant any of the permissions
listed above. All rights are reserved. No license is granted by implication,
estoppel, or the public availability of the repository, except for rights that
cannot legally be restricted.

Third-party components and assets, if any, remain governed by their own
licenses. This notice does not override those licenses or rights that cannot
legally be restricted.
)WI_LICENSE";

// SHA-256 of the exact embedded notice above (UTF-8 bytes).
inline constexpr std::string_view kExpectedLicenseSha256 = "e8314f505c1fff9f596f4030e65492b432b081b1af95ea16b29bd8fdcf7d5c7b";

inline bool verify_embedded_license_notice() {
    return sha256_hex(kEmbeddedLicenseNotice) == kExpectedLicenseSha256;
}

}  // namespace website_indexer::security
