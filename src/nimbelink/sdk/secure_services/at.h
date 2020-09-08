/**
 * \file
 *
 * \brief Enumerates all available AT interface secure services
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

#include "nimbelink/sdk/at/cme.h"
#include "nimbelink/sdk/at/cms.h"
#include "nimbelink/sdk/at/extended_cme.h"
#include "nimbelink/sdk/secure_services/call.h"

/**
 * \brief The available AT secure service APIs
 */
enum At_Apis
{
    // Run an AT command
    At_Apis_RunCommand          = 0,

    // Subscribe to notifications of URCs
    At_Apis_SubscribeUrcs       = 1,

    // Reads the next available URC
    At_Apis_ReadUrc             = 2,
};

/**
 * \brief Possible results when running an AT command
 */
enum At_Result
{
    // The command ran successfully
    At_Result_Success    = 0,

    // A CME error value was returned in the parameters
    At_Result_Cme,

    // A CMS error value was returned in the parameters
    At_Result_Cms,

    // An extended CME erro value was returned in the parameters
    At_Result_ExtendedCme,
};

/**
 * \brief The corresponding error values for each command result
 */
union At_Error
{
    // The integer value itself
    int32_t value;

    // A CME error value
    CmeErrorType cmeError;

    // A CMS error value
    CmsErrorType cmsError;

    // A CME error value
    ExtendedCmeErrorType extendedCmeError;
};

struct At_RunCommandParameters
{
    // The command to run
    const char *command;

    // How long the command is
    uint32_t commandLength;

    // Where to put the response
    char *response;

    // The maximum response length, including NULL byte
    uint32_t maxLength;

    // Where to store the actual response length
    uint32_t responseLength;

    // The result of the command handling
    At_Result result;

    // The error that occurred, if any
    union At_Error error;
};

/**
 * \brief Runs an AT command
 *
 * \param *result
 *      Where to put the command's result
 * \param *error
 *      Where to put any error result
 * \param *command
 *      The command to run
 * \param commandLength
 *      How long the command is
 * \param *response
 *      Where to put the response
 * \param maxLength
 *      The maximum response length, including NULL byte
 * \param *responseLength
 *      Where to store the actual response length; can be NULL
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t At_RunCommand(
    At_Result *result,
    union At_Error *error,
    const char *command,
    uint32_t commandLength,
    char *response,
    uint32_t maxLength,
    uint32_t *responseLength
)
{
    struct At_RunCommandParameters parameters = {
        .command = command,
        .commandLength = commandLength,
        .response = response,
        .maxLength = maxLength
    };

    int32_t _result = Call(SecureService_At, At_Apis_RunCommand, &parameters, sizeof(parameters));

    // If the call itself has an error, it will be an errno-like value, so just
    // use that
    if (_result != 0)
    {
        return _result;
    }

    // Pass along the result, error type, and response length
    if (result != NULL)
    {
        *result = parameters.result;
    }

    if (error != NULL)
    {
        *error = parameters.error;
    }

    if (responseLength != NULL)
    {
        *responseLength = parameters.responseLength;
    }

    return 0;
}

typedef void (*At_UrcCallback)(void);

struct At_SubscribeUrcsParameters
{
    // A callback to invoke when a new URC is ready
    At_UrcCallback callback;
};

/**
 * \brief Subscribes to new URC notifications
 *
 * \param callback
 *      The callback to invoke when a new URC is ready
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t At_SubscribeUrcs(At_UrcCallback callback)
{
    struct At_SubscribeUrcsParameters parameters = {
        .callback = callback
    };

    return Call(SecureService_At, At_Apis_SubscribeUrcs, &parameters, sizeof(parameters));
}

struct At_ReadUrcParameters
{
    // Where to store the URC
    char *urc;

    // The maximum URC length, including NULL byte
    uint32_t maxLength;

    // Where to store the actual URC length
    uint32_t urcLength;
};

/**
 * \brief Reads the next available URC
 *
 * \param *urc
 *      Where to store the URC's contents
 * \param maxLength
 *      The maximum URC length, including NULL byte
 * \param *urcLength
 *      Where to store the actual URC length
 *
 * \return int32_t
 *      The result of the request
*/
static inline int32_t At_ReadUrc(
    char *urc,
    uint32_t maxLength,
    uint32_t *urcLength
)
{
    struct At_ReadUrcParameters parameters = {
        .urc = urc,
        .maxLength = maxLength
    };

    int32_t result = Call(SecureService_At, At_Apis_ReadUrc, &parameters, sizeof(parameters));

    if ((result == 0) && (urcLength != nullptr))
    {
        *urcLength = parameters.urcLength;
    }

    return result;
}

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices::At
{
    struct _Apis
    {
        enum _E
        {
            RunCommand      = At_Apis_RunCommand,
            SubscribeUrcs   = At_Apis_SubscribeUrcs,
            ReadUrc         = At_Apis_ReadUrc
        };
    };

    using Apis = _Apis::_E;

    struct _Result
    {
        enum _E
        {
            Success         = At_Result_Success,
            Cme             = At_Result_Cme,
            Cms             = At_Result_Cms,
            ExtendedCme     = At_Result_ExtendedCme
        };
    };

    using Result = _Result::_E;

    using Error = At_Error;

    using RunCommandParameters = At_RunCommandParameters;

    static inline int32_t RunCommand(
        Result *result,
        Error *error,
        const char *command,
        uint32_t commandLength,
        char *response,
        uint32_t maxLength,
        uint32_t *responseLength = nullptr
    )
    {
        return At_RunCommand(
            reinterpret_cast<At_Result *>(result),
            error,
            command,
            commandLength,
            response,
            maxLength,
            responseLength
        );
    }

    using UrcCallback = At_UrcCallback;
    using SubscribeUrcsParameters = At_SubscribeUrcsParameters;

    static inline int32_t SubscribeUrcs(UrcCallback callback)
    {
        return At_SubscribeUrcs(callback);
    }

    using ReadUrcParameters = At_ReadUrcParameters;

    static inline int32_t ReadUrc(
        char *urc,
        uint32_t maxLength,
        uint32_t *urcLength = nullptr
    )
    {
        return At_ReadUrc(urc, maxLength, urcLength);
    }
}
#endif
