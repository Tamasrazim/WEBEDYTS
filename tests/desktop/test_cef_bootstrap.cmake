cmake_minimum_required(VERSION 3.21)

if(NOT DEFINED CEF_TEST_DOWNLOAD_DIRECTORY OR
   NOT DEFINED CEF_TEST_MODULE)
    message(FATAL_ERROR "CEF test paths were not provided by CTest.")
endif()

# Pre-stage an SDK marker so this test skips the large download.
set(CMAKE_SYSTEM_NAME "Linux")
set(CMAKE_SYSTEM_PROCESSOR "x86_64")
set(CMAKE_SIZEOF_VOID_P 8)

set(_test_version "webedyts-test-version")
set(_expected_root
    "${CEF_TEST_DOWNLOAD_DIRECTORY}/cef_binary_${_test_version}_linux64")
file(REMOVE_RECURSE "${_expected_root}")
file(MAKE_DIRECTORY "${_expected_root}/cmake")
file(WRITE "${_expected_root}/cmake/FindCEF.cmake" "# test marker\n")

include("${CEF_TEST_MODULE}")
webedyts_download_cef(
    _detected_root
    "${CEF_TEST_DOWNLOAD_DIRECTORY}"
    "${_test_version}"
)

if(NOT _detected_root STREQUAL _expected_root)
    message(FATAL_ERROR
        "CEF platform mapping returned '${_detected_root}', expected '${_expected_root}'.")
endif()

message(STATUS "CEF bootstrap selected the expected Linux x64 distribution path.")
