/**
 * \file
 *
 * \brief A collection of secure 'services' available for use in Non-Secure
 *        firmware
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

#ifdef __cplusplus
extern "C"
{
#endif
/**
 * \brief Handles a secure service request
 *
 * \param request
 *      The request, consisting of a service and, optionally, an API
 * \param *parameters
 *      A pointer to a structure with arguments for the request
 * \param size
 *      The size of the parameter structure
 *
 * \return int32_t
 *      The result of the request
 */
extern int32_t __Call(uint32_t request, void *parameters, uint32_t size);
#ifdef __cplusplus
}
#endif

/**
 * \brief The available secure services
 */
enum SecureService
{
    SecureService_Kernel    = 0,
    SecureService_At        = 1,
    SecureService_App       = 2,
    SecureService_Net       = 3,
};

/**
 * \brief Creates a 32-bit request value from a service and an API
 *
 * \param service
 *      The service being requested
 * \param api
 *      The service's unique API being requested
 *
 * \return uint32_t
 *      The request value
 */
#define CREATE_REQUEST(service, api)    ((((uint32_t)service << 16) & 0xFFFF0000) | (uint32_t)api)

/**
 * \brief Gets a 16-bit service value from a request
 *
 * \param request
 *      The request whose service to get
 *
 * \return uint16_t
 *      The service value
 */
#define GET_SERVICE(request)            ((uint16_t)((request >> 16) & 0x0000FFFF))

/**
 * \brief Gets a 16-bit API value from a request
 *
 * \param request
 *      The request whose API to get
 *
 * \return uint16_t
 *      The API value
 */
#define GET_API(request)                ((uint16_t)(request & 0x0000FFFF))

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices
{
    struct _Service
    {
        enum _E
        {
            Kernel  = SecureService_Kernel,
            At      = SecureService_At,
            App     = SecureService_App,
            Net     = SecureService_Net,
        };
    };

    using Service = _Service::_E;

    static constexpr inline uint32_t CreateRequest(uint16_t service, uint16_t api)
    {
        return CREATE_REQUEST(service, api);
    }

    static constexpr inline uint16_t GetService(uint32_t request)
    {
        return GET_SERVICE(request);
    }

    static constexpr inline uint16_t GetApi(uint32_t request)
    {
        return GET_API(request);
    }
}
#endif

#if __ZEPHYR__
#include "nimbelink/sdk/secure_services/helpers/zephyr.h"
#endif
