/*
 * What this does:
 * Tests the SHA-256 helper against known results so a change to the hashing code can be caught before it ships.
 */

#include "../../src/security/sha256.hpp"
#include "../../src/security/license_guard.hpp"

#include <iostream>
#include <string>

int main() {
    using webedyts::security::sha256_hex;

    if (sha256_hex("") != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") {
        std::cerr << "SHA-256 empty-string test failed\n";
        return 1;
    }
    if (sha256_hex("abc") != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") {
        std::cerr << "SHA-256 abc test failed\n";
        return 1;
    }

    if (sha256_hex("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq") !=
        "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1") {
        std::cerr << "SHA-256 multi-block test failed\n";
        return 1;
    }
    const std::string million_a(1000000, 'a');
    if (sha256_hex(million_a) !=
        "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0") {
        std::cerr << "SHA-256 million-byte test failed\n";
        return 1;
    }

    if (!webedyts::security::verify_embedded_license_notice()) {
        std::cerr << "Embedded license SHA-256 mismatch\n";
        return 1;
    }

    std::cout << "SHA-256 and embedded-license checks passed\n";
    return 0;
}
