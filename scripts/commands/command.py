###
 # \file
 #
 # \brief A base sub-command
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
import importlib
import inspect
import math
import os
import platform
import re
import subprocess
import textwrap

try:
    from west.configuration import config

except ImportError:
    class config:
        """A pretend west configuration
        """

        @staticmethod
        def get(*args, **kwargs):
            """Pretends to get a configuration

            :param *args:
                Arguments for the config get
            :param **kwargs
                Keyword arguments for the config get

            :return None:
                Always
            """

            return None

from tools.wsl import Wsl

class Command:
    """A west command for working with Skywire Nano devices, collected under
    the root 'skywire' command
    """

    ConfigPrefix = "skywire:nano"
    """A prefix we'll use for all of our Skywire Nano command configurations"""

    class SubCommand:
        """A sub-command for a base command
        """

        def __init__(self, moduleName, className):
            """Creates a new available sub-command

            :param self:
                Self
            :param moduleName:
                The module the class is found in
            :param className:
                The name of the class to import from the module

            :return none:
            """

            self.moduleName = moduleName
            self.className = className

        def getClass(self):
            """Gets the sub-command's class instance

            :param self:
                Self

            :return None:
                Failed to get class instance
            :return Class:
                The class instance
            """

            try:
                _module = importlib.import_module(self.moduleName)
                _class = getattr(_module, self.className)

                return _class

            except ImportError:
                return None

    @staticmethod
    def _generateDescription(description):
        """Generates a big string describing this command

        :param description:
            The description text

        :return String:
            The description string
        """

        # We likely have a description with a bunch of leading whitespace from a
        # multi-line string in the raw Python source, so let's first strip all
        # of that away
        fields = description.split("\n", maxsplit = 1)

        # If there is a potential special case where the first line began
        # immediately after the triple quote, only unindent everything after
        # that line
        if fields[0] == fields[0].lstrip():
            description = fields[0] + "\n" + textwrap.dedent(fields[1])

        # Else, unindent everything together
        else:
            description = textwrap.dedent(description)

        # Next let's justify each line to our own standards
        #
        # Each line is separated by newline characters in the Python multi-line
        # string itself, so break the multi-line string into each individual
        # line.
        lines = description.split("\n")

        # We're going to be a little lazy with our appending and cleanup as we
        # form paragraphs, so make sure our space-removing step gets run on the
        # final paragraph by having an additional empty line to begin one final,
        # empty paragraph
        lines.append("")

        paragraphs = [""]

        # Next, the raw source code has its own justification, but that's not
        # necessarily aligned to the same boundary that we want to display in
        # the command's output on a terminal, so we'll need to collect each
        # paragraph
        #
        # So, let's string (ha) each line together into a single continuous
        # string that we can justify on our own.
        #
        # We'll note the end of a paragraph once we hit an entirely blank line,
        # and we'll combine each line by adding a space between them.
        for line in lines:
            # If this is an empty line, this is the end of the previous
            # paragraph
            if line == "":
                # We're going to append a space at the beginning of each
                # paragraph with our lazy appending below, so make sure we
                # remove that from each paragraph
                paragraphs[-1] = paragraphs[-1][1:]

                paragraphs.append("")

            # Else, got another line that applies to the current paragraph, so
            # append it
            else:
                paragraphs[-1] += " " + line

        text = ""

        # We've got our paragraphs, so let's finally output each line as it'll
        # appear on a terminal as a single string
        for paragraph in paragraphs:
            lines = textwrap.wrap(paragraph, 80)

            for line in lines:
                text += line + "\n"

            text += "\n"

        # Don't have additional excessive line endings at the beginning or end
        text = text.lstrip("\n").rstrip("\n")

        return text

    def __init__(self, name, help, description, subCommands = None, needUsb = False, configs = None):
        """Creates a new skywire command

        This will append a prefix to all Skywire Command child classes to
        better organize them and avoid conflicts with upstream west commands in
        the same scope as these.

        :param self:
            Self
        :param name:
            The name of the Skywire command
        :param help:
            The short-form help text of the Skywire command
        :param description:
            The long-form description text of the Skywire command
        :param subCommands:
            Sub-commands that this command contains
        :param needUsb:
            Whether or not this command needs USB functionality
        :param configs:
            Configurations for this command

        :return none:
        """

        if subCommands == None:
            subCommands = []

        # Add the configurations as additional description text
        if (configs != None) and (len(configs) > 0):
            description += "\n\nConfigurations:"

            for config in configs:
                description += "\n\n    {}:{}".format(Command.ConfigPrefix, config)

        self._name = name
        self._help = help
        self._description = Command._generateDescription(description = description)

        self._subCommands = []

        # Instantiate each of the sub-commands
        for subCommand in subCommands:
            subCommandClass = subCommand.getClass()

            if subCommandClass != None:
                self._subCommands.append(subCommandClass())

        self._needUsb = needUsb
        self._configs = configs

    def getConfig(self, name):
        """Gets a configuration for a command

        :param self:
            Self
        :param name:
            The name of the configuration to get

        :return None:
            Configuration not found
        :return String:
            The configurtion's value
        """

        # We'll let them qualify namespaces with ':' in their provided name,
        # but we need to split off any namespaces and combine with our uber
        # namespace; and provide the final configuration option name as a
        # standalone string
        fields = name.split(".")

        namespace = Command.ConfigPrefix

        if len(fields) > 1:
            namespace += ":{}".format(fields[0])
            option = fields[1]
        else:
            option = fields[0]

        return config.get(
            namespace,
            option,
            fallback = None
        )

    def _createParser(self, parser):
        """Adds our root parser

        :param self:
            Self
        :param parser:
            The parser adder

        :return parser:
            The root parser
        """

        # Make sure we keep our wonderful description's formatting by telling
        # the underlying argparse.ArgumentParser to use a formatter class of
        # 'raw'
        #
        # This should effectively mean all of our hard formatting work above is
        # left alone and printed to the console literally.
        return parser.add_parser(
            self._name,
            help = self._help,
            description = self._description,
            formatter_class = argparse.RawDescriptionHelpFormatter
        )

    def _addArguments(self, parser):
        """Adds arguments to a parser

        :param self:
            Self
        :param parser:
            The parser to add arguments to

        :return none:
        """

        # First add this command's arguments
        self.addArguments(parser = parser)

        # If we don't have sub-commands, nothing else to do
        if len(self._subCommands) < 1:
            return

        # Make a sub-parser for our sub-commands
        #
        # To avoid issues with nested sub-command users, make our sub-command
        # name argument unique to us.
        parser = parser.add_subparsers(
            title = "{}SubCommands".format(self._name),
            dest = "{}SubCommand".format(self._name),
            required = True
        )

        # For each of our command's sub-commands
        for subCommand in self._subCommands:
            # Add a new parser for this sub-command
            subParser = subCommand._createParser(parser = parser)

            # Add this sub-command's arguments
            subCommand._addArguments(parser = subParser)

    def _runCommand(self, args, unknownArgs):
        """Runs the command

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return none:
        """

        # If we will not be compatible with WSL's limited USB functionality and
        # we're running under WSL, elevate to PowerShell
        if self._needUsb and Wsl.isWsl():
            Wsl.forward()
            return

        try:
            # Always give the base command the chance to run
            try:
                done = self.runCommand(args, unknownArgs)

            except NotImplementedError:
                done = False

            # If that was it or we don't have any sub-commands, move on
            if done or (len(self._subCommands) < 1):
                return

            # Get the name of the sub-command, which we made unique
            subCommandName = args.__getattribute__("{}SubCommand".format(self._name))

            # Try to find a sub-command that'll run this
            for subCommand in self._subCommands:
                if subCommand._name == subCommandName:
                    subCommand._runCommand(args = args, unknownArgs = unknownArgs)
                    return

        except KeyboardInterrupt as ex:
            self.abortCommand()

    def _generateUnimplementedException(self):
        """Generates an unimplemented exception with a function's signature

        :param self:
            Self

        :raise NotImplementedError:

        :return none:
        """

        raise NotImplementedError("'{}' not implemented in '{}'!".format(
            inspect.currentframe().f_back.f_code.co_name,
            self.__class__.__name__
        ))

    def addArguments(self, parser):
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        self._generateUnimplementedException()

    def runCommand(self, args, unknownArgs):
        """Runs the command

        Typical commands do not need to return a value, but commands with
        sub-commands might want to do some intermediate or final handling, and
        can use the return as an indication that the command is done being
        handled.

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return None:
        :return False:
            Command not done
        :return True:
            Command handled
        """

        self._generateUnimplementedException()

    def abortCommand(self):
        """Aborts the command

        :param self:
            Self

        :return none:
        """

        pass
