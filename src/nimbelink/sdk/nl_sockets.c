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
#include <stdbool.h>
#include <stdlib.h>
#include <errno.h>

#include <device.h>
#include <init.h>
#include <net/socket.h>
#include <net/socket_offload.h>
#include <zephyr.h>

#include "nimbelink/sdk/secure_services/net.h"

static int nl_socket_socket(int family, int type, int proto)
{
    return Net_Socket(
        family,
        type,
        proto
    );
}

static int nl_socket_close(int fd)
{
    return Net_Close(
        fd
    );
}

static int nl_socket_accept(int fd, struct sockaddr *addr, socklen_t *addrlen)
{
    return Net_Accept(
        fd,
        addr,
        addrlen
    );
}

static int nl_socket_bind(int fd, const struct sockaddr *addr, socklen_t addrlen)
{
    return Net_Bind(
        fd,
        addr,
        addrlen
    );
}

static int nl_socket_listen(int fd, int backlog)
{
    return Net_Listen(
        fd,
        backlog
    );
}

static int nl_socket_connect(int fd, const struct sockaddr *addr, socklen_t addrlen)
{
    return Net_Connect(
        fd,
        addr,
        addrlen
    );
}

static inline int nl_socket_poll(struct pollfd *fds, int nfds, int timeout)
{
    return Net_Poll(
        fds,
        nfds,
        timeout
    );
}

static int nl_socket_setsockopt(int fd, int level, int optname, const void *optval, socklen_t optlen)
{
    return Net_SetSockOpt(
        fd,
        level,
        optname,
        optval,
        optlen
    );
}

static int nl_socket_getsockopt(int fd, int level, int optname, void *optval, socklen_t *optlen)
{
    return Net_GetSockOpt(
        fd,
        level,
        optname,
        optval,
        optlen
    );
}

static ssize_t nl_socket_recv(int fd, void *buf, size_t max_len, int flags)
{
    return Net_Recv(
        fd,
        buf,
        max_len,
        flags
    );
}

static ssize_t nl_socket_recvfrom(int fd, void *buf, short int len, short int flags, struct sockaddr *from, socklen_t *fromlen)
{
    return Net_RecvFrom(
        fd,
        buf,
        len,
        flags,
        from,
        fromlen
    );
}

static ssize_t nl_socket_send(int fd, const void *buf, size_t len, int flags)
{
    return Net_Send(
        fd,
        buf,
        len,
        flags
    );
}

static ssize_t nl_socket_sendto(int fd, const void *buf, size_t len, int flags, const struct sockaddr *to, socklen_t tolen)
{
    return Net_SendTo(
        fd,
        buf,
        len,
        flags,
        to,
        tolen
    );
}

static void nl_socket_freeaddrinfo(struct addrinfo *root)
{
    // If they didn't provide a valid pointer, ignore this
    if (root == NULL)
    {
        return;
    }

    while (true)
    {
        // Get the next info, if any
        struct addrinfo *next = root->ai_next;

        // Free the current structure
        if (root->ai_addr != NULL)
        {
            free(root->ai_addr);
        }

        if (root->ai_canonname != NULL)
        {
            free(root->ai_canonname);
        }

        free(root);

        // If we're out of infos now, move on
        if (next == NULL)
        {
            break;
        }

        // Note the next info and free it when we come back around
        root = next;
    }
}

static int nl_socket_getaddrinfo(const char *node, const char *service, const struct addrinfo *hints, struct addrinfo **res)
{
    // We'll support up to 3 info structures
    struct addrinfo *infos[3] = {NULL, };

    // Innocent until proven guilty
    bool allAllocated = true;

    // We cannot read Secure RAM, so we must manually allocate and copy
    // addrinfo structures as part of the Secure Service
    //
    // To keep the socket APIs proper, we will still require a pointer to a
    // pointer, but we'll allocate the structure and provide that to the Secure
    // Service API call, and then -- if successful -- store that in the
    // provided double pointer.
    //
    // We'll also use calloc() instead of malloc() to make sure the various
    // pointers are explicitly initialized to NULL.
    for (uint32_t i = 0; i < (sizeof(infos)/sizeof(infos[0])); i++)
    {
        infos[i] = calloc(1, sizeof(struct addrinfo));

        if (infos[i] == NULL)
        {
            allAllocated = false;
            break;
        }

        infos[i]->ai_addr = calloc(1, sizeof(struct sockaddr));
        infos[i]->ai_canonname = calloc(1, NET_AI_CANONNAME_MAX_LENGTH + 1);

        if ((infos[i]->ai_addr == NULL) || (infos[i]->ai_canonname == NULL))
        {
            allAllocated = false;
            break;
        }
    }

    // If any of those failed, abort
    if (!allAllocated)
    {
        nl_socket_freeaddrinfo(infos[0]);

        return -ENOMEM;
    }

    // Make the offloaded API call
    int result = Net_GetAddrInfo(
        node,
        service,
        hints,
        (sizeof(infos)/sizeof(infos[0])),
        infos
    );

    // Assume we won't have to free anything
    int32_t freeFrom = -1;

    // If that failed or somehow wasn't filled in, make sure we free all of our
    // allocated structures
    if ((result != 0) || (infos[0]->ai_addr == NULL))
    {
        freeFrom = 0;

        *res = NULL;
    }
    else
    {
        // We didn't necessarily use all of our info structures, so go back
        // through and find the last entry and free everything after it
        for (uint32_t i = 1; i < (sizeof(infos)/sizeof(infos[0])); i++)
        {
            // If this structure has a linked next one, keep looking
            if (infos[i - 1]->ai_next != NULL)
            {
                continue;
            }

            // This current structure isn't linked to by the previous one, so
            // we'll free this and everything after
            freeFrom = i;

            break;
        }

        *res = infos[0];
    }

    // We won't have necessarily linked the structs together, so if we've got
    // stuff to free, link together the unused structures and let our free-er
    // iterate through and free them
    if (freeFrom >= 0)
    {
        for (uint32_t i = freeFrom + 1; i < (sizeof(infos)/sizeof(infos[0])); i++)
        {
            infos[i - 1]->ai_next = infos[i];
        }

        nl_socket_freeaddrinfo(infos[freeFrom]);
    }

    return result;
}

static int nl_socket_fcntl(int fd, int cmd, va_list args)
{
    return Net_Fcntl(
        fd,
        cmd,
        args
    );
}

static const struct socket_offload nl_socket_ops = {
    .socket = nl_socket_socket,
    .close = nl_socket_close,
    .accept = nl_socket_accept,
    .bind = nl_socket_bind,
    .listen = nl_socket_listen,
    .connect = nl_socket_connect,
    .poll = nl_socket_poll,
    .setsockopt = nl_socket_setsockopt,
    .getsockopt = nl_socket_getsockopt,
    .recv = nl_socket_recv,
    .recvfrom = nl_socket_recvfrom,
    .send = nl_socket_send,
    .sendto = nl_socket_sendto,
    .getaddrinfo = nl_socket_getaddrinfo,
    .freeaddrinfo = nl_socket_freeaddrinfo,
    .fcntl = nl_socket_fcntl,
};

static int nl_socket_init(struct device *arg)
{
    (void)arg;

    return 0;
}

static struct nl_socket_iface_data {
    struct net_if *iface;
} nl_socket_iface_data;

static void nl_socket_iface_init(struct net_if *iface)
{
    nl_socket_iface_data.iface = iface;

    iface->if_dev->offloaded = true;

    socket_offload_register(&nl_socket_ops);
}

static struct net_if_api nl_if_api = {
    .init = nl_socket_iface_init,
};

NET_DEVICE_OFFLOAD_INIT(
    nl_socket,
    "nl_socket",
    nl_socket_init,
    &nl_socket_iface_data,
    NULL,
    0,
    &nl_if_api,
    1280
);
