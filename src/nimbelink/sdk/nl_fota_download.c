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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <at_cmd.h>
#include <at_notif.h>
#include <net/fota_download.h>

#include "nimbelink/sdk/at/cme.h"

// A callback to invoke with events
static fota_download_callback_t callback = NULL;

// Whether or not we've started FOTA
static bool fotaStarted = false;

/**
 * \brief Sends a FOTA event
 *
 * \param event
 *      The event to send
 *
 * \return none
 */
static inline void SendEvent(const struct fota_download_evt *event)
{
    // A pointer read is an atomic operation, so just grab it before we use it
    fota_download_callback_t _callback = callback;

    // If there's a callback, invoke it
    if (_callback != NULL)
    {
        _callback(event);
    }
}

/**
 * \brief Handles URCs from the AT interface
 *
 * \param *context
 *      A context
 * \param *urc
 *      The incoming URC
 *
 * \return none
 */
static void UrcCallback(void *context, const char *urc)
{
    (void)context;

    // If we haven't started FOTA, ignore this
    if (!fotaStarted)
    {
        return;
    }

    // If this doesn't look like a DFU URC, ignore this
    if (strncmp(urc, "DFU: ", 4) != 0)
    {
        return;
    }

    // Skip the URC's heading
    const char *start = strchr(urc, ' ');

    if (start == NULL)
    {
        return;
    }

    char *end = NULL;

    // Get the event ID
    uint32_t value = strtoul(start, &end, 0);

    // If it couldn't get a number, ignore this
    if ((value == 0) && (end == NULL))
    {
        return;
    }

    struct fota_download_evt event;

    // Figure out what happened
    switch (value)
    {
        // The DFU was rejected
        default:
        case 0:
        {
            fotaStarted = false;

            event = (struct fota_download_evt) {
                .id = FOTA_DOWNLOAD_EVT_ERROR
            };

            break;
        }

        // The DFU has been applied at the start of this boot
        //
        // We do not send events for this.
        case 1:
        {
            return;
        }

        // Progress has been made on the DFU
        case 2:
        {
        #   if CONFIG_FOTA_DOWNLOAD_PROGRESS_EVT
            uint32_t progress;

            // If we didn't find an end to the event ID when we converted it,
            // we won't know where to find our progress, so just default to
            // something
            if (end == NULL)
            {
                progress = 0;
            }
            // Else, continue parsing the next value, which should be separated
            // by a comma
            else
            {
                end++;

                // If the conversion fails, progress will be 0, which is a good
                // enough default
                progress = strtoul(end, &end, 0);
            }
        #   endif

            event = (struct fota_download_evt) {
                .id = FOTA_DOWNLOAD_EVT_PROGRESS,
            #   if CONFIG_FOTA_DOWNLOAD_PROGRESS_EVT
                .offset = progress
            #   endif
            };

            break;
        }

        // The DFU is pending a reboot
        case 3:
        {
            fotaStarted = false;

            event = (struct fota_download_evt) {
                .id = FOTA_DOWNLOAD_EVT_FINISHED
            };

            break;
        }
    }

    SendEvent(&event);
}

/**
 * \brief Initializes the FOTA download module
 *
 * \param client_callback
 *      A callback to register for events
 *
 * \return 0
 *      FOTA download initialized
 */
int fota_download_init(fota_download_callback_t client_callback)
{
    if (client_callback == NULL)
    {
        return -EINVAL;
    }

    at_notif_register_handler(NULL, UrcCallback);

    callback = client_callback;

    fotaStarted = false;

    return 0;
}

/**
 * \brief Starts a FOTA download process
 *
 * \param *host
 *      The host URL
 * \param *file
 *      The file to download from the host
 *
 * \return -ENOBUFS
 *      Host and file strings too large
 * \return -EALREADY
 *      FOTA download already in progress
 * \return -ENOEXEC
 *      The AT command failed for another reason
 * \return 0
 *      FOTA download started
 */
int fota_download_start(const char *host, const char *file)
{
    // If we've already started FOTA, ignore this
    if (fotaStarted)
    {
        return -EALREADY;
    }

    char command[CONFIG_AT_CMD_RESPONSE_MAX_LEN + 1];

    int length = snprintf(
        command,
        sizeof(command),
        "AT#XFOTA=%s,%s",
        host,
        file
    );

    // If that didn't all fit in the buffer, obviously this won't work
    if (length >= sizeof(command))
    {
        return -ENOBUFS;
    }

    enum at_cmd_state state;

    // Try to run our AT command
    int result = at_cmd_write(
        command,
        command,
        sizeof(command),
        &state
    );

    // If that failed, obviously it didn't start
    if (result != 0)
    {
        return result;
    }

    // If the AT command failed because one was already in progress, let the
    // caller know
    if ((state == AT_CMD_ERROR_CME) && (result == CME_PHONE_IS_BUSY))
    {
        return -EALREADY;
    }

    // If the AT command wasn't successful, use a generic error code
    if (state != AT_CMD_OK)
    {
        return -ENOEXEC;
    }

    // Note FOTA has started
    fotaStarted = false;

    return 0;
}
