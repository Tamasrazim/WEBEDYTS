#include "../../src/security/sha256.hpp"
#include "../../src/security/license_guard.hpp"

#include <iostream>

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
    if (!webedyts::security::verify_embedded_license_notice()) {
        std::cerr << "Embedded license SHA-256 mismatch\n";
        return 1;
    }

    std::cout << "SHA-256 and embedded-license checks passed\n";
    return 0;
}
