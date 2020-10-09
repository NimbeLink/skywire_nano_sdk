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

enum Net_Apis
{
    Net_Apis_Socket         = 0,
    Net_Apis_Close          = 1,
    Net_Apis_Accept         = 2,
    Net_Apis_Bind           = 3,
    Net_Apis_Listen         = 4,
    Net_Apis_Connect        = 5,
    Net_Apis_Poll           = 6,
    Net_Apis_SetSockOpt     = 7,
    Net_Apis_GetSockOpt     = 8,
    Net_Apis_Recv           = 9,
    Net_Apis_RecvFrom       = 10,
    Net_Apis_Send           = 11,
    Net_Apis_SendTo         = 12,
    Net_Apis_GetAddrInfo    = 13,
    Net_Apis_FreeAddrInfo   = 14,
    Net_Apis_Fcntl          = 15,
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

struct Net_GetAddrInfoParameters
{
    const char *node;
    const char *service;
    const struct addrinfo *hints;
    uint32_t reslen;
    struct addrinfo **res;
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
    va_list args;
};

static inline int32_t Net_Socket(int32_t family, int32_t type, int32_t proto)
{
    struct Net_SocketParameters parameters = {
        .family = family,
        .type = type,
        .proto = proto
    };

    return Call(SecureService_Net, Net_Apis_Socket, &parameters, sizeof(parameters));
}

static inline int32_t Net_Close(int32_t fd)
{
    struct Net_CloseParameters parameters = {
        .fd = fd
    };

    return Call(SecureService_Net, Net_Apis_Close, &parameters, sizeof(parameters));
}

static inline int32_t Net_Accept(int32_t fd, struct sockaddr *addr, uint32_t *addrlen)
{
    struct Net_AcceptParameters parameters = {
        .fd = fd,
        .addr = addr,
        .addrlen = addrlen
    };

    return Call(SecureService_Net, Net_Apis_Accept, &parameters, sizeof(parameters));
}

static inline int32_t Net_Bind(int32_t fd, const struct sockaddr *addr, uint32_t addrlen)
{
    struct Net_BindParameters parameters = {
        .fd = fd,
        .addr = addr,
        .addrlen = addrlen
    };

    return Call(SecureService_Net, Net_Apis_Bind, &parameters, sizeof(parameters));
}

static inline int32_t Net_Listen(int32_t fd, int32_t backlog)
{
    struct Net_ListenParameters parameters = {
        .fd = fd,
        .backlog = backlog
    };

    return Call(SecureService_Net, Net_Apis_Listen, &parameters, sizeof(parameters));
}

static inline int32_t Net_Connect(int32_t fd, const struct sockaddr *addr, uint32_t addrlen)
{
    struct Net_ConnectParameters parameters = {
        .fd = fd,
        .addr = addr,
        .addrlen = addrlen
    };

    return Call(SecureService_Net, Net_Apis_Connect, &parameters, sizeof(parameters));
}

static inline int32_t Net_Poll(struct pollfd *fds, int32_t nfds, int32_t timeout)
{
    struct Net_PollParameters parameters = {
        .fds = fds,
        .nfds = nfds,
        .timeout = timeout
    };

    return Call(SecureService_Net, Net_Apis_Poll, &parameters, sizeof(parameters));
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

    return Call(SecureService_Net, Net_Apis_SetSockOpt, &parameters, sizeof(parameters));
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

    return Call(SecureService_Net, Net_Apis_GetSockOpt, &parameters, sizeof(parameters));
}

static inline int32_t Net_Recv(int32_t fd, void *buf, uint32_t max_len, int32_t flags)
{
    struct Net_RecvParameters parameters = {
        .fd = fd,
        .buf = buf,
        .max_len = max_len,
        .flags = flags
    };

    return Call(SecureService_Net, Net_Apis_Recv, &parameters, sizeof(parameters));
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

    return Call(SecureService_Net, Net_Apis_RecvFrom, &parameters, sizeof(parameters));
}

static inline int32_t Net_Send(int32_t fd, const void *buf, uint32_t len, int32_t flags)
{
    struct Net_SendParameters parameters = {
        .fd = fd,
        .buf = buf,
        .len = len,
        .flags = flags
    };

    return Call(SecureService_Net, Net_Apis_Send, &parameters, sizeof(parameters));
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

    return Call(SecureService_Net, Net_Apis_SendTo, &parameters, sizeof(parameters));
}

static inline int32_t Net_GetAddrInfo(const char *node, const char *service, const struct addrinfo *hints, uint32_t reslen, struct addrinfo **res)
{
    struct Net_GetAddrInfoParameters parameters = {
        .node = node,
        .service = service,
        .hints = hints,
        .reslen = reslen,
        .res = res
    };

    return Call(SecureService_Net, Net_Apis_GetAddrInfo, &parameters, sizeof(parameters));
}

static inline int32_t Net_FreeAddrInfo(struct addrinfo *root)
{
    struct Net_FreeAddrInfoParameters parameters = {
        .root = root
    };

    return Call(SecureService_Net, Net_Apis_FreeAddrInfo, &parameters, sizeof(parameters));
}

static inline int32_t Net_Fcntl(int32_t fd, int32_t cmd, va_list args)
{
    struct Net_FcntlParameters parameters = {
        .fd = fd,
        .cmd = cmd,
        .args = args
    };

    return Call(SecureService_Net, Net_Apis_Fcntl, &parameters, sizeof(parameters));
}

#ifdef __cplusplus
#include <utility>

namespace NimbeLink::Sdk::SecureServices::Net
{
    struct _Apis
    {
        enum _E
        {
            Socket          = Net_Apis_Socket,
            Close           = Net_Apis_Close,
            Accept          = Net_Apis_Accept,
            Bind            = Net_Apis_Bind,
            Listen          = Net_Apis_Listen,
            Connect         = Net_Apis_Connect,
            Poll            = Net_Apis_Poll,
            SetSockOpt      = Net_Apis_SetSockOpt,
            GetSockOpt      = Net_Apis_GetSockOpt,
            Recv            = Net_Apis_Recv,
            RecvFrom        = Net_Apis_RecvFrom,
            Send            = Net_Apis_Send,
            SendTo          = Net_Apis_SendTo,
            GetAddrInfo     = Net_Apis_GetAddrInfo,
            FreeAddrInfo    = Net_Apis_FreeAddrInfo,
            Fcntl           = Net_Apis_Fcntl,
        };
    };

    using Apis = _Apis::_E;

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
