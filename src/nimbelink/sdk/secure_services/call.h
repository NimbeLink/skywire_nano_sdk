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
#include <hal/nrf_egu.h>

#ifdef __cplusplus
extern "C"
{
#endif

/**
 * \brief Queues a secure service request
 *
 * \param request
 *      The request, consisting of a service and, optionally, an API
 * \param *parameters
 *      A pointer to a structure with arguments for the request
 * \param size
 *      The size of the parameter structure
 *
 * \return -EAGAIN
 *      Secure services not yet available
 * \return -ETIMEDOUT
 *      Failed to queue the request
 * \return <0
 *      An error occurred
 * \return 0
 *      Request will be serviced, and response will be sent
 * \return 1
 *      Request serviced, no response will be sent
 */
extern int32_t __PutSecureServiceRequest(uint32_t request, void *parameters, uint32_t size);

/**
 * \brief Gets a secure service request's response
 *
 * \param request
 *      The original request
 * \param *parameters
 *      A pointer to the structure with arguments from the request
 * \param size
 *      The size of the parameter structure
 *
 * \return -EAGAIN
 *      Secure services not yet available
 * \return -ETIMEDOUT
 *      Failed to get a response
 * \return int32_t
 *      The result of the request's handling
 */
extern int32_t __GetSecureServiceResponse(uint32_t request, void *parameters, uint32_t size);

extern int32_t CallSecureService(uint8_t service, uint16_t api, void *parameters, uint32_t size);

/**
 * \brief How many channels for secure services are available
 */
#define SECURE_SERVICE_CHANNEL_COUNT    4

/**
 * \brief A reserved channel for asynchronous secure service messages
 */
#define SECURE_SERVICE_ASYNC_CHANNEL    SECURE_SERVICE_CHANNEL_COUNT

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
 * \param channel
 *      The channel this request is being sent on
 * \param service
 *      The service being requested
 * \param api
 *      The service's unique API being requested
 *
 * \return uint32_t
 *      The request value
 */
#define CREATE_REQUEST(channel, service, api)       \
    (                                               \
        (((uint32_t)channel << 24) & 0xFF000000) |  \
        (((uint32_t)service << 16) & 0x00FF0000) |  \
        (uint32_t)api                               \
    )

/**
 * \brief Gets an 8-bit channel value from a request
 *
 * \param request
 *      The request whose channel to get
 *
 * \return uint8_t
 *      The channel value
 */
#define GET_CHANNEL(request)            ((uint8_t)((request >> 24) & 0x000000FF))

/**
 * \brief Gets a 8-bit service value from a request
 *
 * \param request
 *      The request whose service to get
 *
 * \return uint8_t
 *      The service value
 */
#define GET_SERVICE(request)            ((uint8_t)((request >> 16) & 0x000000FF))

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
}
#endif

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices
{
    static constexpr const std::size_t ChannelCount = SECURE_SERVICE_CHANNEL_COUNT;
    static constexpr const std::size_t AsyncChannel = SECURE_SERVICE_ASYNC_CHANNEL;

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

    static constexpr inline uint32_t CreateRequest(uint8_t channel, uint8_t service, uint16_t api)
    {
        return CREATE_REQUEST(channel, service, api);
    }

    static constexpr inline uint8_t GetChannel(uint32_t request)
    {
        return GET_CHANNEL(request);
    }

    static constexpr inline uint8_t GetService(uint32_t request)
    {
        return GET_SERVICE(request);
    }

    static constexpr inline uint16_t GetApi(uint32_t request)
    {
        return GET_API(request);
    }

    static inline int32_t Call(uint8_t service, uint16_t api, void *parameters = nullptr, uint32_t size = 0)
    {
        return CallSecureService(service, api, parameters, size);
    }

    template <typename T>
    static inline int32_t Call(uint8_t service, uint16_t api, T &parameters)
    {
        return CallSecureService(service, api, &parameters, sizeof(T));
    }
}
#endif
