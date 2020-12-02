###
 # \file
 #
 # \brief Runs commands available in our package
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import sys

from dualie import Dualie

from commands.app import AppCommand
from commands.format import FormatCommand
from commands.update import UpdateCommand

# Make a configuration for our 'skywire' command
anonymousConfig = Dualie.AnonymousConfig(
    name = "skywire",
    isRaw = None,
    description = "provides Skywire commands",
    subCommands = [
        AppCommand(),
        FormatCommand(),
        UpdateCommand(),
    ]
)

# If we're being run from a standard Python context, manually run our command
#
# Otherwise, 'west' (which would be the thing likely running us in that case)
# will do everything for us.
if __name__ == "__main__":
    anonymousConfig.isRaw = True

    SkywireCommand = Dualie.makeInstantiable(anonymousConfig = anonymousConfig)

    SkywireCommand().runRaw(args = sys.argv[1:])

# Else, we're being run from 'west', so set up the dualie command
else:
    anonymousConfig.isRaw = False

    SkywireCommand = Dualie.makeInstantiable(anonymousConfig = anonymousConfig)
