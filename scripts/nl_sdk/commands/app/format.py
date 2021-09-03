"""
Formats Skywire Nano device firmware for DFU uploading

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import typing

import nimbelink.cell.modem.nano as nano

import nl_sdk.commands as commands

class FormatCommand(commands.ProjectCommand):
    """Formats Skywire Nano device firmware for DFU uploading

    This command applies a Skywire Nano-specific DFU header to a firmware image

    Commands handling uploading firmware to a Skywire Nano handle the process of
    applying headers on-the-fly, but if the firmware image needs to be hosted
    for FOTA or needs to be available locally ahead of time (e.g. for sending
    via an application's XMODEM handling) the header can be applied to the
    firmware image with this command.
    """

    def __init__(self) -> None:
        """Creates a new format command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            singleProject = True,
            resources = [
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.UpdateArtifact, name = "application"),
            ]
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        commands.ProjectCommand.addArguments(self, parser = parser)

        parser.add_argument(
            "-s", "--stack",
            required = False,
            help = "Specify a stack firmware update file to format"
        )

        parser.add_argument(
            "-m", "--modem",
            required = False,
            help = "Specify a modem firmware update file to format"
        )

        parser.add_argument(
            "output",
            nargs = 1,
            help = "The file to write the formatted firmware image to"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs our command

        :param self:
            Self
        :param args:
            Our arguments

        :return int:
            Our result
        """

        result = commands.ProjectCommand.runCommand(self, args = args)

        if result is not None:
            return result

        # Make sure our 'output' variable is single-length
        args.output = args.output[0]

        # If they didn't provide anything to do, assume they want to use their
        # application firmware
        if (args.application is None) and (args.stack is None) and (args.modem is None):
            args.application = args.projects[0].updateArtifact

            # If this project's update artifact is outdated, at least warn about
            # the most recent build having likely not been re-signed
            if args.projects[0].isOutdated(artifact = args.projects[0].updateArtifact):
                self.stdout.warning("Update file likely outdated from most recent build (did you forget to sign?)")

        things = [thing for thing in [args.application, args.stack, args.modem] if thing is not None]

        # If they provided more than one thing, that's a paddlin'
        if len(things) > 1:
            self.stdout.error("Can only format one image at a time, choose from:")

            for thing in things:
                self.stdout.error(f"    {thing}")

            return 1

        if args.stack is not None:
            self.stdout.info(f"Formatting stack update '{args.stack}'...")

            with open(args.stack, "rb") as input:
                with open(args.output, "wb") as output:
                    output.write(nano.Dfu.format(input.read(), nano.Dfu.Type.Stack))

        elif args.application is not None:
            self.stdout.info(f"Formatting application update '{args.application}'...")

            with open(args.application, "rb") as input:
                with open(args.output, "wb") as output:
                    output.write(nano.Dfu.format(input.read(), nano.Dfu.Type.Application))

        elif args.modem is not None:
            self.stdout.info(f"Formatting modem update '{modem}'...")

            with open(args.modem, "rb") as input:
                with open(args.output, "wb") as output:
                    output.write(nano.Dfu.format(input.read(), nano.Dfu.Type.Modem))

        self.stdout.info("Formatting done!")

        return 0
