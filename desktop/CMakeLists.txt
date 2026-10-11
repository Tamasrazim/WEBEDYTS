cmake_minimum_required(VERSION 3.21)

if(NOT CEF_ROOT AND DEFINED ENV{CEF_ROOT})
    file(TO_CMAKE_PATH "$ENV{CEF_ROOT}" CEF_ROOT)
endif()

if(NOT CEF_ROOT OR NOT EXISTS "${CEF_ROOT}/cmake/FindCEF.cmake")
    message(FATAL_ERROR
        "Set CEF_ROOT to an extracted CEF binary distribution. "
        "WEBEDYTS does not replace the Chromium runtime with a system web view.")
endif()

set(CMAKE_MODULE_PATH "${CEF_ROOT}/cmake" ${CMAKE_MODULE_PATH})
find_package(CEF REQUIRED)

if(OS_MAC)
    enable_language(OBJC OBJCXX)
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

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

    add_executable(webedyts_desktop MACOSX_BUNDLE ${WEBEDYTS_SOURCES})
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
            "${CEF_ROOT}/LICENSE.txt"
            "${WEBEDYTS_LICENSE_DEST}/CEF-LICENSE.txt"
        VERBATIM
    )
else()
    message(WARNING
        "CEF LICENSE.txt was not found at the CEF root. Check the selected "
        "binary distribution and include its notices before redistribution.")
endif()

find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_Interpreter_FOUND)
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
endif()

message(STATUS "WEBEDYTS desktop target uses the full CEF/Chromium runtime.")
message(STATUS "CEF root: ${CEF_ROOT}")
message(STATUS "The installed application is expected to be hundreds of MB; no dummy files are added to inflate its size.")
