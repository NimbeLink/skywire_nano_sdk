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

try:
    from west.commands import WestCommand

except ImportError:
    class WestCommand:
        """A pretend west command when the tool isn't installed
        """

        def __init__(self, *args, **kwargs):
            """Pretends to create a west command

            :param self:
                Self
            :param *args:
                Arguments for the west command
            :param **kwargs:
                Keyword arguments for the west command

            :return none:
            """

            pass

class Dualie(WestCommand):
    """A command that can be run under 'west' or basic Python
    """

    class AnonymousConfig:
        """A configuration for an anonymous class
        """

        def __init__(self, command, isRaw = False):
            """Creates a new anonymous config

            :param self:
                Self
            :param command:
                The root command to wrap
            :param isRaw:
                Whether or not we're running in a 'raw' Python context

            :return none:
            """

            self.command = command
            self.isRaw = isRaw

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

    @classmethod
    def setRaw(cls, isRaw):
        """Sets if this class is a 'raw' Python command

        :param cls:
            Class
        :param isRaw:
            Whether or not we're running in a 'raw' Python context

        :return none:
        """

        cls.config.isRaw = isRaw

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

        # Instantiate our command
        self._config.command = self._config.command()

        # If this isn't 'raw' -- that is, it's probably through 'west' -- then
        # initialize our parent class as if we were the command we wrap
        if not self._config.isRaw:
            super().__init__(
                self._config.command._name,
                *args,
                **kwargs,
                help = self._config.command._help,
                description = self._config.command._description
            )

    def do_add_parser(self, parser):
        """Adds a parser

        :param self:
            Self
        :param parser:
            The parser to add to

        :return parser:
            The new parser
        """

        # If we are not given a parser, first make one of our own
        if parser == None:
            parser = argparse.ArgumentParser(
                description = self._config.command._description
            )

        # Else, add our command to the parser
        else:
            parser = self._config.command._createParser(parser = parser)

        # Add our command's arguments
        self._config.command._addArguments(parser = parser)

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

        # If we're being run 'raw', then we'll need to managing creating parsers
        # on owr own
        if self._config.isRaw:
            # Add our parameters and whatnot to a new parser
            parser = self.do_add_parser(parser = None)

            # Parse the arguments using the parser we made
            args = parser.parse_args(args = args)
            unknownArgs = []

        self._config.command._runCommand(args = args, unknownArgs = unknownArgs)
