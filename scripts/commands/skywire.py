###
 # \file
 #
 # \brief Works with Skywire Nano devices
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

from west.commands import WestCommand
from west.configuration import config

from tools.wsl import Wsl

class SkywireCommand(WestCommand):
    """A west command for working with Skywire Nano devices, collected under
    the root 'skywire' command
    """

    NamePrefix = "skywire"
    """A prefix to go before each command's name, in the form of:

        '<prefix>-<name>'
    """

    ConfigPrefix = "skywire:nano"
    """A prefix we'll use for all of our Skywire Nano command configurations"""

    def generateDescription(self):
        """Generates a big string describing this command

        :param self:
            Self

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

        for paragraph in self._about:
            # Move our raw strings over so they're justified to the left
            justifiedText = textwrap.dedent(paragraph)

            # Wrap the lines at 80 columns
            lines += textwrap.wrap(
                justifiedText,
                80
            )

            # Add in a blank line between each paragraph's set of lines
            lines.append("")

        description = ""

        for line in lines:
            # Compile the 80-column lines generated above into a single string
            description += "{}\n".format(line)

        return description

    def __init__(self, *args, name, about, needUsb = False, configs = None, **kwargs):
        """Creates a new skywire command

        This will append a prefix to all Skywire Command child classes to
        better organize them and avoid conflicts with upstream west commands in
        the same scope as these.

        :param self:
            Self
        :param *args:
            Additional arguments
        :param **kwargs:
            Additional keyword arguments
        :param name:
            The name of the Skywire command
        :param about:
            The long-form about text of the Skywire command
        :param needUsb:
            Whether or not this command needs USB functionality

        :return none:
        """

        # Add the configurations as additional 'about' text
        if (configs != None) and (len(configs) > 0):
            about += ["Configurations:"]

            for config in configs:
                about += ["-    {}:{}".format(SkywireCommand.ConfigPrefix, config)]

        self._name = name
        self._about = about
        self._needUsb = needUsb
        self._configs = configs

        if "prefix" not in kwargs:
            prefix = True
        else:
            prefix = kwargs["prefix"]

            kwargs.pop("prefix")

        # If we should include a prefix, figure that out
        if prefix:
            # Append our prefix to the command's name
            if not name.startswith(SkywireCommand.NamePrefix):
                name = "{}-{}".format(SkywireCommand.NamePrefix, name)

        # Make sure the child class didn't try to specify 'description'
        # manually, since we'll do that for them
        for key, value in kwargs.items():
            if key == "description":
                raise Exception(
                    "Do not include a description in a Skywire command ('{}')!".format(
                        self.__name__
                    )
                )

        # Generate the description text
        description = self.generateDescription()

        # Pass up along the chain of inheritance
        super().__init__(name, *args, **kwargs, description = description)

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

        namespace = SkywireCommand.ConfigPrefix

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

    def do_add_parser(self, parserAdder):
        """Adds a parser

        :param self:
            Self
        :param parserAdder:
            The parser adder

        :return parser:
            The new parser
        """

        # Make sure we keep our wonderful description's formatting by telling
        # the underlying argparse.ArgumentParser to use a formatter class of
        # 'raw'
        #
        # This should effectively mean all of our hard formatting work above is
        # left alone and printed to the console literally.
        parser = parserAdder.add_parser(
            self.name,
            help = self.help,
            description = self.description,
            formatter_class = argparse.RawDescriptionHelpFormatter
        )

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

        self.addArguments(parser)

        return parser

    def do_run(self, args, unknownArgs):
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
