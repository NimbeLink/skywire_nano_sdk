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

add_subdirectory(secure_services)

# Always include the peripheral request collector
zephyr_sources(
    peripheral_requests.c
)

# If using the auto-validation of the image, include that
if (CONFIG_AUTO_IMAGE_VALIDATION)
    zephyr_sources(
        image_valid.c
    )
endif()

# If using NimbeLink's Secure Services for offloading socket operations,
# include that
if (CONFIG_NIMBELINK_SOCKETS)
    zephyr_sources(
        nl_sockets.c
    )
endif()

# If using NimbeLink's Secure Services for offloading AT functionality, include
# that
if (CONFIG_NIMBELINK_AT_CMD)
    zephyr_sources(
        nl_at_cmd.c
    )
endif()

# If using NimbeLink's Secure Services for offloading FOTA, include that
if (CONFIG_NIMBELINK_FOTA_DOWNLOAD)
    zephyr_sources(
        nl_fota_download.c
    )
endif()
