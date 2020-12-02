/**
 * \file
 *
 * \brief Handles a Non-Secure fatal errors
 *
 * (C) NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#include <arch/cpu.h>
#include <fatal.h>
#include <logging/log.h>
#include <logging/log_ctrl.h>

#include "nimbelink/sdk/secure_services/kernel.h"

LOG_MODULE_REGISTER(fatal_error, LOG_LEVEL_INF);

/**
 * \brief Handles a fatal system error
 *
 *  This will allow the fatal error to go unhandled, allowing the Secure
 *  firmware to handle the error and prevent the Non-Secure application from
 *  being launched during the next, immediate reboot.
 *
 * \param reason
 *      The reason for the fatal error
 * \param *esf
 *      The stack frame
 *
 * \return none
 */
void k_sys_fatal_error_handler(unsigned int reason, const z_arch_esf_t *esf)
{
	(void)esf;
	(void)reason;

	LOG_ERR("Resetting the system");
	LOG_WRN("Preventing application from running next boot");
	LOG_PANIC();

    Kernel_Reset(KERNEL_RESET_SKIP_LAUNCH);
}
