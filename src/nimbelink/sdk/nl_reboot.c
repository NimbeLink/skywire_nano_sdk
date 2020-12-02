/**
 * \file
 *
 * \brief Handles a Non-Secure reboot
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
#include <stdio.h>

#include "nimbelink/sdk/secure_services/kernel.h"

/**
 * \brief Handles a reboot
 *
 * \param type
 *      The type of reboot to perform
 *
 * \return none
 */
void sys_arch_reboot(int type)
{
    (void)type;

    Kernel_Reset(0);

    // If that somehow failed, we'll still end up causing bad things -- either
    // our current exception will keep bubbling up into the Secure context or
    // we'll hit some assert() -- so just ignore the result
}
