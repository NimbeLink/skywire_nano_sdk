/**
 * \file
 *
 * \brief CME error codes
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

#define FOREACH_CME_PAIR(op)                                        \
    op(PHONE_FAILURE,                                       0)      \
    op(NO_CONNECTION_TO_PHONE,                              1)      \
    op(PHONE_ADAPTER_LINK_RESERVED,                         2)      \
    op(OPERATION_NOT_ALLOWED,                               3)      \
    op(OPERATION_NOT_SUPPORTED,                             4)      \
    op(PH_SIM_PIN_REQUIRED,                                 5)      \
    op(PH_FSIM_PIN_REQUIRED,                                6)      \
    op(PH_FSIM_PUK_REQUIRED,                                7)      \
    op(SIM_NOT_INSERTED,                                    10)     \
    op(SIM_PIN_REQUIRED,                                    11)     \
    op(SIM_PUK_REQUIRED,                                    12)     \
    op(SIM_FAILURE,                                         13)     \
    op(SIM_BUSY,                                            14)     \
    op(SIM_WRONG,                                           15)     \
    op(INCORRECT_PASSWORD,                                  16)     \
    op(SIM_PIN2_REQUIRED,                                   17)     \
    op(SIM_PUK2_REQUIRED,                                   18)     \
    op(MEMORY_FULL,                                         20)     \
    op(INVALID_INDEX,                                       21)     \
    op(NOT_FOUND,                                           22)     \
    op(MEMORY_FAILURE,                                      23)     \
    op(TEXT_STRING_TOO_LONG,                                24)     \
    op(INVALID_CHARACTERS_IN_TEXT_STRING,                   25)     \
    op(DIAL_STRING_TOO_LONG,                                26)     \
    op(INVALID_CHARACTERS_IN_DIAL_STRING,                   27)     \
    op(NO_NETWORK_SERVICE,                                  30)     \
    op(NETWORK_TIMEOUT,                                     31)     \
    op(NETWORK_NOT_ALLOWED_EMERGENCY_CALLS_ONLY,            32)     \
    op(NETWORK_PERSONALIZATION_PIN_REQUIRED,                40)     \
    op(NETWORK_PERSONALIZATION_PUK_REQUIRED,                41)     \
    op(NETWORK_SUBSET_PERSONALIZATION_PIN_REQUIRED,         42)     \
    op(NETWORK_SUBSET_PERSONALIZATION_PUK_REQUIRED,         43)     \
    op(SERVICE_PROVIDER_PERSONALIZATION_PIN_REQUIRED,       44)     \
    op(SERVICE_PROVIDER_PERSONALIZATION_PUK_REQUIRED,       45)     \
    op(CORPORATE_PERSONALIZATION_PIN_REQUIRED,              46)     \
    op(CORPORATE_PERSONALIZATION_PUK_REQUIRED,              47)     \
    op(PH_SIM_PUK_REQUIRED,                                 48)     \
    op(INCORRECT_PARAMETERS,                                50)     \
    op(UNKNOWN_ERROR,                                       100)    \
    op(ILLEGAL_MS,                                          103)    \
    op(ILLEGAL_ME,                                          106)    \
    op(GPRS_SERVICES_NOT_ALLOWED,                           107)    \
    op(PLMN_NOT_ALLOWED,                                    111)    \
    op(LOCATION_AREA_NOT_ALLOWED,                           112)    \
    op(ROAMING_NOT_ALLOWED_IN_THIS_LOCATION_AREA,           113)    \
    op(OPERATION_TEMPORARY_NOT_ALLOWED,                     126)    \
    op(SERVICE_OPERATION_NOT_SUPPORTED,                     132)    \
    op(REQUESTED_SERVICE_OPTION_NOT_SUBSCRIBED,             133)    \
    op(SERVICE_OPTION_TEMPORARY_OUT_OF_ORDER,               134)    \
    op(UNSPECIFIED_GPRS_ERROR,                              148)    \
    op(PDP_AUTHENTICATION_FAILURE,                          149)    \
    op(INVALID_MOBILE_CLASS,                                150)    \
    op(OPERATION_TEMPORARILY_NOT_ALLOWED,                   256)    \
    op(CALL_BARRED,                                         257)    \
    op(PHONE_IS_BUSY,                                       258)    \
    op(USER_ABORT,                                          259)    \
    op(INVALID_DIAL_STRING,                                 260)    \
    op(SS_NOT_EXECUTED,                                     261)    \
    op(SIM_BLOCKED,                                         262)    \
    op(INVALID_BLOCK,                                       263)    \
    op(SIM_POWERED_DOWN,                                    772)

/**
 * \brief The C global namespace will get "CME_<error>" enumerations
 */
#define GENERATE_C_CME_ENUM(name, value)    \
    CME_ ## name = value,

/**
 * \brief The C++ CmeError class will get "<error>" enumerations assigned to
 *        their corresponding C "CME_<error>" counterparts
 */
#define GENERATE_CPP_CME_ENUM(name, value)  \
    name = CME_ ## name,

#define GENERATE_CME_STRING(name, value)    \
    {                                       \
        name,                               \
        #name                               \
    },

enum CmeErrorType
{
    FOREACH_CME_PAIR(GENERATE_C_CME_ENUM)
};

#ifdef __cplusplus
#include <cstdbool>

namespace NimbeLink::Sdk::At
{
    class CmeError;
}

class NimbeLink::Sdk::At::CmeError
{
    public:
        enum Type
        {
            FOREACH_CME_PAIR(GENERATE_CPP_CME_ENUM)
        };

        struct StringMap
        {
            // The type this string maps to
            Type type;

            // The string representation of the type
            const char *string;
        };

        static constexpr const struct StringMap StringMaps[] = {
            FOREACH_CME_PAIR(GENERATE_CME_STRING)
        };

    private:
        // The type of error this is
        Type type;

    public:
        CmeError(void) = default;

        /**
         * \brief Creates a new CME error
         *
         * \param type
         *      The type of error this is
         *
         * \return none
         */
        constexpr CmeError(Type type):
            type(type) {}

        /**
         * \brief Gets the error
         *
         * \param none
         *
         * \return Type
         *      The error
         */
        inline operator Type() const
        {
            return this->type;
        }

        /**
         * \brief Checks if this is a particular error type
         *
         * \param type
         *      The error type to check
         *
         * \return true
         *      This is that error type
         * \return false
         *      This is a different error type
         */
        inline bool operator==(const Type type) const
        {
            return (this->type == type);
        }

        /**
         * \brief Checks if this is a particular error type
         *
         * \param type
         *      The error type to check
         *
         * \return true
         *      This is that error type
         * \return false
         *      This is a different error type
         */
        inline bool operator!=(const Type type) const
        {
            return (this->type != type);
        }
};
#endif
