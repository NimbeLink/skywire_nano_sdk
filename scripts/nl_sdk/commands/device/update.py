"""
Updates Skywire Nano device firmware

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
import nimbelink.command as command

import nl_sdk.commands as commands

class UpdateCommand(commands.ProjectCommand):
    """Updates Skywire Nano device firmware via XMODEM
    """

    def __init__(self) -> None:
        """Creates a new update command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "update",
            help = "Updates Skywire Nano device firmware via XMODEM",
            singleProject = False,
            resources = [
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.UpdateArtifact, name = "application", singleValue = False),
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
            action = "append",
            required = False,
            help = "Specify a stack firmware update file to update"
        )

        parser.add_argument(
            "-m", "--modem",
            action = "append",
            required = False,
            help = "Specify a modem firmware update file to update"
        )

        parser.add_argument(
            "-n", "--no-reboot",
            dest = "noReboot",
            action = "count",
            default = 0,
            required = False,
            help = "Prevent the device from automatically rebooting after successful DFU transfer"
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

        # Convert our reboot indicator to something more useful
        if args.noReboot > 0:
            allowReboot = False
        else:
            allowReboot = True

        # If they didn't provide anything to do, assume they want to update with
        # their application firmware
        if (args.application is None) and (args.stack is None) and (args.modem is None):
            args.application = []

            for project in args.projects:
                args.application += [project.updateArtifact]

                # If this project's update artifact is outdated, at least warn
                # about the most recent build having likely not been re-signed
                if project.isOutdated(artifact = project.updateArtifact):
                    self.stdout.warning("Update file likely outdated from most recent build (did you forget to sign?)")

        # Put together all of the things we'll be updating
        blobs = []

        if args.stack is not None:
            for stack in args.stack:
                self.stdout.info(f"Adding stack update '{stack}'")

                with open(stack, "rb") as file:
                    blobs.append((file.read(), nano.Dfu.Type.Stack))

        if args.application is not None:
            for application in args.application:
                self.stdout.info(f"Adding application update '{application}'")

                with open(application, "rb") as file:
                    blobs.append((file.read(), nano.Dfu.Type.Application))

        if args.modem is not None:
            for modem in args.modem:
                self.stdout.info(f"Adding modem update '{modem}'")

                with open(modem, "rb") as file:
                    blobs.append((file.read(), nano.Dfu.Type.Modem))

        # Update!
        for blob in blobs:
            # If this isn't the last thing, don't reboot
            if blob != blobs[-1]:
                autoReboot = False

            # Else, this is the last thing, so defer to if the user said to not
            # reboot
            else:
                autoReboot = allowReboot

                if not autoReboot:
                    self.stdout.info("Skipping reboot")

            self.stdout.info("Uploading next file...")

            args.nano.app.upload(data = blob[0], type = blob[1], reboot = autoReboot)

            self.stdout.info("Upload done!")

        self.stdout.info("Done!")

        return 0
