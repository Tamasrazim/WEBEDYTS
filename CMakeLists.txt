# Sets up the top-level WEBEDYTS build and connects the desktop app and its checks.

cmake_minimum_required(VERSION 3.16)

project(WEBEDYTS LANGUAGES C CXX)

option(WEBEDYTS_BUILD_DESKTOP "Build the native CEF desktop application" OFF)

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

if(WEBEDYTS_BUILD_DESKTOP)
    if(CMAKE_VERSION VERSION_LESS 3.21)
        message(FATAL_ERROR "The CEF desktop build requires CMake 3.21 or newer.")
    endif()
    add_subdirectory(desktop)
endif()
