/**
 * \file
 *
 * \brief Enumerates all available kernel secure services
 *
 * (C) NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#pragma once

#include <errno.h>
#include <stdint.h>

#include "nimbelink/sdk/secure_services/call.h"

#ifdef __cplusplus
extern "C"
{
#endif

/**
 * \brief The available APIs
 */
enum Kernel_Api
{
    // Trigger the Non-Secure kernel's context switcher
    Kernel_Api_PendSv               = 0,

    // Request Non-Secure access to a peripheral
    Kernel_Api_PeripheralAccess     = 1,

    // Mark the Non-Secure image as valid
    Kernel_Api_MarkImageValid       = 2,

    // Get the current errno value
    Kernel_Api_Errno                = 3,

    // Reset
    Kernel_Api_Reset                = 4,
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
    return CallSecureService(SecureService_Kernel, Kernel_Api_PendSv, NULL, 0);
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

    return CallSecureService(SecureService_Kernel, Kernel_Api_PeripheralAccess, &parameters, sizeof(parameters));
}

/**
 * \brief Requests marking the Non-Secure image as valid
 *
 * \param none
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t Kernel_MarkImageValid(void)
{
    return CallSecureService(SecureService_Kernel, Kernel_Api_MarkImageValid, NULL, 0);
}

struct Kernel_ErrnoParameters
{
    int32_t errnoValue;
};

/**
 * \brief Gets the latest errno value
 *
 * \param none
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t Kernel_Errno(void)
{
    struct Kernel_ErrnoParameters parameters;

    int32_t result = CallSecureService(SecureService_Kernel, Kernel_Api_Errno, &parameters, sizeof(parameters));

    if (result == 0)
    {
        errno = parameters.errnoValue;
    }

    return result;
}

/**
 * \brief Requests skipping launching the application after the reset
 */
#define KERNEL_RESET_SKIP_LAUNCH    (1U << 0)

struct Kernel_ResetParameters
{
    // Flags for the reset handling
    uint32_t flags;
};

/**
 * \brief Requests a reset
 *
 *  If 'successful', this function will not return.
 *
 * \param flags
 *      Flags for the reset handling
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t Kernel_Reset(uint32_t flags)
{
    struct Kernel_ResetParameters parameters = {
        .flags = flags
    };

    return CallSecureService(SecureService_Kernel, Kernel_Api_Reset, &parameters, sizeof(parameters));
}

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices::Kernel
{
    struct _Api
    {
        enum _E
        {
            PendSv              = Kernel_Api_PendSv,
            PeripheralAccess    = Kernel_Api_PeripheralAccess,
            MarkImageValid      = Kernel_Api_MarkImageValid,
            Errno               = Kernel_Api_Errno,
            Reset               = Kernel_Api_Reset,
        };
    };

    using Api = _Api::_E;

    static inline int32_t PendSv(void)
    {
        return Kernel_PendSv();
    }

    using PeripheralAccessParameters = Kernel_PeripheralAccessParameters;

    static inline int32_t PeripheralAccess(const void *peripheral)
    {
        return Kernel_PeripheralAccess(peripheral);
    }

    static inline int32_t MarkImageValid(void)
    {
        return Kernel_MarkImageValid();
    }

    using ErrnoParameters = Kernel_ErrnoParameters;

    static inline int32_t Errno(void)
    {
        return Kernel_Errno();
    }

    namespace ResetFlag
    {
        static constexpr const uint32_t SkipLaunch = KERNEL_RESET_SKIP_LAUNCH;
    };

    using ResetParameters = Kernel_ResetParameters;

    static inline int32_t Reset(uint32_t flags = 0)
    {
        return Kernel_Reset(flags);
    }
}
#endif
