/**
 * \file
 *
 * \brief Defines asynchronous secure service messages
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

#ifdef __cplusplus
extern "C"
{
#endif

/**
 * \brief The available asynchronous messages we can get
 */
enum Async_Event
{
    // A new AT URC
    Async_Event_AtUrc       = 0,
};

struct Async_Parameters
{
    // The event that occurred
    uint32_t event;

    // A buffer for generic data
    uint8_t buffer[1024];
};

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices::Async
{
    struct _Event
    {
        enum _E
        {
            AtUrc           = Async_Event_AtUrc,
        };
    };

    using Event = _Event::_E;

    using Parameters = Async_Parameters;
}
#endif
