/**
 * \file
 *
 * \brief Implements the fota_download library APIs
 *
 * (C) NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <modem/at_cmd.h>
#include <modem/at_notif.h>
#include <device.h>
#include <init.h>
#include <zephyr.h>

#include "nimbelink/sdk/secure_services/at.h"

// The callbacks we'll invoke when we get URCs
static at_cmd_handler_t handlers[1] = {NULL, };

// A semaphore for using the callback storage
static K_SEM_DEFINE(handlerSemaphore, 1, 1);

/**
 * \brief Handles an incoming URC notification from the Secure stack
 *
 *  The Secure Service API says we should treat the callback we get as if it
 *  were an interrupt, so we will pass the actual handling of reading the URCs
 *  and distributing them to our subscribers off to our work item.
 *
 * \param *buf
 *      The URC
 *
 * \return none
 */
static void UrcCallback(const char *buf)
{
    // Distribute the URC
    for (size_t i = 0; i < (sizeof(handlers)/sizeof(handlers[0])); i++)
    {
        k_sem_take(&handlerSemaphore, K_FOREVER);

        if (handlers[i] != NULL)
        {
            handlers[i](buf);
        }

        k_sem_give(&handlerSemaphore);
    }
}

/**
 * \brief Initializes the AT command module
 *
 *  The AT command interface is always available via the Secure Service APIs,
 *  so there's nothing to be done as far as initializing it. We will also
 *  handle URCs from it as the single sink, so we will set that up.
 *
 * \param none
 *
 * \return 0
 *      Always
 */
int at_cmd_init(void)
{
    // Subscribe to the Secure stack's URC notifications
    At_SubscribeUrcs(UrcCallback);

    return 0;
}

/**
 * \brief Initializes the AT command module
 *
 *  This helper is for the system initialization hook.
 *
 * \param *device
 *      Unused
 *
 * \return int
 *      Refer to at_cmd_init()
 */
static __attribute__((unused)) int _at_cmd_init(struct device *device)
{
    (void)device;

    return at_cmd_init();
}

/**
 * \brief Runs an AT command
 *
 * \param *cmd
 *      The AT command to run
 * \param handler
 *      A callback to invoke with a response
 *
 * \return -ENOBUFS
 *      AT_CMD_RESPONSE_MAX_LEN is not large enough to hold the data returned
 *      from the modem
 * \return ENOEXEC
 *      The modem returned ERROR
 * \return -EMSGSIZE
 *      The supplied buffer is too small or NULL
 * \return -EIO
 *      The function failed to send the command
 * \return 0
 *      The command execution was successful (same as OK returned from
 *      modem). Error codes returned from the Secure Service API are
 *      returned as negative values; CMS and CME errors are returned as
 *      positive values. The state parameter will indicate if it's a CME
 *      or CMS error. ERROR will return ENOEXEC (positve).
 */
int at_cmd_write_with_callback(
    const char *const cmd,
    at_cmd_handler_t  handler
)
{
    // It seems that the response length should include a spot for the NULL
    // byte, but whatever; just include that manually
    char buf[CONFIG_AT_CMD_RESPONSE_MAX_LEN + 1];

    int result = at_cmd_write(
        cmd,
        buf,
        sizeof(buf),
        NULL
    );

    // If that failed, don't call the callback
    if (result != 0)
    {
        return result;
    }

    if (handler != NULL)
    {
        handler(buf);
    }

    return 0;
}

/**
 * \brief Runs an AT command
 *
 * \param *cmd
 *      The AT command to run
 * \param *buf
 *      The buffer to write the response to
 * \param buf_len
 *      The maximum amount of buffer space
 * \param *state
 *      Where to put the final outcome
 *
 * \return -ENOBUFS
 *      AT_CMD_RESPONSE_MAX_LEN is not large enough to hold the data returned
 *      from the modem
 * \return ENOEXEC
 *      The modem returned ERROR
 * \return -EMSGSIZE
 *      The supplied buffer is too small or NULL
 * \return -EIO
 *      The function failed to send the command
 * \return 0
 *      The command execution was successful (same as OK returned from
 *      modem). Error codes returned from the Secure Service API are
 *      returned as negative values; CMS and CME errors are returned as
 *      positive values. The state parameter will indicate if it's a CME
 *      or CMS error. ERROR will return ENOEXEC (positve).
 */
int at_cmd_write(
    const char *const cmd,
    char *buf,
    size_t buf_len,
    enum at_cmd_state *state
)
{
    enum At_Result atResult;
    union At_Error atError;
    uint32_t responseLength;

    int32_t result = At_RunCommand(
        &atResult,
        &atError,
        cmd,
        strlen(cmd),
        buf,
        buf_len,
        &responseLength
    );

    // If something bad happened -- outside of the context of the AT command's
    // handling itself by the Secure stack -- use that as our error code
    if (result != 0)
    {
        return -abs(result);
    }

    // Assume it's going to be some generic error
    //
    // We don't expect to ever have a non-specific AT error, but might as well
    // be diligent.
    enum at_cmd_state _state = AT_CMD_ERROR;
    result = abs(atError.value);

    // Figure out how to convert our response
    switch (atResult)
    {
        case At_Result_Success:
        {
            _state = AT_CMD_OK;
            result = 0;
            break;
        }

        case At_Result_Cme:
        {
            _state = AT_CMD_ERROR_CME;
            result = abs(atError.cmeError);
            break;
        }

        case At_Result_ExtendedCme:
        {
            _state = AT_CMD_ERROR_CME;
            result = abs(atError.extendedCmeError);
            break;
        }

        case At_Result_Cms:
        {
            _state = AT_CMD_ERROR_CMS;
            result = abs(atError.cmeError);
            break;
        }
    }

    // If they wanted it, give the state
    if (state != NULL)
    {
        *state = _state;
    }

    return result;
}

/**
 * \brief Saves a callback handler for notifications from the AT interface
 *
 * \param handler
 *      The handler to set
 *
 * \return none
 */
void at_cmd_set_notification_handler(at_cmd_handler_t handler)
{
    if (handler == NULL)
    {
        return;
    }

    k_sem_take(&handlerSemaphore, K_FOREVER);

    for (size_t i = 0; i < (sizeof(handlers)/sizeof(handlers[0])); i++)
    {
        // If this handler isn't set, use it
        if (handlers[i] == NULL)
        {
            handlers[i] = handler;
            break;
        }
    }

    k_sem_give(&handlerSemaphore);
}

#ifdef CONFIG_AT_CMD_SYS_INIT
SYS_INIT(
    _at_cmd_init,
    APPLICATION,
    CONFIG_AT_CMD_INIT_PRIORITY
);
#endif
