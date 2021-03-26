###
 # \file
 #
 # \brief The base 'skywire' command
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

from commands.command import Command

class SkywireCommand(Command):
    """The base Skywire command
    """

    def __init__(self):
        """Creates a new Skywire command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "skywire",
            help = "provides Skywire commands",
            description = [
                "This provides sub-commands for working with the Skywire Nano."
            ],
            subCommands = [
                Command.SubCommand("commands.app",      "AppCommand"),
                Command.SubCommand("commands.format",   "FormatCommand"),
                Command.SubCommand("commands.update",   "UpdateCommand"),
            ]
        )

    def addArguments(self, parser):
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        # Add an always-available argument for being verbose
        parser.add_argument(
            "-v",
            "--verbose",
            dest = "verbose",
            action = "count",
            default = 0,
            required = False,
            help = "Use verbose output"
        )
