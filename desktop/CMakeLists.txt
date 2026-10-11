cmake_minimum_required(VERSION 3.21)

option(WEBEDYTS_DOWNLOAD_CEF
    "Download the full official CEF distribution when CEF_ROOT is not set" OFF)
set(WEBEDYTS_CEF_VERSION
    "154.0.34+g14c5a08+chromium-154.0.8037.98"
    CACHE STRING "Version of the official CEF standard binary distribution")

if(NOT CEF_ROOT AND DEFINED ENV{CEF_ROOT})
    file(TO_CMAKE_PATH "$ENV{CEF_ROOT}" CEF_ROOT)
endif()

if(NOT CEF_ROOT AND WEBEDYTS_DOWNLOAD_CEF)
    include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/DownloadCEF.cmake")
    webedyts_download_cef(
        CEF_ROOT
        "${CMAKE_BINARY_DIR}/_deps/cef"
        "${WEBEDYTS_CEF_VERSION}"
    )
endif()

if(NOT CEF_ROOT OR NOT EXISTS "${CEF_ROOT}/cmake/FindCEF.cmake")
    message(FATAL_ERROR
        "Set CEF_ROOT to an extracted CEF distribution, or enable "
        "WEBEDYTS_DOWNLOAD_CEF=ON to fetch the full official runtime. "
        "WEBEDYTS does not replace Chromium with a system web view.")
endif()

set(CMAKE_MODULE_PATH "${CEF_ROOT}/cmake" ${CMAKE_MODULE_PATH})
find_package(CEF REQUIRED)

if(OS_MAC)
    # Xcode 16 emits an SDK-specific -target that can conflict with CEF's
    # minimum macOS flag. Keep that diagnostic visible, but don't treat this
    # harmless flag override as a fatal compilation error.
    add_compile_options(
        "$<$<COMPILE_LANG_AND_ID:CXX,AppleClang>:-Wno-error=overriding-option>"
    )
endif()

if(OS_MAC)
    enable_language(OBJC OBJCXX)
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(OS_MAC)
    set(CMAKE_OBJCXX_STANDARD 20)
    set(CMAKE_OBJCXX_STANDARD_REQUIRED ON)
    set(CMAKE_OBJCXX_EXTENSIONS OFF)
endif()

set(WEBEDYTS_VERSION "0.1.0")
set(WEBEDYTS_SOURCES
    src/webedyts_desktop.cpp
)

# CEF's generated macros configure compiler flags and runtime output paths.
SET_CEF_TARGET_OUT_DIR()
add_subdirectory(${CEF_LIBCEF_DLL_WRAPPER_PATH}
                 "${CMAKE_CURRENT_BINARY_DIR}/libcef_dll_wrapper")

if(OS_WINDOWS OR OS_LINUX)
    ADD_LOGICAL_TARGET("libcef_lib" "${CEF_LIB_DEBUG}" "${CEF_LIB_RELEASE}")
endif()

if(OS_MAC)
    set(EXECUTABLE_NAME "WEBEDYTS")
    set(PRODUCT_NAME "WEBEDYTS")
    set(BUNDLE_IDENTIFIER "com.tamasrazim.webedyts")

    configure_file(
        resources/mac/Info.plist.in
        "${CMAKE_CURRENT_BINARY_DIR}/Info.plist"
        @ONLY
    )

    add_executable(webedyts_desktop MACOSX_BUNDLE ${WEBEDYTS_SOURCES} src/main_mac.mm)
    SET_EXECUTABLE_TARGET_PROPERTIES(webedyts_desktop)
    set_target_properties(webedyts_desktop PROPERTIES
        OUTPUT_NAME "WEBEDYTS"
        MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_BINARY_DIR}/Info.plist"
        MACOSX_BUNDLE_BUNDLE_NAME "WEBEDYTS"
        MACOSX_BUNDLE_GUI_IDENTIFIER "${BUNDLE_IDENTIFIER}"
        MACOSX_BUNDLE_SHORT_VERSION_STRING "${WEBEDYTS_VERSION}"
        MACOSX_BUNDLE_BUNDLE_VERSION "${WEBEDYTS_VERSION}"
    )
    target_link_libraries(webedyts_desktop PRIVATE
        libcef_dll_wrapper
        ${CEF_STANDARD_LIBS}
    )

    set(WEBEDYTS_APP "${CEF_TARGET_OUT_DIR}/WEBEDYTS.app")
    COPY_MAC_FRAMEWORK(webedyts_desktop "${CEF_BINARY_DIR}" "${WEBEDYTS_APP}")

    # Build the helper bundles expected by this CEF distribution.
    foreach(_suffix_list ${CEF_HELPER_APP_SUFFIXES})
        string(REPLACE ":" ";" _helper_suffixes "${_suffix_list}")
        list(GET _helper_suffixes 0 _helper_name_suffix)
        list(GET _helper_suffixes 1 _helper_target_suffix)
        list(GET _helper_suffixes 2 _helper_plist_suffix)

        set(_helper_target "webedyts_helper${_helper_target_suffix}")
        set(_helper_output_name "WEBEDYTS Helper${_helper_name_suffix}")
        set(_helper_bundle_identifier
            "${BUNDLE_IDENTIFIER}.helper${_helper_plist_suffix}")
        set(_helper_plist
            "${CMAKE_CURRENT_BINARY_DIR}/helper-Info${_helper_target_suffix}.plist")

        file(READ
            "${CMAKE_CURRENT_SOURCE_DIR}/resources/mac/helper-Info.plist.in"
            _helper_plist_contents)
        string(REPLACE "@HELPER_EXECUTABLE_NAME@" "${_helper_output_name}"
            _helper_plist_contents "${_helper_plist_contents}")
        string(REPLACE "@HELPER_PRODUCT_NAME@" "${_helper_output_name}"
            _helper_plist_contents "${_helper_plist_contents}")
        string(REPLACE "@HELPER_BUNDLE_IDENTIFIER@" "${_helper_bundle_identifier}"
            _helper_plist_contents "${_helper_plist_contents}")
        string(REPLACE "@WEBEDYTS_VERSION@" "${WEBEDYTS_VERSION}"
            _helper_plist_contents "${_helper_plist_contents}")
        file(WRITE "${_helper_plist}" "${_helper_plist_contents}")

        add_executable(${_helper_target} MACOSX_BUNDLE src/helper_mac.mm)
        SET_EXECUTABLE_TARGET_PROPERTIES(${_helper_target})
        set_target_properties(${_helper_target} PROPERTIES
            OUTPUT_NAME "${_helper_output_name}"
            MACOSX_BUNDLE_INFO_PLIST "${_helper_plist}"
            MACOSX_BUNDLE_BUNDLE_NAME "${_helper_output_name}"
            MACOSX_BUNDLE_GUI_IDENTIFIER "${_helper_bundle_identifier}"
            MACOSX_BUNDLE_SHORT_VERSION_STRING "${WEBEDYTS_VERSION}"
            MACOSX_BUNDLE_BUNDLE_VERSION "${WEBEDYTS_VERSION}"
        )
        target_link_libraries(${_helper_target} PRIVATE
            libcef_dll_wrapper
            ${CEF_STANDARD_LIBS}
        )
        add_dependencies(webedyts_desktop "${_helper_target}")

        add_custom_command(TARGET webedyts_desktop POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_directory
                "${CEF_TARGET_OUT_DIR}/${_helper_output_name}.app"
                "${WEBEDYTS_APP}/Contents/Frameworks/${_helper_output_name}.app"
            VERBATIM
        )
    endforeach()

    # macOS CEF resources are bundled inside the framework.
    add_custom_command(TARGET webedyts_desktop POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory
            "${WEBEDYTS_APP}/Contents/Resources/app"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/prototype/index.html"
            "${WEBEDYTS_APP}/Contents/Resources/app/index.html"
        VERBATIM
    )

    set(WEBEDYTS_LICENSE_DEST "${WEBEDYTS_APP}/Contents/Resources/licenses")
else()
    if(OS_WINDOWS AND USE_SANDBOX)
        # Current CEF Windows packages use the signed bootstrap executable
        # when sandbox integration is enabled.
        add_library(webedyts_desktop SHARED ${WEBEDYTS_SOURCES})
        SET_LIBRARY_TARGET_PROPERTIES(webedyts_desktop)
        set_target_properties(webedyts_desktop PROPERTIES OUTPUT_NAME "WEBEDYTS")
        target_link_libraries(webedyts_desktop PRIVATE
            libcef_lib
            libcef_dll_wrapper
            ${CEF_STANDARD_LIBS}
        )
        COPY_SINGLE_FILE(webedyts_desktop
            "${CEF_BINARY_DIR}/bootstrap.exe"
            "${CEF_TARGET_OUT_DIR}/WEBEDYTS.exe"
        )
    else()
        if(OS_WINDOWS)
            add_executable(webedyts_desktop WIN32 ${WEBEDYTS_SOURCES})
        else()
            add_executable(webedyts_desktop ${WEBEDYTS_SOURCES})
        endif()
        SET_EXECUTABLE_TARGET_PROPERTIES(webedyts_desktop)
        target_link_libraries(webedyts_desktop PRIVATE
            libcef_lib
            libcef_dll_wrapper
            ${CEF_STANDARD_LIBS}
        )
    endif()

    COPY_FILES(webedyts_desktop "${CEF_BINARY_FILES}"
        "${CEF_BINARY_DIR}" "${CEF_TARGET_OUT_DIR}")
    COPY_FILES(webedyts_desktop "${CEF_RESOURCE_FILES}"
        "${CEF_RESOURCE_DIR}" "${CEF_TARGET_OUT_DIR}")

    add_custom_command(TARGET webedyts_desktop POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory
            "${CEF_TARGET_OUT_DIR}/resources/app"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/prototype/index.html"
            "${CEF_TARGET_OUT_DIR}/resources/app/index.html"
        VERBATIM
    )

    if(OS_LINUX)
        SET_LINUX_SUID_PERMISSIONS(webedyts_desktop
            "${CEF_TARGET_OUT_DIR}/chrome-sandbox")
    endif()

    set(WEBEDYTS_LICENSE_DEST "${CEF_TARGET_OUT_DIR}/licenses")
endif()

if(EXISTS "${CEF_ROOT}/LICENSE.txt")
    add_custom_command(TARGET webedyts_desktop POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${WEBEDYTS_LICENSE_DEST}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/LICENSE"
            "${WEBEDYTS_LICENSE_DEST}/WEBEDYTS-LICENSE.txt"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/AI-USE-POLICY.md"
            "${WEBEDYTS_LICENSE_DEST}/AI-USE-POLICY.md"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_CURRENT_SOURCE_DIR}/THIRD-PARTY-NOTICES.md"
            "${WEBEDYTS_LICENSE_DEST}/THIRD-PARTY-NOTICES.md"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CEF_ROOT}/LICENSE.txt"
            "${WEBEDYTS_LICENSE_DEST}/CEF-LICENSE.txt"
        VERBATIM
    )
else()
    message(FATAL_ERROR
        "CEF LICENSE.txt was not found at the CEF root. Check the selected "
        "binary distribution and include its notices before redistribution.")
endif()

find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_Interpreter_FOUND)
    add_test(
        NAME webedyts_bundle_size_test
        COMMAND "${Python3_EXECUTABLE}"
            "${CMAKE_SOURCE_DIR}/tests/desktop/test_bundle_size.py"
    )
    add_test(
        NAME webedyts_package_checksum_test
        COMMAND "${Python3_EXECUTABLE}"
            "${CMAKE_SOURCE_DIR}/tests/desktop/test_package_checksum.py"
    )
    add_test(
        NAME webedyts_cef_bootstrap_test
        COMMAND "${CMAKE_COMMAND}"
            "-DCEF_TEST_DOWNLOAD_DIRECTORY=${CMAKE_CURRENT_BINARY_DIR}/cef-bootstrap-test"
            "-DCEF_TEST_MODULE=${CMAKE_CURRENT_SOURCE_DIR}/cmake/DownloadCEF.cmake"
            -P "${CMAKE_SOURCE_DIR}/tests/desktop/test_cef_bootstrap.cmake"
    )

    if(OS_MAC)
        set(WEBEDYTS_BUNDLE_TO_CHECK "${WEBEDYTS_APP}")
    else()
        set(WEBEDYTS_BUNDLE_TO_CHECK "${CEF_TARGET_OUT_DIR}")
    endif()
    add_custom_target(webedyts_report_bundle_size
        COMMAND "${Python3_EXECUTABLE}"
            "${CMAKE_CURRENT_SOURCE_DIR}/tools/report-bundle-size.py"
            "${WEBEDYTS_BUNDLE_TO_CHECK}"
        DEPENDS webedyts_desktop
        COMMENT "Checking the bundled Chromium runtime and installed footprint"
        VERBATIM
    )

    if(OS_MAC)
        set(WEBEDYTS_PACKAGE_NAME
            "WEBEDYTS-macOS-${CMAKE_SYSTEM_PROCESSOR}-$<CONFIG>.tar.gz")
        set(WEBEDYTS_PACKAGE_FLAGS "czf")
        set(WEBEDYTS_PACKAGE_FORMAT "gnutar")
        set(WEBEDYTS_PACKAGE_CONTENTS "WEBEDYTS.app")
        set(WEBEDYTS_PACKAGE_WORKING_DIRECTORY "${CEF_TARGET_OUT_DIR}")
    elseif(OS_WINDOWS)
        set(WEBEDYTS_PACKAGE_NAME
            "WEBEDYTS-Windows-${CMAKE_SYSTEM_PROCESSOR}-$<CONFIG>.zip")
        set(WEBEDYTS_PACKAGE_FLAGS "cf")
        set(WEBEDYTS_PACKAGE_FORMAT "zip")
        set(WEBEDYTS_PACKAGE_CONTENTS ".")
        set(WEBEDYTS_PACKAGE_WORKING_DIRECTORY "${CEF_TARGET_OUT_DIR}")
    else()
        set(WEBEDYTS_PACKAGE_NAME
            "WEBEDYTS-Linux-${CMAKE_SYSTEM_PROCESSOR}-$<CONFIG>.tar.gz")
        set(WEBEDYTS_PACKAGE_FLAGS "czf")
        set(WEBEDYTS_PACKAGE_FORMAT "gnutar")
        set(WEBEDYTS_PACKAGE_CONTENTS ".")
        set(WEBEDYTS_PACKAGE_WORKING_DIRECTORY "${CEF_TARGET_OUT_DIR}")
    endif()

    if(OS_WINDOWS)
        if(CMAKE_SIZEOF_VOID_P EQUAL 8)
            set(WEBEDYTS_PACKAGE_ARCH "x64")
        else()
            set(WEBEDYTS_PACKAGE_ARCH "x86")
        endif()
        if(CMAKE_GENERATOR_PLATFORM MATCHES "ARM64")
            set(WEBEDYTS_PACKAGE_ARCH "arm64")
        endif()
    elseif(OS_MAC)
        if(PROJECT_ARCH)
            set(WEBEDYTS_PACKAGE_ARCH "${PROJECT_ARCH}")
        elseif(CMAKE_OSX_ARCHITECTURES)
            set(WEBEDYTS_PACKAGE_ARCH "${CMAKE_OSX_ARCHITECTURES}")
        else()
            set(WEBEDYTS_PACKAGE_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
        endif()
    else()
        set(WEBEDYTS_PACKAGE_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
    endif()

    string(REPLACE "${CMAKE_SYSTEM_PROCESSOR}" "${WEBEDYTS_PACKAGE_ARCH}"
        WEBEDYTS_PACKAGE_NAME "${WEBEDYTS_PACKAGE_NAME}")
    set(WEBEDYTS_PACKAGE_PATH
        "${CMAKE_BINARY_DIR}/packages/${WEBEDYTS_PACKAGE_NAME}")
    add_custom_target(webedyts_package
        COMMAND "${CMAKE_COMMAND}" -E make_directory
            "${CMAKE_BINARY_DIR}/packages"
        COMMAND "${Python3_EXECUTABLE}"
            "${CMAKE_CURRENT_SOURCE_DIR}/tools/report-bundle-size.py"
            "${WEBEDYTS_BUNDLE_TO_CHECK}"
            --minimum-mib 200
            --fail-below-minimum
        COMMAND "${CMAKE_COMMAND}" -E tar
            ${WEBEDYTS_PACKAGE_FLAGS}
            "${WEBEDYTS_PACKAGE_PATH}"
            "--format=${WEBEDYTS_PACKAGE_FORMAT}"
            --
            "${WEBEDYTS_PACKAGE_CONTENTS}"
        COMMAND "${Python3_EXECUTABLE}"
            "${CMAKE_CURRENT_SOURCE_DIR}/tools/write-package-checksum.py"
            "${WEBEDYTS_PACKAGE_PATH}"
        WORKING_DIRECTORY "${WEBEDYTS_PACKAGE_WORKING_DIRECTORY}"
        DEPENDS webedyts_desktop
        COMMENT "Checking and packaging the complete WEBEDYTS runtime"
        VERBATIM
    )
else()
    message(WARNING
        "Python 3 was not found. The native app can be built, but size validation "
        "and the portable package target will not be available.")
endif()

message(STATUS "WEBEDYTS desktop target uses the full CEF/Chromium runtime.")
message(STATUS "CEF root: ${CEF_ROOT}")
message(STATUS "The installed application is expected to be hundreds of MB; no dummy files are added to inflate its size.")
