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

import argparse
import sys

from commands.app import SkywireAppCommand
from commands.dfu import SkywireDfuCommand
from commands.flash import SkywireFlashCommand
from commands.update import SkywireUpdateCommand

class Command:
    @staticmethod
    def run(args):
        """Runs a command invocation

        :param args:
            Arguments to parse

        :return none
        """

        # Make a parser and a sub-parser for our commands
        parser = argparse.ArgumentParser()

        subParser = parser.add_subparsers(
            title = "commands",
            dest = "command",
            required = True
        )

        # Make a command for each of the ones we provide
        commands = [
            SkywireAppCommand(prefix = False),
            SkywireDfuCommand(prefix = False),
            SkywireFlashCommand(prefix = False),
            SkywireUpdateCommand(prefix = False),
        ]

        for command in commands:
            # Add this command's arguments to a new sub-parser
            command.do_add_parser(parserAdder = subParser)

        # Parse the arguments
        args = parser.parse_args(args = args)

        # Call the appropriate command with the parsed arguments
        for command in commands:
            if command.name != args.command:
                continue

            command.do_run(args = args, unknownArgs = [])

            break

if __name__ == "__main__":
    Command.run(sys.argv[1:])
