/**
 * \file
 *
 * \brief Requests Non-Secure access to configured peripherals
 *
 * (C) NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#include <stddef.h>
#include <stdint.h>

#include <init.h>
#include <nrf9160.h>

#include "nimbelink/sdk/secure_services/kernel.h"

/**
 * \brief Handles requesting Non-Secure access to needed peripherals
 *
 * \param *device
 *      Unused
 *
 * \return 0
 *      Always
 */
static int RequestPeripherals(struct device *device)
{
    static const uintptr_t Peripherals[] = {
    #   if CONFIG_REQUEST_NON_SECURE_UARTE_1
        NRF_UARTE1_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_UARTE_2
        NRF_UARTE2_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_UARTE_3
        NRF_UARTE3_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_SAADC
        NRF_SAADC_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_TIMER_0
        NRF_TIMER0_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_TIMER_1
        NRF_TIMER1_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_TIMER_2
        NRF_TIMER2_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_RTC_1
        NRF_RTC1_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_DPPIC
        NRF_DPPIC_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_EGU_1
        NRF_EGU1_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_EGU_2
        NRF_EGU2_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_EGU_3
        NRF_EGU3_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_EGU_4
        NRF_EGU4_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_EGU_5
        NRF_EGU5_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_PWM_0
        NRF_PWM0_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_PWM_1
        NRF_PWM1_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_PWM_2
        NRF_PWM2_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_PWM_3
        NRF_PWM3_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_PDM
        NRF_PDM_NS_BASE,
    #   endif
    #   if CONFIG_REQUEST_NON_SECURE_I2S
        NRF_I2S_NS_BASE,
    #   endif
    };

    (void)device;

    for (size_t i = 0; i < (sizeof(Peripherals)/sizeof(Peripherals[0])); i++)
    {
        int32_t result = Kernel_PeripheralAccess((const void *)(Peripherals[i]));

        if (result != 0)
        {
            return result;
        }
    }

    return 0;
}

// Run our access request handling during system initialization, as early as
// possible (to beat any driver initializations that depend on access to the
// peripherals)
SYS_INIT(RequestPeripherals, PRE_KERNEL_1, 0);
