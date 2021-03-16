/**
 * \file
 *
 * \brief A collection of secure 'services' available for use in Non-Secure
 *        firmware
 *
 * (C) NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <device.h>
#include <init.h>
#include <zephyr.h>

#include "nimbelink/sdk/secure_services/async.h"
#include "nimbelink/sdk/secure_services/at.h"
#include "nimbelink/sdk/secure_services/call.h"
#include "nimbelink/sdk/secure_services/kernel.h"

// Semaphores for signalling incoming secure service responses, one for each
// potential EGU trigger and one for our asynchronous channel
static struct k_sem semaphores[SECURE_SERVICE_CHANNEL_COUNT + 1];

// A bitfield for managing channels
static uint16_t channels = 0;

// Make sure the bitfield is big enough for all of our bidirectional channels
BUILD_ASSERT((sizeof(channels) * CHAR_BIT) >= SECURE_SERVICE_CHANNEL_COUNT);

// Make sure the asynchronous channel can be tacked onto the end of the
// bidirectional ones
BUILD_ASSERT(SECURE_SERVICE_ASYNC_CHANNEL == SECURE_SERVICE_CHANNEL_COUNT);

/**
 * \brief Requests pending the Non-Secure PendSV interrupt
 *
 * \param none
 *
 * \return none
 */
void arch_set_pendsv(void)
{
    // Lock interrupts to try and keep our Secure-world thread -- which is
    // running the Non-Secure kernel -- fully in Non-Secure world while being
    // swapping in and out
    uint32_t key = irq_lock();

    // Request kernel work
    __PutSecureServiceRequest(CREATE_REQUEST(0, SecureService_Kernel, Kernel_Api_PendSv), NULL, 0);

    // Unlock interrupts again
    //
    // After this point, we should expect either our PendSV flag to be pended
    // for us, or the Secure world's process of pending PendSV for us to be
    // primed and ready to take over as soon as we would re-enter Thread mode
    // (in the ARM core's eyes).
    irq_unlock(key);
}

/**
 * \brief Wraps calling the Non-Secure Callable API with scheduler locking
 *
 *  The Secure and Non-Secure worlds each have their own set of stack pointers,
 *  and the ARM core will -- at a hardware level -- swap usage of each when
 *  switching from Secure to Non-Secure and vice versa. Thus, once we've made
 *  our way into the Non-Secure Callable functions as they're implemented in
 *  Secure firmware, 'our' stack pointer -- that is, the stack pointer for our
 *  execution -- will no longer be the stack pointer our kernel adjusts when
 *  doing context switches.
 *
 *  This on its own wouldn't necessarily be a bad thing if our kernel was able
 *  to suspend the execution of the Secure function call and switch to a
 *  different Non-Secure execution -- that is, perform a context switch to a
 *  different thread. However, the Non-Secure world does not have this ability.
 *  Thus, if our kernel were to attempt a context switch while the current
 *  execution context was in the middle of Secure execution -- that is, was in
 *  the middle of calling a Non-Secure Callable function -- the kernel would
 *  successfully swap out the current thread's RAM state and -- critically --
 *  stack pointers, but the execution context would still revert back to the
 *  Secure execution. Eventually, that execution would complete and attempt to
 *  pop down its call stack to where this invocation occurred. But, since the
 *  kernel swapped out the context, the call stack would be messed up. Either
 *  execution would keep going until some state was corrupted enough to cause a
 *  crash, or the FType handling of the core's registers would not pass an
 *  integrity check -- which the core does as a part of its Secure<->Non-Secure
 *  transition handling -- and the core would throw an exception.
 *
 *  So, to avoid all of this, we will specifically prevent the Non-Secure
 *  kernel from trying to swap out the current thread while we're in the middle
 *  of a Non-Secure Callable invocation.
 *
 *  The kernel doesn't like calling this API when in an interrupt context, and
 *  since we aren't going to pre-empt an ISR with the PendSV context switching
 *  anyway (since it uses the lowest-possible interrupt priority), we don't
 *  need to run these operations when calling Non-Secure Callable functions
 *  from an ISR.
 *
 * \param request
 *      The request
 * \param *parameters
 *      Parameters for the request
 * \param size
 *      The size of the parameters
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t PutSecureServiceRequest(uint32_t request, void *parameters, uint32_t size)
{
    bool locked;

    if (!k_is_in_isr())
    {
        locked = true;
        k_sched_lock();
    }
    else
    {
        locked = false;
    }

    int32_t result = __PutSecureServiceRequest(request, parameters, size);

    if (locked)
    {
        k_sched_unlock();
    }

    return result;
}

/**
 * \brief Wraps calling the Non-Secure Callable API with scheduler locking
 *
 * \param request
 *      The request
 * \param *parameters
 *      Parameters for the request
 * \param size
 *      The size of the parameters
 *
 * \return int32_t
 *      The result of the request
 */
static inline int32_t GetSecureServiceResponse(uint32_t request, void *parameters, uint32_t size)
{
    bool locked;

    if (!k_is_in_isr())
    {
        locked = true;
        k_sched_lock();
    }
    else
    {
        locked = false;
    }

    int32_t result = __GetSecureServiceResponse(request, parameters, size);

    if (locked)
    {
        k_sched_unlock();
    }

    return result;
}

/**
 * \brief Gets an EGU 'task' from an index
 *
 * \param i
 *      The task to get
 *
 * \return nrf_egu_task_t
 *      The EGU 'task'
 */
static inline nrf_egu_task_t GetEguTask(size_t i)
{
    return (nrf_egu_task_t)offsetof(NRF_EGU_Type, TASKS_TRIGGER[i]);
}

/**
 * \brief Gets an EGU 'event' from an index
 *
 * \param i
 *      The event to get
 *
 * \return nrf_egu_event_t
 *      The EGU 'event'
 */
static inline nrf_egu_event_t GetEguEvent(size_t i)
{
    return (nrf_egu_event_t)offsetof(NRF_EGU_Type, EVENTS_TRIGGERED[i]);
}

/**
 * \brief Gets an EGU 'interrupt' from an index
 *
 * \param i
 *      The interrupt to get
 *
 * \return nrf_egu_int_mask_t
 *      The EGU 'interrupt'
 */
static inline nrf_egu_int_mask_t GetEguInterrupt(size_t i)
{
    return (nrf_egu_int_mask_t)(EGU_INTENSET_TRIGGERED0_Msk << i);
}

/**
 * \brief Handles an EGU channel's potential interrupt
 *
 * \param channel
 *      The channel to handle
 *
 * \return none
 */
static inline void HandleEguInterrupt(size_t channel)
{
    // If this channel hasn't had an interrupt, nothing to do
    if (!nrf_egu_event_check(NRF_EGU2, GetEguEvent(channel)))
    {
        return;
    }

    // Clear the event for the next time
    nrf_egu_event_clear(NRF_EGU2, GetEguEvent(channel));

    // Note there's an available response using our signalling semaphore
    k_sem_give(&(semaphores[channel]));
}

/**
 * \brief Handles the EGU interrupt
 *
 * \param *arg
 *      Unused
 *
 * \return none
 */
static void __attribute__((used)) EguInterrupt(void *arg)
{
    (void)arg;

    // Handle all of our bidirectional channels
    for (size_t i = 0; i < SECURE_SERVICE_CHANNEL_COUNT; i++)
    {
        HandleEguInterrupt(i);
    }

    // Also handle our asynchronous channel
    HandleEguInterrupt(SECURE_SERVICE_ASYNC_CHANNEL);
}

// A callback for incoming AT URCs
static At_UrcCallback urcCallback = NULL;

/**
 * \brief Monitors asynchronous secure service messages
 *
 * \param none
 *
 * \return none
 */
static void MonitorAsync(void)
{
    static struct Async_Parameters parameters;

    while (true)
    {
        // Avoid getting more messages than our semaphore can handle and loop
        // until we run out of messages
        while (true)
        {
            // Try to get the async message
            int32_t result = GetSecureServiceResponse(CREATE_REQUEST(SECURE_SERVICE_ASYNC_CHANNEL, 0, 0), &parameters, sizeof(parameters));

            // If that failed, we must be out of messages, so wait for more
            // notifications
            if (result != 0)
            {
                break;
            }

            // Figure out what to do
            switch ((enum Async_Event)parameters.event)
            {
                case Async_Event_AtUrc:
                {
                    // Atomically grab the callback
                    At_UrcCallback callback = urcCallback;

                    // If there is a valid callback, invoke it
                    if (callback != NULL)
                    {
                        callback((const char *)parameters.buffer);
                    }

                    break;
                }
            }
        }

        // Wait for something to come in
        //
        // No real harm in this call somehow failing, so ignore the result.
        //
        // Additionally, we want to specifically do a first-time pulling of any
        // pre-existing asynchronous messages, so we'll specifically do this
        // after our loop above. We could accomplish this with our semaphore
        // having a given resource at initialization, but this is hopefully
        // less likely to cause a communication issue between developers. It
        // also makes our initialization -- which initializes all of the other
        // semaphores to have zero resources at startup -- a little easier.
        k_sem_take(&(semaphores[SECURE_SERVICE_ASYNC_CHANNEL]), K_FOREVER);
    }
}

K_THREAD_DEFINE(
    secure_service_thread,
    1024,
    MonitorAsync,
    NULL,
    NULL,
    NULL,
    K_HIGHEST_APPLICATION_THREAD_PRIO,
    0,
    0
);

/**
 * \brief Reserves a secure service channel
 *
 * \param *channel
 *      Where to store the reserved channel
 *
 * \return false
 *      No channels available
 * \return true
 *      Channel reserved
 */
static bool ReserveChannel(uint8_t *channel)
{
    uint32_t key = irq_lock();

    // Guilty until proven innocent
    bool reserved = false;

    for (size_t i = 0; i < SECURE_SERVICE_CHANNEL_COUNT; i++)
    {
        // If this channel is free, grab it
        if ((channels & (1 << i)) == 0)
        {
            channels |= (1 << i);
            *channel = i;

            reserved = true;

            break;
        }
    }

    irq_unlock(key);

    return reserved;
}

/**
 * \brief Frees a secure service channel
 *
 * \param channel
 *      The channel to free
 *
 * \return none
 */
static void FreeChannel(uint8_t channel)
{
    uint32_t key = irq_lock();

    // If it's valid, clear this channel
    if (channel < SECURE_SERVICE_CHANNEL_COUNT)
    {
        channels &= ~(1 << channel);
    }

    irq_unlock(key);
}

/**
 * \brief Handles a secure service internally
 *
 * \param *result
 *      Where to put the result of the handling, if done internally
 * \param service
 *      The secure service
 * \param api
 *      The service's API
 * \param *parameters
 *      Parameters for the call
 * \param size
 *      The size of the parameters
 *
 * \return true
 *      Secure service handled internally
 * \return false
 *      Secure service not handled internally
 */
static bool HandleInternalService(int32_t *result, uint8_t service, uint16_t api, void *parameters, uint32_t size)
{
    // If this is subscribing to AT URCs, we'll handle that internally
    if ((service == SecureService_At) && (api == At_Api_SubscribeUrcs))
    {
        uint32_t key = irq_lock();

        // Assume this won't go well
        *result = -ENOMEM;

        // If the callback isn't set yet and the parameters look fine, allow
        // this
        if ((urcCallback == NULL) && (parameters != NULL) && (size == sizeof(struct At_SubscribeUrcsParameters)))
        {
            urcCallback = ((struct At_SubscribeUrcsParameters *)parameters)->callback;

            *result = 0;
        }

        irq_unlock(key);

        return true;
    }

    // Looks like this isn't something we handle internally
    return false;
}

/**
 * \brief Handles calling a secure service
 *
 * \param service
 *      The secure service
 * \param api
 *      The service's API
 * \param *parameters
 *      Parameters for the call
 * \param size
 *      The size of the parameters
 *
 * \return int32_t
 *      The result of the call
 */
int32_t CallSecureService(uint8_t service, uint16_t api, void *parameters, uint32_t size)
{
    int32_t result;

    if (HandleInternalService(&result, service, api, parameters, size))
    {
        return result;
    }

    // Grab a semaphore for dispatching our request
    uint8_t channel;

    // If that failed, we won't be able to manage our request
    if (!ReserveChannel(&channel))
    {
        return -ETIMEDOUT;
    }

    // Make sure we don't have a synchronization issue and we wait for a proper
    // signal
    k_sem_take(&(semaphores[channel]), K_NO_WAIT);

    // Try to queue our request
    result = PutSecureServiceRequest(CREATE_REQUEST(channel, service, api), parameters, size);

    // If our result was handled immediately, that's a success
    if (result == 1)
    {
        result = 0;
        goto Done;
    }

    // If that failed, that's going to be our result
    if (result != 0)
    {
        goto Done;
    }

    // Wait for a response
    result = k_sem_take(&(semaphores[channel]), K_FOREVER);

    // If we failed to get a response, we're done
    if (result != 0)
    {
        result = -ETIMEDOUT;
        goto Done;
    }

    // Get the response and use its result as our result
    result = GetSecureServiceResponse(CREATE_REQUEST(channel, service, api), parameters, size);

Done:
    FreeChannel(channel);

    return result;
}

/**
 * \brief Sets up an EGU channel
 *
 * \param channel
 *      The channel to set up
 *
 * \return none
 */
static inline void SetupEguChannel(size_t channel)
{
    // Initialize our signalling semaphore
    k_sem_init(&(semaphores[channel]), 0, 1);

    nrf_egu_subscribe_set(NRF_EGU2, GetEguTask(channel), channel);
    nrf_egu_publish_set(NRF_EGU2, GetEguEvent(channel), channel);
}

/**
 * \brief Sets up the secure service handling
 *
 * \param *device
 *      Unused
 *
 * \return 0
 *      Always
 */
static int SetupSecureServices(const struct device *device)
{
    (void)device;

    // Set the EGU up to do a basic interrupt operation when we get responses
    for (size_t i = 0; i < SECURE_SERVICE_CHANNEL_COUNT; i++)
    {
        SetupEguChannel(i);
    }

    // Also set up a channel for the asynchronous messages
    SetupEguChannel(SECURE_SERVICE_ASYNC_CHANNEL);

    nrf_egu_int_enable(NRF_EGU2, NRF_EGU_INT_ALL);

    // We expect to already have access to EGU2 before we're launched, so don't
    // bother requesting it
    IRQ_CONNECT(EGU2_IRQn, 6, EguInterrupt, NULL, 0);
    irq_enable(EGU2_IRQn);

    return 0;
}

// Run our secure service setup during system initialization, as early as
// possible (to beat any driver initializations that depend on access to the
// peripherals). We also need to beat our own peripheral access requesting (if
// included)
SYS_INIT(SetupSecureServices, PRE_KERNEL_1, 0);
