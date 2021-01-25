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

#include <bsd_limits.h>
#include <device.h>
#include <init.h>
#include <net/socket.h>
#include <net/socket_offload.h>
#include <sockets_internal.h>
#include <zephyr.h>

#include "nimbelink/sdk/secure_services/kernel.h"
#include "nimbelink/sdk/secure_services/net.h"

#define FD_TO_OBJ(fd)       ((void *)(fd + 1))
#define OBJ_TO_FD(context)  (((int)context) - 1)

/**
 * \brief Chicken, meet egg
 */
static const struct socket_op_vtable nl_socket_op_vtable;

static int nl_socket_socket(int family, int type, int proto)
{
    int result = Net_Socket(
        family,
        type,
        proto
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static int nl_socket_close(void *context)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_Close(
        fd
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static int nl_socket_accept(void *context, struct sockaddr *addr, socklen_t *addrlen)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_Accept(
        fd,
        addr,
        addrlen
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static int nl_socket_bind(void *context, const struct sockaddr *addr, socklen_t addrlen)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_Bind(
        fd,
        addr,
        addrlen
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static int nl_socket_listen(void *context, int backlog)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_Listen(
        fd,
        backlog
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static int nl_socket_connect(void *context, const struct sockaddr *addr, socklen_t addrlen)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_Connect(
        fd,
        addr,
        addrlen
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static inline int nl_socket_poll(struct pollfd *fds, int nfds, int timeout)
{
    struct pollfd _fds[BSD_MAX_SOCKET_COUNT] = { 0 };

    int changeCount = 0;

    for (int i = 0; i < nfds; i++)
    {
        _fds[i].events = 0;
        fds[i].revents = 0;

        // Per POSIX, negative file descriptors are just ignored, so if this is
        // negative, ignore it
        if (fds[i].fd < 0)
        {
            _fds[i].fd = fds[i].fd;
            continue;
        }

        void *context = z_get_fd_obj(
            fds[i].fd,
            (const struct fd_op_vtable *)&nl_socket_op_vtable,
            ENOTSUP
        );

        // If we found the object, great, note its translated file descriptor
        if (context != NULL)
        {
            _fds[i].fd = OBJ_TO_FD(context);
        }
        // Else, note that's an invalid file descriptor
        else
        {
            fds[i].revents = POLLNVAL;
            changeCount++;
        }

        if (fds[i].events & POLLIN)
        {
            _fds[i].events |= POLLIN;
        }

        if (fds[i].events & POLLOUT)
        {
            _fds[i].events |= POLLOUT;
        }
    }

    // If things changed above, that means not all of the file descriptors were
    // valid
    if (changeCount > 0)
    {
        return changeCount;
    }

    int result = Net_Poll(
        _fds,
        nfds,
        timeout
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    for (int i = 0; i < nfds; i++)
    {
        fds[i].revents = _fds[i].revents;
    }

    return result;
}

static int nl_socket_setsockopt(void *context, int level, int optname, const void *optval, socklen_t optlen)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_SetSockOpt(
        fd,
        level,
        optname,
        optval,
        optlen
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static int nl_socket_getsockopt(void *context, int level, int optname, void *optval, socklen_t *optlen)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_GetSockOpt(
        fd,
        level,
        optname,
        optval,
        optlen
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static ssize_t nl_socket_recvfrom(void *context, void *buf, unsigned int len, int flags, struct sockaddr *from, socklen_t *fromlen)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_RecvFrom(
        fd,
        buf,
        len,
        flags,
        from,
        fromlen
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static ssize_t nl_socket_read(void *context, void *buffer, size_t count)
{
    return nl_socket_recvfrom(context, buffer, count, 0, NULL, 0);
}

static ssize_t nl_socket_sendto(void *context, const void *buf, size_t len, int flags, const struct sockaddr *to, socklen_t tolen)
{
    int fd = OBJ_TO_FD(context);

    int result = Net_SendTo(
        fd,
        buf,
        len,
        flags,
        to,
        tolen
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static ssize_t nl_socket_write(void *context, const void *buffer, size_t count)
{
    return nl_socket_sendto(context, buffer, count, 0, NULL, 0);
}

static ssize_t nl_socket_sendmsg(void *context, const struct msghdr *msg, int flags)
{
    static K_MUTEX_DEFINE(lock);
    static uint8_t buffer[128];

    if (msg == NULL)
    {
        errno = EINVAL;

        return -1;
    }

    ssize_t length = 0;

    // Try to reduce number of `sendto` calls by copying data if they fit into a
    // single buffer
    for (int i = 0; i < msg->msg_iovlen; i++)
    {
        length += msg->msg_iov[i].iov_len;
    }

    if (length <= sizeof(buffer))
    {
        k_mutex_lock(&lock, K_FOREVER);

        length = 0;

        for (int i = 0; i < msg->msg_iovlen; i++)
        {
            memcpy(
                buffer + length,
                msg->msg_iov[i].iov_base,
                msg->msg_iov[i].iov_len
            );

            length += msg->msg_iov[i].iov_len;
        }

        int result = nl_socket_sendto(
            context,
            buffer,
            length,
            flags,
            msg->msg_name,
            msg->msg_namelen
        );

        k_mutex_unlock(&lock);

        return result;
    }

    length = 0;

    // The data won't fit into intermediate buffer, so send the buffers
    // separately
    for (int i = 0; i < msg->msg_iovlen; i++)
    {
        if (msg->msg_iov[i].iov_len == 0)
        {
            continue;
        }

        int result = nl_socket_sendto(
            context,
            msg->msg_iov[i].iov_base,
            msg->msg_iov[i].iov_len,
            flags,
            msg->msg_name,
            msg->msg_namelen
        );

        if (result < 0)
        {
            return result;
        }

        length += result;
    }

    return length;
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

        return DNS_EAI_MEMORY;
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
    int flags = va_arg(args, int);

    int result = Net_Fcntl(
        fd,
        cmd,
        flags
    );

    if (result < 0)
    {
        Kernel_Errno();
    }

    return result;
}

static int nl_socket_ioctl(void *context, unsigned int request, va_list args)
{
    int fd = OBJ_TO_FD(context);

    switch (request)
    {
        case ZFD_IOCTL_POLL_PREPARE:
            return -EXDEV;

        case ZFD_IOCTL_POLL_UPDATE:
            return -EOPNOTSUPP;

        case ZFD_IOCTL_POLL_OFFLOAD:
        {
            struct zsock_pollfd *fds = va_arg(args, struct zsock_pollfd *);
            int fdCount = va_arg(args, int);
            int timeout = va_arg(args, int);

            return nl_socket_poll(fds, fdCount, timeout);
        }

        // In Zephyr, fcntl() is apparently just an alias of ioctl()
        default:
            return nl_socket_fcntl(fd, request, args);
    }
}

static const struct socket_op_vtable nl_socket_op_vtable = {
    .fd_vtable = {
        .read = nl_socket_read,
        .write = nl_socket_write,
        .close = nl_socket_close,
        .ioctl = nl_socket_ioctl,
    },
    .bind = nl_socket_bind,
    .connect = nl_socket_connect,
    .listen = nl_socket_listen,
    .accept = nl_socket_accept,
    .sendto = nl_socket_sendto,
    .sendmsg = nl_socket_sendmsg,
    .recvfrom = nl_socket_recvfrom,
    .getsockopt = nl_socket_getsockopt,
    .setsockopt = nl_socket_setsockopt,
};

static bool nl_socket_is_supported(int family, int type, int proto)
{
    if (IS_ENABLED(CONFIG_NET_SOCKETS_OFFLOAD_TLS))
    {
        return true;
    }

    if (((proto >= IPPROTO_TLS_1_0) && (proto <= IPPROTO_TLS_1_2)) ||
        ((proto >= IPPROTO_DTLS_1_0) && (proto <= IPPROTO_DTLS_1_2)))
    {
        return false;
    }

    return true;
}

static int nl_socket_create(int family, int type, int proto)
{
    int fd = z_reserve_fd();

    if (fd < 0)
    {
        return -1;
    }

    int sd = nl_socket_socket(family, type, proto);

    if (sd < 0)
    {
        z_free_fd(fd);

        return -1;
    }

    z_finalize_fd(fd, FD_TO_OBJ(sd), (const struct fd_op_vtable *)&nl_socket_op_vtable);

    return fd;
}

NET_SOCKET_REGISTER(
    nl_socket,
    AF_UNSPEC,
    nl_socket_is_supported,
    nl_socket_create
);

static int nl_socket_init(const struct device *arg)
{
    (void)arg;

    return 0;
}

static const struct socket_dns_offload nl_socket_dns_ops = {
    .getaddrinfo = nl_socket_getaddrinfo,
    .freeaddrinfo = nl_socket_freeaddrinfo
};

static struct nl_socket_iface_data {
    struct net_if *iface;
} nl_socket_iface_data;

static void nl_socket_iface_init(struct net_if *iface)
{
    nl_socket_iface_data.iface = iface;

    iface->if_dev->offloaded = true;

    socket_offload_dns_register(&nl_socket_dns_ops);
}

static struct net_if_api nl_if_api = {
    .init = nl_socket_iface_init,
};

NET_DEVICE_OFFLOAD_INIT(
    nl_socket,
    "nl_socket",
    nl_socket_init,
    device_pm_control_nop,
    &nl_socket_iface_data,
    NULL,
    0,
    &nl_if_api,
    1280
);
