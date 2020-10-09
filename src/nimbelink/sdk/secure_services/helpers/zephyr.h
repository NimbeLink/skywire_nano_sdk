/**
 * \file
 *
 * \brief Secure service helpers for a Zephyr-based application
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

#include <zephyr.h>

/**
 * \brief Handles a secure service request
 *
 * \param service
 *      The service to access
 * \param api
 *      The service's unique API to invoke
 * \param *parameters
 *      A pointer to a structure with arguments for the request
 * \param size
 *      The size of the parameter structure
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t Call(uint16_t service, uint16_t api, void *parameters, uint32_t size)
{
    // The Secure and Non-Secure worlds each have their own set of stack
    // pointers, and the ARM core will -- at a hardware level -- swap usage of
    // each when switching from Secure to Non-Secure and vice versa. Thus, once
    // we've made our way into the __Call() function as it's implemented in
    // Secure firmware, 'our' stack pointer -- that is, the stack pointer for
    // our execution -- will no longer be the stack pointer our kernel adjusts
    // when doing context switches.
    //
    // This on its own wouldn't necessarily be a bad thing if our kernel
    // was able to suspend the execution of the Secure function call and
    // switch to a different Non-Secure execution -- that is, perform a
    // context switch to a different thread. However, the Non-Secure world
    // does not have this ability. Thus, if the kernel were to attempt a
    // context switch while the current execution context was in the middle
    // of Secure execution -- that is, was in the middle of calling
    // __Call() -- the kernel would successfully swap out the current
    // thread's RAM state and -- critically -- stack pointers, but the
    // execution context would still revert back to the Secure execution.
    // Eventually, that execution would complete and attempt to pop down
    // its call stack to where this invocation occurred. But, since the
    // kernel swapped out the context, the call stack would be messed up.
    // Either execution would keep going until some state was corrupted
    // enough to cause a crash, or the FType handling of the core's
    // registers would not pass an integrity check -- which the core does
    // as a part of its Secure<->Non-Secure transition handling -- and the
    // core would throw an exception.
    //
    // So, to avoid all of this, we will specifically prevent the kernel
    // from trying to swap out the current thread while we're in the middle
    // of a Secure __Call() invocation.
    //
    // The kernel doesn't like calling this API when in an interrupt
    // context, and since we aren't going to pre-empt an ISR with the
    // PendSV context switching anyway (since it uses the lowest-possible
    // interrupt priority), we don't need to run these operations when
    // calling __Call() from an ISR.
    if (!k_is_in_isr())
    {
        k_sched_lock();
    }

    int32_t result = __Call(CREATE_REQUEST(service, api), parameters, size);

    if (!k_is_in_isr())
    {
        k_sched_unlock();
    }

    return result;
}

#ifdef __cplusplus
namespace NimbeLink::Sdk::SecureServices
{
    static inline int32_t Call(uint16_t service, uint16_t api, void *parameters = nullptr, uint32_t size = 0)
    {
        return ::Call(service, api, parameters, size);
    }

    /**
     * \brief Handles a secure service request
     *
     * \param service
     *      The service to access
     * \param api
     *      The service's unqiue API to invoke
     * \param &parameters
     *      A structure with arguments for the request
     *
     * \return int32_t
     *      The result of the request
     */
    template <typename T>
    static inline int32_t Call(uint16_t service, uint16_t api, T &parameters)
    {
        return ::Call(service, api, &parameters, sizeof(T));
    }
}
#endif
