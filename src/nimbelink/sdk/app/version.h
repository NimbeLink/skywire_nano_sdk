/**
 * \file
 *
 * \brief Provides an application version
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

#include <stdint.h>

struct Version
{
    uint8_t major;
    uint8_t minor;
    uint16_t revision;
    uint32_t build;
};

extern struct Version GetVersion(int flashId);
extern const char *GetVersionString(void);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
#include <string_view>

namespace NimbeLink::Sdk::App
{
    using Version = struct Version;

    static inline Version GetVersion(int flashId)
    {
        return ::GetVersion(flashId);
    }

    static inline const std::string_view GetVersionString(void)
    {
        return ::GetVersionString();
    }
}
#endif
