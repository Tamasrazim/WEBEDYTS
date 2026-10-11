# Download the official, full CEF binary distribution when requested.
#
# The upstream .sha1 file is used to detect incomplete or corrupted downloads.
# It is an integrity check, not a signature or a guarantee of publisher identity.

function(webedyts_download_cef output_variable download_directory cef_version)
    if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        if(CMAKE_GENERATOR_PLATFORM MATCHES "ARM64" OR
           CMAKE_CXX_COMPILER_ARCHITECTURE_ID STREQUAL "ARM64" OR
           CMAKE_SYSTEM_PROCESSOR MATCHES "^(ARM64|arm64|aarch64)$")
            set(_cef_platform "windowsarm64")
        elseif(CMAKE_SIZEOF_VOID_P EQUAL 8)
            set(_cef_platform "windows64")
        else()
            set(_cef_platform "windows32")
        endif()
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64)$")
            set(_cef_platform "linuxarm64")
        elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm|armv7l|armv7.*)$")
            set(_cef_platform "linuxarm")
        elseif(CMAKE_SIZEOF_VOID_P EQUAL 8)
            set(_cef_platform "linux64")
        else()
            message(FATAL_ERROR
                "The current WEBEDYTS CEF bootstrap does not support Linux x86 32-bit.")
        endif()
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        if(DEFINED PROJECT_ARCH AND NOT PROJECT_ARCH STREQUAL "")
            set(_cef_arch "${PROJECT_ARCH}")
        elseif(CMAKE_OSX_ARCHITECTURES)
            list(LENGTH CMAKE_OSX_ARCHITECTURES _cef_arch_count)
            if(NOT _cef_arch_count EQUAL 1)
                message(FATAL_ERROR
                    "Choose one macOS architecture per CEF build: set PROJECT_ARCH to x86_64 or arm64.")
            endif()
            list(GET CMAKE_OSX_ARCHITECTURES 0 _cef_arch)
        else()
            set(_cef_arch "${CMAKE_SYSTEM_PROCESSOR}")
        endif()

        if(_cef_arch MATCHES "^(arm64|aarch64)$")
            set(PROJECT_ARCH "arm64" CACHE STRING "CEF target architecture" FORCE)
            set(_cef_platform "macosarm64")
        elseif(_cef_arch MATCHES "^(x86_64|AMD64|amd64)$")
            set(PROJECT_ARCH "x86_64" CACHE STRING "CEF target architecture" FORCE)
            set(_cef_platform "macosx64")
        else()
            message(FATAL_ERROR
                "Unsupported macOS CEF architecture '${_cef_arch}'. Use x86_64 or arm64.")
        endif()
    else()
        message(FATAL_ERROR
            "No prebuilt CEF distribution is configured for ${CMAKE_SYSTEM_NAME}.")
    endif()

    set(_cef_distribution
        "cef_binary_${cef_version}_${_cef_platform}")
    set(_cef_root "${download_directory}/${_cef_distribution}")
    set(_cef_archive "${download_directory}/${_cef_distribution}.tar.bz2")
    set(_cef_archive_url
        "https://cef-builds.spotifycdn.com/${_cef_distribution}.tar.bz2")

    if(NOT EXISTS "${_cef_root}/cmake/FindCEF.cmake")
        file(MAKE_DIRECTORY "${download_directory}")

        # CEF versions contain plus signs, which must be escaped in the URL.
        string(REPLACE "+" "%2B" _cef_url_escaped "${_cef_archive_url}")
        file(DOWNLOAD
            "${_cef_url_escaped}.sha1"
            "${_cef_archive}.sha1"
            STATUS _cef_hash_status
            TLS_VERIFY ON
        )
        list(GET _cef_hash_status 0 _cef_hash_status_code)
        if(NOT _cef_hash_status_code EQUAL 0)
            message(FATAL_ERROR
                "Could not fetch the official CEF checksum: ${_cef_hash_status}")
        endif()

        file(READ "${_cef_archive}.sha1" _cef_expected_sha1)
        string(STRIP "${_cef_expected_sha1}" _cef_expected_sha1)
        string(TOLOWER "${_cef_expected_sha1}" _cef_expected_sha1)
        string(LENGTH "${_cef_expected_sha1}" _cef_hash_length)
        if(NOT _cef_hash_length EQUAL 40 OR
           NOT _cef_expected_sha1 MATCHES "^[0-9a-f]+$")
            message(FATAL_ERROR
                "The CEF download endpoint returned an invalid SHA-1 checksum.")
        endif()

        set(_cef_download_archive TRUE)
        if(EXISTS "${_cef_archive}")
            file(SHA1 "${_cef_archive}" _cef_existing_sha1)
            string(TOLOWER "${_cef_existing_sha1}" _cef_existing_sha1)
            if(_cef_existing_sha1 STREQUAL _cef_expected_sha1)
                set(_cef_download_archive FALSE)
            else()
                file(REMOVE "${_cef_archive}")
            endif()
        endif()

        if(_cef_download_archive)
            message(STATUS
                "Downloading the full CEF ${cef_version} ${_cef_platform} distribution.")
            file(DOWNLOAD
                "${_cef_url_escaped}"
                "${_cef_archive}"
                EXPECTED_HASH "SHA1=${_cef_expected_sha1}"
                SHOW_PROGRESS
                STATUS _cef_download_status
                TLS_VERIFY ON
            )
            list(GET _cef_download_status 0 _cef_download_status_code)
            if(NOT _cef_download_status_code EQUAL 0)
                file(REMOVE "${_cef_archive}")
                message(FATAL_ERROR
                    "CEF download failed: ${_cef_download_status}")
            endif()
        endif()

        message(STATUS "Extracting the full CEF distribution. This requires substantial disk space.")
        execute_process(
            COMMAND "${CMAKE_COMMAND}" -E tar xzf "${_cef_archive}"
            WORKING_DIRECTORY "${download_directory}"
            RESULT_VARIABLE _cef_extract_result
        )
        if(NOT _cef_extract_result STREQUAL "0")
            message(FATAL_ERROR
                "Could not extract ${_cef_archive}: ${_cef_extract_result}")
        endif()
    endif()

    if(NOT EXISTS "${_cef_root}/cmake/FindCEF.cmake")
        message(FATAL_ERROR
            "The extracted CEF distribution is incomplete: ${_cef_root}")
    endif()

    set(${output_variable} "${_cef_root}" PARENT_SCOPE)
endfunction()
