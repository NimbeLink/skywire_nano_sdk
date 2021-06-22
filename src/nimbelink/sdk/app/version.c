/**
 * \file
 *
 * \brief Provides an application version
 *
 * (C) NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#include <stdbool.h>

#include <dfu/mcuboot.h>
#include <zephyr.h>

#include "nimbelink/sdk/app/version.h"

/**
 * \brief Gets the device's version
 *
 *  If we fail to find a version, the default will be returned.
 *
 * \param flashId
 *      The flash ID containing the image whose version to get
 *
 * \return Version
        The version
 */
struct Version GetVersion(int flashId)
{
    struct mcuboot_img_header header;

    // Try to read the image header
    int result = boot_read_bank_header(
        flashId,
        &header,
        sizeof(header)
    );

    struct Version version;

    // If that failed or we don't know how to parse this version, we won't be
    // able to find the version
    if ((result != 0) || (header.mcuboot_version != 1))
    {
        version.major       = 0;
        version.minor       = 0;
        version.revision    = 0;
        version.build       = 0;
    }
    else
    {
        version.major       = header.h.v1.sem_ver.major;
        version.minor       = header.h.v1.sem_ver.minor;
        version.revision    = header.h.v1.sem_ver.revision;
        version.build       = header.h.v1.sem_ver.build_num;
    }

    return version;
}

/**
 * \brief Gets the version string
 *
 * \param none
 *
 * \return const char *
 *      The version string
 */
const char *GetVersionString(void)
{
    static const char *versionString =
    #include CONFIG_NIMBELINK_VERSION_APP_FILE
    ;

    return versionString;
}
