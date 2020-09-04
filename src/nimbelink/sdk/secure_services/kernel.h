/**
 * \file
 *
 * \brief Enumerates all available kernel secure services
 *
 * © NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#pragma once

#include <stdint.h>

#include "nimbelink/sdk/secure_services/call.h"

/**
 * \brief The available APIs
 */
enum Kernel_Apis
{
    // Trigger the Non-Secure kernel's context switcher
    Kernel_Apis_PendSv              = 0,

    // Request Non-Secure access to a peripheral
    Kernel_Apis_PeripheralAccess    = 1,
};

/**
 * \brief Requests kernel work
 *
 * \param none
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t Kernel_PendSv(void)
{
    return __Call(CREATE_REQUEST(SecureService_Kernel, Kernel_Apis_PendSv), NULL, 0);
}

struct Kernel_PeripheralAccessParameters
{
    // The peripheral in memory
    const void *peripheral;
};

/**
 * \brief Requests Non-Secure access to a peripheral
 *
 * \param *peripheral
 *      The peripheral in memory
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t Kernel_PeripheralAccess(const void *peripheral)
{
    struct Kernel_PeripheralAccessParameters parameters = {
        .peripheral = peripheral
    };

    return Call(SecureService_Kernel, Kernel_Apis_PeripheralAccess, &parameters, sizeof(parameters));
}

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices::Kernel
{
    struct _Apis
    {
        enum _E
        {
            PendSv              = Kernel_Apis_PendSv,
            PeripheralAccess    = Kernel_Apis_PeripheralAccess
        };
    };

    using Apis = _Apis::_E;

    static inline int32_t PendSv(void)
    {
        return Kernel_PendSv();
    }

    using PeripheralAccessParameters = Kernel_PeripheralAccessParameters;

    static inline int32_t PeripheralAccess(const void *peripheral)
    {
        return Kernel_PeripheralAccess(peripheral);
    }
}
#endif
