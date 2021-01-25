/**
 * \file
 *
 * \brief Requests marking the Non-Secure image as valid
 *
 * (C) NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#include <init.h>

#include "nimbelink/sdk/secure_services/kernel.h"

/**
 * \brief Requests marking the Non-Secure image as valid once booted
 *
 * \param *device
 *      Unused
 *
 * \return 0
 *      Image marked as valid
 * \return int
 *      A failure occurred while marking the image as valid
 */
static int MarkImageValid(const struct device *device)
{
    (void)device;

    return Kernel_MarkImageValid();
}

// Run our image marking during system initialization, as late as possible (to
// allow all other systems to have a chance to initialize and ensure nothing
// goes wrong)
SYS_INIT(MarkImageValid, APPLICATION, 99);
