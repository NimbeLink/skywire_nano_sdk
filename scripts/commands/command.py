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

from west.configuration import config

from tools.wsl import Wsl

class Command:
    """A west command for working with Skywire Nano devices, collected under
    the root 'skywire' command
    """

    ConfigPrefix = "skywire:nano"
    """A prefix we'll use for all of our Skywire Nano command configurations"""

    @staticmethod
    def _generateDescription(description):
        """Generates a big string describing this command

        :param description:
            The description text

        :return String:
            The description string
        """

        # I'm going through a few hoops here to make it easier on you lazy devs
        # out there
        #
        # We'll first make a series of multi-line strings using Python's
        # triple-quote syntax. Then, for each one of those, we'll use
        # textwrap.dedent() to drop the indendations that Python will include
        # in the original strings -- which mucks with the console's output, as
        # it should be left-aligned.
        #
        # After we have a large string, we'll auto-justify it to 80 columns to
        # make it look nice and pretty. Then we'll go through and compile the
        # ultimate string with each of those justified lines, including extra
        # blank lines between each paragraph's set of lines.
        #
        # This all keeps things here in the source nice and easy to format
        # without having to do things like have our text all the way at the
        # left of the editor screen or for developers to have to move the text
        # around their screen as they're editing the description itself to
        # manually justify it in the source. All you should have to do is edit
        # the text, justify the whole thing here in the source (purely for the
        # sake of people looking at the source), and move on.
        #
        # Additionally, the tripe-quotes and backslash are critical for
        # textwrap.dedent() to work. Not including that puts the first line at
        # a different indentation level in the original string -- which makes
        # sense -- and that prevents it from properly doing its job
        # (essentially, it just leaves the trailing indented lines alone,
        # effectively doing nothing).
        #
        # Please keep the standalone triple-quotes below, as some of us have
        # hand-compiled syntax highlighters for our editors that are a little
        # more picky about Python's triple-quote syntax
        lines = []

        for paragraph in description:
            # Move our raw strings over so they're justified to the left
            justifiedText = textwrap.dedent(paragraph)

            # Wrap the lines at 80 columns
            lines += textwrap.wrap(
                justifiedText,
                80
            )

            # Add in a blank line between each paragraph's set of lines
            lines.append("")

        text = ""

        for line in lines:
            # Compile the 80-column lines generated above into a single string
            text += "{}\n".format(line)

        return text

    def __init__(self, name, help, description, needUsb = False, configs = None):
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
        :param needUsb:
            Whether or not this command needs USB functionality
        :param configs:
            Configurations for this command

        :return none:
        """

        # Add the configurations as additional description text
        if (configs != None) and (len(configs) > 0):
            description += ["Configurations:"]

            for config in configs:
                description += ["-    {}:{}".format(Command.ConfigPrefix, config)]

        self._name = name
        self._help = help
        self._needUsb = needUsb
        self._configs = configs

        # Generate the description text
        self._description = Command._generateDescription(description = description)

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

    def _addArguments(self, parserAdder):
        """Adds a parser

        :param self:
            Self
        :param parserAdder:
            The parser adder

        :return none:
        """

        # Make sure we keep our wonderful description's formatting by telling
        # the underlying argparse.ArgumentParser to use a formatter class of
        # 'raw'
        #
        # This should effectively mean all of our hard formatting work above is
        # left alone and printed to the console literally.
        parser = parserAdder.add_parser(
            self._name,
            help = self._help,
            description = self._description,
            formatter_class = argparse.RawDescriptionHelpFormatter
        )

        self.addArguments(parser)

    def _runCommand(self, args, unknownArgs):
        """Runs the stuff command

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
            self.runCommand(args, unknownArgs)
        except KeyboardInterrupt as ex:
            self.abortCommand()

    def generateUnimplementedException(self):
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

        self.generateUnimplementedException()

    def runCommand(self, args, unknownArgs):
        """Runs the stuff command

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return none:
        """

        self.generateUnimplementedException()

    def abortCommand(self):
        """Aborts the stuff command

        :param self:
            Self

        :return none:
        """

        pass
