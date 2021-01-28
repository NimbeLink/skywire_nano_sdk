/**
 * \file
 *
 * \brief Enumerates all available networking secure services
 *
 *  Because these APIs are entirely a wrapper around pass-through socket
 *  operations that are well-defined by existing standards, the documentation
 *  of individual meaning of enumerations, parameters, and functions is not
 *  going to be reproduced here. For information on these aspects, refer to the
 *  standard POSIX standards.
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

#include <net/socket.h>

#include "nimbelink/sdk/secure_services/call.h"

#ifdef __cplusplus
extern "C"
{
#endif

enum Net_Api
{
    Net_Api_Socket          = 0,
    Net_Api_Close           = 1,
    Net_Api_Accept          = 2,
    Net_Api_Bind            = 3,
    Net_Api_Listen          = 4,
    Net_Api_Connect         = 5,
    Net_Api_Poll            = 6,
    Net_Api_SetSockOpt      = 7,
    Net_Api_GetSockOpt      = 8,
    Net_Api_Recv            = 9,
    Net_Api_RecvFrom        = 10,
    Net_Api_Send            = 11,
    Net_Api_SendTo          = 12,
    Net_Api_GetAddrInfo     = 13,
    Net_Api_FreeAddrInfo    = 14,
    Net_Api_Fcntl           = 15,
};

struct Net_SocketParameters
{
    int32_t family;
    int32_t type;
    int32_t proto;
};

struct Net_CloseParameters
{
    int32_t fd;
};

struct Net_AcceptParameters
{
    int32_t fd;
    struct sockaddr *addr;
    uint32_t *addrlen;
};

struct Net_BindParameters
{
    int32_t fd;
    const struct sockaddr *addr;
    uint32_t addrlen;
};

struct Net_ListenParameters
{
    int32_t fd;
    int32_t backlog;
};

struct Net_ConnectParameters
{
    int32_t fd;
    const struct sockaddr *addr;
    uint32_t addrlen;
};

struct Net_PollParameters
{
    struct pollfd *fds;
    int32_t nfds;
    int32_t timeout;
};

struct Net_SetSockOptParameters
{
    int32_t fd;
    int32_t level;
    int32_t optname;
    const void *optval;
    uint32_t optlen;
};

struct Net_GetSockOptParameters
{
    int32_t fd;
    int32_t level;
    int32_t optname;
    void *optval;
    uint32_t *optlen;
};

struct Net_RecvParameters
{
    int32_t fd;
    void *buf;
    uint32_t max_len;
    int32_t flags;
};

struct Net_RecvFromParameters
{
    int32_t fd;
    void *buf;
    int16_t len;
    int16_t flags;
    struct sockaddr *from;
    uint32_t *fromlen;
};

struct Net_SendParameters
{
    int32_t fd;
    const void *buf;
    uint32_t len;
    int32_t flags;
};

struct Net_SendToParameters
{
    int32_t fd;
    const void *buf;
    uint32_t len;
    int32_t flags;
    const struct sockaddr *to;
    uint32_t tolen;
};

/**
 * \brief A proper POSIX addrinfo struct
 *
 *  Zephyr appears to have taken to defining addrinfo as their zsock_addrinfo
 *  structure in recent versions, which is decidedly *not* what addrinfo
 *  actually is. As such, to remain compatible with the Skywire Nano stack
 *  firmware handling, this structure format will be used.
 */
struct nl_addrinfo
{
    int ai_flags;
    int ai_family;
    int ai_socktype;
    int ai_protocol;
    socklen_t ai_addrlen;
    struct sockaddr *ai_addr;
    char *ai_canonname;
    struct nl_addrinfo *ai_next;
};

struct Net_GetAddrInfoParameters
{
    const char *node;
    const char *service;
    const struct nl_addrinfo *hints;
    uint32_t reslen;
    struct nl_addrinfo **res;
};

#define NET_AI_CANONNAME_MAX_LENGTH     20

struct Net_FreeAddrInfoParameters
{
    struct addrinfo *root;
};

struct Net_FcntlParameters
{
    int32_t fd;
    int32_t cmd;

    // fcntl() typically takes variable arguments, but the Nordic sockets are
    // limited to a single 32-bit integer argument in their handling anyway
    int32_t args;
};

static inline int32_t Net_Socket(int32_t family, int32_t type, int32_t proto)
{
    struct Net_SocketParameters parameters = {
        .family = family,
        .type = type,
        .proto = proto
    };

    return CallSecureService(SecureService_Net, Net_Api_Socket, &parameters, sizeof(parameters));
}

static inline int32_t Net_Close(int32_t fd)
{
    struct Net_CloseParameters parameters = {
        .fd = fd
    };

    return CallSecureService(SecureService_Net, Net_Api_Close, &parameters, sizeof(parameters));
}

static inline int32_t Net_Accept(int32_t fd, struct sockaddr *addr, uint32_t *addrlen)
{
    struct Net_AcceptParameters parameters = {
        .fd = fd,
        .addr = addr,
        .addrlen = addrlen
    };

    return CallSecureService(SecureService_Net, Net_Api_Accept, &parameters, sizeof(parameters));
}

static inline int32_t Net_Bind(int32_t fd, const struct sockaddr *addr, uint32_t addrlen)
{
    struct Net_BindParameters parameters = {
        .fd = fd,
        .addr = addr,
        .addrlen = addrlen
    };

    return CallSecureService(SecureService_Net, Net_Api_Bind, &parameters, sizeof(parameters));
}

static inline int32_t Net_Listen(int32_t fd, int32_t backlog)
{
    struct Net_ListenParameters parameters = {
        .fd = fd,
        .backlog = backlog
    };

    return CallSecureService(SecureService_Net, Net_Api_Listen, &parameters, sizeof(parameters));
}

static inline int32_t Net_Connect(int32_t fd, const struct sockaddr *addr, uint32_t addrlen)
{
    struct Net_ConnectParameters parameters = {
        .fd = fd,
        .addr = addr,
        .addrlen = addrlen
    };

    return CallSecureService(SecureService_Net, Net_Api_Connect, &parameters, sizeof(parameters));
}

static inline int32_t Net_Poll(struct pollfd *fds, int32_t nfds, int32_t timeout)
{
    struct Net_PollParameters parameters = {
        .fds = fds,
        .nfds = nfds,
        .timeout = timeout
    };

    return CallSecureService(SecureService_Net, Net_Api_Poll, &parameters, sizeof(parameters));
}

static inline int32_t Net_SetSockOpt(int32_t fd, int32_t level, int32_t optname, const void *optval, uint32_t optlen)
{
    struct Net_SetSockOptParameters parameters = {
        .fd = fd,
        .level = level,
        .optname = optname,
        .optval = optval,
        .optlen = optlen
    };

    return CallSecureService(SecureService_Net, Net_Api_SetSockOpt, &parameters, sizeof(parameters));
}

static inline int32_t Net_GetSockOpt(int32_t fd, int32_t level, int32_t optname, void *optval, uint32_t *optlen)
{
    struct Net_GetSockOptParameters parameters = {
        .fd = fd,
        .level = level,
        .optname = optname,
        .optval = optval,
        .optlen = optlen
    };

    return CallSecureService(SecureService_Net, Net_Api_GetSockOpt, &parameters, sizeof(parameters));
}

static inline int32_t Net_Recv(int32_t fd, void *buf, uint32_t max_len, int32_t flags)
{
    struct Net_RecvParameters parameters = {
        .fd = fd,
        .buf = buf,
        .max_len = max_len,
        .flags = flags
    };

    return CallSecureService(SecureService_Net, Net_Api_Recv, &parameters, sizeof(parameters));
}

static inline int32_t Net_RecvFrom(int32_t fd, void *buf, int16_t len, int16_t flags, struct sockaddr *from, uint32_t *fromlen)
{
    struct Net_RecvFromParameters parameters = {
        .fd = fd,
        .buf = buf,
        .len = len,
        .flags = flags,
        .from = from,
        .fromlen = fromlen
    };

    return CallSecureService(SecureService_Net, Net_Api_RecvFrom, &parameters, sizeof(parameters));
}

static inline int32_t Net_Send(int32_t fd, const void *buf, uint32_t len, int32_t flags)
{
    struct Net_SendParameters parameters = {
        .fd = fd,
        .buf = buf,
        .len = len,
        .flags = flags
    };

    return CallSecureService(SecureService_Net, Net_Api_Send, &parameters, sizeof(parameters));
}

static inline int32_t Net_SendTo(int32_t fd, const void *buf, uint32_t len, int32_t flags, const struct sockaddr *to, uint32_t tolen)
{
    struct Net_SendToParameters parameters = {
        .fd = fd,
        .buf = buf,
        .len = len,
        .flags = flags,
        .to = to,
        .tolen = tolen
    };

    return CallSecureService(SecureService_Net, Net_Api_SendTo, &parameters, sizeof(parameters));
}

static inline int32_t Net_GetAddrInfo(const char *node, const char *service, const struct nl_addrinfo *hints, uint32_t reslen, struct nl_addrinfo **res)
{
    struct Net_GetAddrInfoParameters parameters = {
        .node = node,
        .service = service,
        .hints = hints,
        .reslen = reslen,
        .res = res
    };

    return CallSecureService(SecureService_Net, Net_Api_GetAddrInfo, &parameters, sizeof(parameters));
}

static inline int32_t Net_FreeAddrInfo(struct addrinfo *root)
{
    struct Net_FreeAddrInfoParameters parameters = {
        .root = root
    };

    return CallSecureService(SecureService_Net, Net_Api_FreeAddrInfo, &parameters, sizeof(parameters));
}

static inline int32_t Net_Fcntl(int32_t fd, int32_t cmd, int32_t args)
{
    struct Net_FcntlParameters parameters = {
        .fd = fd,
        .cmd = cmd,
        .args = args
    };

    return CallSecureService(SecureService_Net, Net_Api_Fcntl, &parameters, sizeof(parameters));
}

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
#include <utility>

namespace NimbeLink::Sdk::SecureServices::Net
{
    struct _Api
    {
        enum _E
        {
            Socket          = Net_Api_Socket,
            Close           = Net_Api_Close,
            Accept          = Net_Api_Accept,
            Bind            = Net_Api_Bind,
            Listen          = Net_Api_Listen,
            Connect         = Net_Api_Connect,
            Poll            = Net_Api_Poll,
            SetSockOpt      = Net_Api_SetSockOpt,
            GetSockOpt      = Net_Api_GetSockOpt,
            Recv            = Net_Api_Recv,
            RecvFrom        = Net_Api_RecvFrom,
            Send            = Net_Api_Send,
            SendTo          = Net_Api_SendTo,
            GetAddrInfo     = Net_Api_GetAddrInfo,
            FreeAddrInfo    = Net_Api_FreeAddrInfo,
            Fcntl           = Net_Api_Fcntl,
        };
    };

    using Api = _Api::_E;

    using SocketParameters          = Net_SocketParameters;
    using CloseParameters           = Net_CloseParameters;
    using AcceptParameters          = Net_AcceptParameters;
    using BindParameters            = Net_BindParameters;
    using ListenParameters          = Net_ListenParameters;
    using ConnectParameters         = Net_ConnectParameters;
    using PollParameters            = Net_PollParameters;
    using SetSockOptParameters      = Net_SetSockOptParameters;
    using GetSockOptParameters      = Net_GetSockOptParameters;
    using RecvParameters            = Net_RecvParameters;
    using RecvFromParameters        = Net_RecvFromParameters;
    using SendParameters            = Net_SendParameters;
    using SendToParameters          = Net_SendToParameters;
    using GetAddrInfoParameters     = Net_GetAddrInfoParameters;
    using FreeAddrInfoParameters    = Net_FreeAddrInfoParameters;
    using FcntlParameters           = Net_FcntlParameters;

    template <typename... Args>
    static inline int32_t Socket(Args&&... args)
    {
        return Net_Socket(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Close(Args&&... args)
    {
        return Net_Close(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Accept(Args&&... args)
    {
        return Net_Accept(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Bind(Args&&... args)
    {
        return Net_Bind(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Listen(Args&&... args)
    {
        return Net_Listen(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Connect(Args&&... args)
    {
        return Net_Connect(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Poll(Args&&... args)
    {
        return Net_Poll(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t SetSockOpt(Args&&... args)
    {
        return Net_SetSockOpt(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t GetSockOpt(Args&&... args)
    {
        return Net_GetSockOpt(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Recv(Args&&... args)
    {
        return Net_Recv(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t RecvFrom(Args&&... args)
    {
        return Net_RecvFrom(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Send(Args&&... args)
    {
        return Net_Send(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t SendTo(Args&&... args)
    {
        return Net_SendTo(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t GetAddrInfo(Args&&... args)
    {
        return Net_GetAddrInfo(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t FreeAddrInfo(Args&&... args)
    {
        return Net_FreeAddrInfo(std::forward<Args>(args)...);
    }

    template <typename... Args>
    static inline int32_t Fcntl(Args&&... args)
    {
        return Net_Fcntl(std::forward<Args>(args)...);
    }

}
#endif
