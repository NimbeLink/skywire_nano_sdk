/**
 * \file
 *
 * \brief Extended CME error codes for application-specific usage
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

#define FOREACH_EXTENDED_CME_PAIR(op)                           \
    op(MODEM_COMMUNICATION,                             612)    \
    op(GSMA_BACKOFF,                                    613)

/**
 * \brief The C global namespace will get "EXT_CME_<error>" enumerations
 */
#define GENERATE_C_EXTENDED_CME_ENUM(name, value)       \
    EXT_CME_ ## name = value,

/**
 * \brief The C++ ExtendedCmeError class will get "<error>" enumerations
 *        assigned to their corresponding C "EXT_CME_<error>" counterparts
 */
#define GENERATE_CPP_EXTENDED_CME_ENUM(name, value)     \
    name = EXT_CME_ ## name,

#define GENERATE_EXTENDED_CME_STRING(name, value)       \
    {                                                   \
        name,                                           \
        #name                                           \
    },

enum ExtendedCmeErrorType
{
    FOREACH_EXTENDED_CME_PAIR(GENERATE_C_EXTENDED_CME_ENUM)
};

#ifdef __cplusplus
#include <cstdbool>

namespace NimbeLink::Sdk::Cell::At
{
    class ExtendedCmeError;
}

class NimbeLink::Sdk::Cell::At::ExtendedCmeError
{
    public:
        enum Type
        {
            FOREACH_EXTENDED_CME_PAIR(GENERATE_CPP_EXTENDED_CME_ENUM)
        };

        struct StringMap
        {
            // The type this string maps to
            Type type;

            // The string representation of the type
            const char *string;
        };

        static constexpr const struct StringMap StringMaps[] = {
            FOREACH_EXTENDED_CME_PAIR(GENERATE_EXTENDED_CME_STRING)
        };

    private:
        // The type of error this is
        Type type;

    public:
        ExtendedCmeError(void) = default;

        /**
         * \brief Creates a new extended CME error
         *
         * \param type
         *      The type of error this is
         *
         * \return none
         */
        constexpr ExtendedCmeError(Type type):
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
