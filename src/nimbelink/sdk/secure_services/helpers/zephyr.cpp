/**
 * \file
 *
 * \brief Secure service helpers for a Zephyr-based application
 *
 * © NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#include <cstdint>

#include <zephyr.h>

#include "nimbelink/sdk/secure_services/kernel.h"

extern "C"
{
void arch_set_pendsv(void)
{
    // Lock interrupts to try and keep our Secure-world thread -- which is
    // running the Non-Secure kernel -- fully in Non-Secure world while being
    // swapping in and out
    uint32_t key = irq_lock();

    // Request kernel work
    NimbeLink::Sdk::SecureServices::Kernel::PendSv();

    // Unlock interrupts again
    //
    // After this point, we should expect either our PendSV flag to be pended
    // for us, or the Secure world's process of pending PendSV for us to be
    // primed and ready to take over as soon as we would re-enter Thread mode
    // (in the ARM core's eyes).
    irq_unlock(key);
}
}
