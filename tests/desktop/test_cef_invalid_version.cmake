# Verifies that an invalid CEF version is rejected with a useful error instead of being treated as a valid download.

cmake_minimum_required(VERSION 3.21)

if(NOT DEFINED CEF_TEST_DOWNLOAD_DIRECTORY OR
   NOT DEFINED CEF_TEST_MODULE OR
   NOT DEFINED CEF_TEST_VERSION)
    message(FATAL_ERROR "CEF validation test arguments are missing.")
endif()

include("${CEF_TEST_MODULE}")
webedyts_download_cef(
    _unexpected_root
    "${CEF_TEST_DOWNLOAD_DIRECTORY}"
    "${CEF_TEST_VERSION}"
)

message(FATAL_ERROR "Malformed CEF version was unexpectedly accepted.")
