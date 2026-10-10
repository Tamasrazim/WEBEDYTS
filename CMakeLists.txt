cmake_minimum_required(VERSION 3.16)

project(WEBEDYTS LANGUAGES CXX)

add_executable(webedyts_security_test
    tests/security/sha256_test.cpp
)

target_compile_features(webedyts_security_test PRIVATE cxx_std_17)

if(MSVC)
    target_compile_options(webedyts_security_test PRIVATE /W4)
else()
    target_compile_options(webedyts_security_test PRIVATE -Wall -Wextra -Wpedantic)
endif()

enable_testing()
add_test(NAME webedyts_security_test COMMAND webedyts_security_test)
