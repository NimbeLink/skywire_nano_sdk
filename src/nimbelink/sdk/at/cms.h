/**
 * \file
 *
 * \brief CMS error codes
 *
 * © NimbeLink Corp. 2020
 *
 * All rights reserved except as explicitly granted in the license agreement
 * between NimbeLink Corp. and the designated licensee.  No other use or
 * disclosure of this software is permitted. Portions of this software may be
 * subject to third party license terms as specified in this software, and such
 * portions are excluded from the preceding copyright notice of NimbeLink Corp.
 */
#pragma once

#define FOREACH_CMS_PAIR(op)                                        \
    op(UNASSIGNED_NUMBER,                                   1)      \
    op(OPERATOR_DETERMINED_BARRING,                         8)      \
    op(CALL_BARED,                                          10)     \
    op(SHORT_MESSAGE_TRANSFER_REJECTED,                     21)     \
    op(DESTINATION_OUT_OF_SERVICE,                          27)     \
    op(UNINDENTIFIED_SUBSCRIBER,                            28)     \
    op(FACILITY_REJECTED,                                   29)     \
    op(UNKNOWN_SUBSCRIBER,                                  30)     \
    op(NETWORK_OUT_OF_ORDER,                                38)     \
    op(TEMPORARY_FAILURE,                                   41)     \
    op(CONGESTION,                                          42)     \
    op(RECOURCES_UNAVAILABLE,                               47)     \
    op(REQUESTED_FACILITY_NOT_SUBSCRIBED,                   50)     \
    op(REQUESTED_FACILITY_NOT_IMPLEMENTED,                  69)     \
    op(INVALID_SHORT_MESSAGE_TRANSFER_REFERENCE_VALUE,      81)     \
    op(INVALID_MESSAGE_UNSPECIFIED,                         95)     \
    op(INVALID_MANDATORY_INFORMATION,                       96)     \
    op(MESSAGE_TYPE_NON_EXISTENT_OR_NOT_IMPLEMENTED,        97)     \
    op(MESSAGE_NOT_COMPATIBLE_WITH_SHORT_MESSAGE_PROTOCOL,  98)     \
    op(INFORMATION_ELEMENT_NON_EXISTENT_OR_NOT_IMPLEMENTE,  99)     \
    op(PROTOCOL_ERROR_UNSPECIFIED,                          111)    \
    op(INTERNETWORKING_UNSPECIFIED,                         127)    \
    op(TELEMATIC_INTERNETWORKING_NOT_SUPPORTED,             128)    \
    op(SHORT_MESSAGE_TYPE_0_NOT_SUPPORTED,                  129)    \
    op(CANNOT_REPLACE_SHORT_MESSAGE,                        130)    \
    op(UNSPECIFIED_TP_PID_ERROR,                            143)    \
    op(DATA_CODE_SCHEME_NOT_SUPPORTED,                      144)    \
    op(MESSAGE_CLASS_NOT_SUPPORTED,                         145)    \
    op(UNSPECIFIED_TP_DCS_ERROR,                            159)    \
    op(COMMAND_CANNOT_BE_ACTIONED,                          160)    \
    op(COMMAND_UNSUPPORTED,                                 161)    \
    op(UNSPECIFIED_TP_COMMAND_ERROR,                        175)    \
    op(TPDU_NOT_SUPPORTED,                                  176)    \
    op(SC_BUSY,                                             192)    \
    op(NO_SC_SUBSCRIPTION,                                  193)    \
    op(SC_SYSTEM_FAILURE,                                   194)    \
    op(INVALID_SME_ADDRESS,                                 195)    \
    op(DESTINATION_SME_BARRED,                              196)    \
    op(SM_REJECTED_DUPLICATE_SM,                            197)    \
    op(TP_VPF_NOT_SUPPORTED,                                198)    \
    op(TP_VP_NOT_SUPPORTED,                                 199)    \
    op(D0_SIM_SMS_STORAGE_FULL,                             208)    \
    op(NO_SMS_STORAGE_CAPABILITY_IN_SIM,                    209)    \
    op(ERROR_IN_MS,                                         210)    \
    op(MEMORY_CAPACITY_EXCEEDED,                            211)    \
    op(SIM_APPLICATION_TOOLKIT_BUSY,                        212)    \
    op(SIM_DATA_DOWNLOAD_ERROR,                             213)    \
    op(UNSPECIFIED_ERROR_CAUSE,                             255)    \
    op(ME_FAILURE,                                          300)    \
    op(SMS_SERVICE_OF_ME_RESERVED,                          301)    \
    op(OPERATION_NOT_ALLOWED,                               302)    \
    op(OPERATION_NOT_SUPPORTED,                             303)    \
    op(INVALID_PDU_MODE_PARAMETER,                          304)    \
    op(INVALID_TEXT_MODE_PARAMETER,                         305)    \
    op(SIM_NOT_INSERTED,                                    310)    \
    op(SIM_PIN_REQUIRED,                                    311)    \
    op(PH_SIM_PIN_REQUIRED,                                 312)    \
    op(SIM_FAILURE,                                         313)    \
    op(SIM_BUSY,                                            314)    \
    op(SIM_WRONG,                                           315)    \
    op(SIM_PUK_REQUIRED,                                    316)    \
    op(SIM_PIN2_REQUIRED,                                   317)    \
    op(SIM_PUK2_REQUIRED,                                   318)    \
    op(MEMORY_FAILURE,                                      320)    \
    op(INVALID_MEMORY_INDEX,                                321)    \
    op(MEMORY_FULL,                                         322)    \
    op(SMSC_ADDRESS_UNKNOWN,                                330)    \
    op(NO_NETWORK_SERVICE,                                  331)    \
    op(NETWORK_TIMEOUT,                                     332)    \
    op(NO_CNMA_EXPECTED,                                    340)    \
    op(UNKNOWN_ERROR,                                       500)    \
    op(USER_ABORT,                                          512)    \
    op(UNABLE_TO_STORE,                                     513)    \
    op(INVALID_STATUS,                                      514)    \
    op(DEVICE_BUSY_OR_INVALID_CHARACTER_IN_STRING,          515)    \
    op(INVALID_LENGTH,                                      516)    \
    op(INVALID_CHARACTER_IN_PDU,                            517)    \
    op(INVALID_PARAMETER,                                   518)    \
    op(INVALID_LENGTH_OR_CHARACTER,                         519)    \
    op(INVALID_CHARACTER_IN_TEXT,                           520)    \
    op(TIMER_EXPIRED,                                       521)    \
    op(OPERATION_TEMPORARY_NOT_ALLOWED,                     522)    \
    op(SIM_NOT_READY,                                       532)    \
    op(CELL_BROADCAST_ERROR_UNKNOWN,                        534)    \
    op(PROTOCOL_STACK_BUSY,                                 535)    \
    op(INVALID_PARAMETER2,                                  538)

/**
 * \brief The C global namespace will get "CMS_<error>" enumerations
 */
#define GENERATE_C_CMS_ENUM(name, value)    \
    CMS_ ## name = value,

/**
 * \brief The C++ CmsError class will get "<error>" enumerations assigned to
 *        their corresponding C "CMS_<error>" counterparts
 */
#define GENERATE_CPP_CMS_ENUM(name, value)  \
    name = CMS_ ## name,

#define GENERATE_CMS_STRING(name, value)    \
    {                                       \
        name,                               \
        #name                               \
    },

enum CmsErrorType
{
    FOREACH_CMS_PAIR(GENERATE_C_CMS_ENUM)
};

#ifdef __cplusplus
#include <cstdbool>

namespace NimbeLink::Sdk::At
{
    class CmsError;
}

class NimbeLink::Sdk::At::CmsError
{
    public:
        enum Type
        {
            FOREACH_CMS_PAIR(GENERATE_CPP_CMS_ENUM)
        };

        struct StringMap
        {
            // The type this string maps to
            Type type;

            // The string representation of the type
            const char *string;
        };

        static constexpr const struct StringMap StringMaps[] = {
            FOREACH_CMS_PAIR(GENERATE_CMS_STRING)
        };

    private:
        // The type of error this is
        Type type;

    public:
        CmsError(void) = default;

        /**
         * \brief Creates a new CMS error
         *
         * \param type
         *      The type of error this is
         *
         * \return none
         */
        constexpr CmsError(Type type):
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
