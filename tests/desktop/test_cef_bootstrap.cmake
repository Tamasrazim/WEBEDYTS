cmake_minimum_required(VERSION 3.21)

if(NOT DEFINED CEF_TEST_DOWNLOAD_DIRECTORY OR
   NOT DEFINED CEF_TEST_MODULE)
    message(FATAL_ERROR "CEF test paths were not provided by CTest.")
endif()

include("${CEF_TEST_MODULE}")

# Every case creates a tiny marker directory, so platform mapping can be tested
# without transferring or extracting the large CEF SDK.
function(assert_cef_platform system_name processor pointer_size project_arch expected_platform)
    set(CMAKE_SYSTEM_NAME "${system_name}")
    set(CMAKE_SYSTEM_PROCESSOR "${processor}")
    set(CMAKE_SIZEOF_VOID_P "${pointer_size}")
    set(PROJECT_ARCH "${project_arch}")

    set(_test_version "webedyts-test-version")
    set(_expected_root
        "${CEF_TEST_DOWNLOAD_DIRECTORY}/cef_binary_${_test_version}_${expected_platform}")
    file(REMOVE_RECURSE "${_expected_root}")
    file(MAKE_DIRECTORY "${_expected_root}/cmake")
    file(WRITE "${_expected_root}/cmake/FindCEF.cmake" "# test marker\n")

    webedyts_download_cef(
        _detected_root
        "${CEF_TEST_DOWNLOAD_DIRECTORY}"
        "${_test_version}"
    )

    if(NOT _detected_root STREQUAL _expected_root)
        message(FATAL_ERROR
            "${system_name}/${processor} mapped to '${_detected_root}', expected '${_expected_root}'.")
    endif()
endfunction()

assert_cef_platform("Linux" "x86_64" 8 "" "linux64")
assert_cef_platform("Linux" "aarch64" 8 "" "linuxarm64")
assert_cef_platform("Linux" "armv7l" 4 "" "linuxarm")
assert_cef_platform("Windows" "AMD64" 8 "" "windows64")
assert_cef_platform("Windows" "ARM64" 8 "" "windowsarm64")
assert_cef_platform("Windows" "x86" 4 "" "windows32")
assert_cef_platform("Darwin" "arm64" 8 "arm64" "macosarm64")
assert_cef_platform("Darwin" "x86_64" 8 "x86_64" "macosx64")

message(STATUS "All supported CEF platform mappings selected the expected SDK paths.")
