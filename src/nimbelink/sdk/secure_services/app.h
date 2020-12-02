/**
 * \file
 *
 * \brief Enumerates all available application secure services
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

#include <stdint.h>

#include "nimbelink/sdk/secure_services/call.h"

#ifdef __cplusplus
extern "C"
{
#endif

/**
 * \brief The available APIs
 */
enum App_Api
{
    // Write a new signing/encryption key
    App_Api_AddKey                  = 0,
};

struct App_AddKeyParameters
{
    // The key's data
    const void *key;

    // The key's length, in bytes
    uint32_t length;
};

/**
 * \brief Requests adding a signing/encryption key
 *
 * \param *key
 *      The key's data
 * \param length
 *      The key's length, in bytes
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t App_AddKey(const void *key, uint32_t length)
{
    struct App_AddKeyParameters parameters = {
        .key = key,
        .length = length
    };

    return CallSecureService(SecureService_App, App_Api_AddKey, &parameters, sizeof(parameters));
}

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices::App
{
    struct _Api
    {
        enum _E
        {
            AddKey              = App_Api_AddKey,
        };
    };

    using Api = _Api::_E;

    using AddKeyParameters = App_AddKeyParameters;

    static inline int32_t AddKey(const void *key, uint32_t length)
    {
        return App_AddKey(key, length);
    }
}
#endif
