###
 # \file
 #
 # \brief Provides a command runnable from 'west' or basic Python
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
import os

from west.commands import WestCommand

class Dualie(WestCommand):
    """A command that can be run under 'west' or basic Python
    """

    class AnonymousConfig:
        """A configuration for an anonymous class
        """

        def __init__(self, name, isRaw, description, subCommands):
            """Creates a new anonymous config

            :param self:
                Self
            :param name:
                The name of the instantiated dualie command
            :param isRaw:
                Whether or not we're running in a 'raw' Python context
            :param description:
                Info about this dualie command
            :param subCommands:
                Our available sub-commands

            :return none:
            """

            self.name = name
            self.isRaw = isRaw
            self.description = description
            self.subCommands = subCommands

    @staticmethod
    def makeInstantiable(anonymousConfig):
        """Makes an anonymously-instantiable dualie command

        :param anonymousConfig:
            The anonymous configuration

        :return cls:
            A new class
        """

        class Anonymous(Dualie):
            config = anonymousConfig

        return Anonymous

    def __init__(self, *args, **kwargs):
        """Creates a new dualie command

        :param self:
            Self
        :param *args:
            Arguments for the west command
        :param **kwargs:
            Keyword arguments for the west command

        :return none:
        """

        # Note our parent's configuration
        self._config = self.__class__.config

        # If this isn't 'raw' -- that is, it's probably through 'west' -- then
        # initialize our parent class
        if not self._config.isRaw:
            super().__init__(
                self._config.name,
                *args,
                **kwargs,
                help = self._config.description,
                description = self._config.description
            )

    def do_add_parser(self, parserAdder):
        """Adds a parser

        :param self:
            Self
        :param parserAdder:
            The parser to add to

        :return parser:
            The new parser
        """

        if not self._config.isRaw:
            parser = parserAdder.add_parser(
                self._config.name,
                help = self._config.description,
                description = self._config.description
            )
        else:
            parser = parserAdder

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

        # Make a sub-parser for the commands we find
        subParser = parser.add_subparsers(
            title = "commands",
            dest = "command",
            required = True
        )

        # For each command we found, add its arguments to our sub-parser
        for command in self._config.subCommands:
            command._addArguments(parserAdder = subParser)

        return parser

    def do_run(self, args, unknownArgs):
        """Runs the command

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return none:
        """

        for command in self._config.subCommands:
            if command._name == args.command:
                command._runCommand(args = args, unknownArgs = unknownArgs)
                break

    def runRaw(self, args):
        """Runs a command invocation

        :param self:
            Self
        :param args:
            Arguments to parse

        :return none
        """

        # Make a parser
        parser = argparse.ArgumentParser(
            description = self._config.description
        )

        # Add our parameters and whatnot
        self.do_add_parser(parserAdder = parser)

        # Parse the arguments
        args = parser.parse_args(args = args)

        # Call the appropriate command with the parsed arguments
        self.do_run(args = args, unknownArgs = [])
