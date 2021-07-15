###
 # \file
 #
 # \brief Builds the Skywire Nano SDK
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

# If the SDK is being used, include the relevant sources
if (CONFIG_NIMBELINK_SDK)
    zephyr_library()

    # If the older stack firmware ABI is used but the older link library isn't,
    # let the user know that's likely not what they intended
    if (CONFIG_STACK_ABI_VERSION MATCHES "^1\.0\..*" AND
        NOT CONFIG_ARM_ENTRY_VENEERS_LIB_NAME MATCHES "libentryveneers_v1_0.*\.a"
    )
        message(WARNING "Legacy ABI used with newer veneers file!")
    elseif(CONFIG_STACK_ABI_VERSION MATCHES "^1\.1\..*" AND
        NOT CONFIG_ARM_ENTRY_VENEERS_LIB_NAME MATCHES "libentryveneers\.a"
    )
        message(WARNING "New ABI used with older veneers file!")
    endif()

    # The SDK will always use Secure Services
    add_subdirectory(secure_services)

    # Always include the peripheral request collector
    zephyr_library_sources(peripheral_requests.c)

    # If using the auto-validation of the image, include that
    if (CONFIG_AUTO_IMAGE_VALIDATION)
        zephyr_library_sources(image_valid.c)
    endif()

    # If using NimbeLink's Non-Secure reboot handling, include that
    if (CONFIG_NIMBELINK_REBOOT)
        zephyr_library_sources(nl_reboot.c)
    endif()

    # If we're providing the fatal error handling, include that
    if (CONFIG_ABORT_ON_FATAL_ERROR)
        zephyr_library_sources(nl_fatal_error.c)
    endif()

    # If using NimbeLink's Secure Services for offloading socket operations,
    # include that
    if (CONFIG_NIMBELINK_SOCKETS)
        zephyr_library_sources(nl_sockets.c)
    endif()

    # If using NimbeLink's Secure Services for offloading AT functionality,
    # include that
    if (CONFIG_NIMBELINK_AT_CMD)
        zephyr_library_sources(nl_at_cmd.c)
    endif()

    # If using NimbeLink's Secure Services for offloading FOTA, include that
    if (CONFIG_NIMBELINK_FOTA_DOWNLOAD)
        zephyr_library_sources(nl_fota_download.c)
    endif()
endif()
