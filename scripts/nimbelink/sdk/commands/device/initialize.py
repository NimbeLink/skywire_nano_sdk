"""
Initializes a converted Skywire Nano device

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import struct
import typing

import nimbelink.cell.modem.nano as nano
import nimbelink.command as command

import nimbelink.sdk.commands as commands

class InitializeCommand(commands.ProjectCommand):
    """Initializes a Skywire Nano device for application firmware use
    """

    def __init__(self) -> None:
        """Creates a new update command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            singleProject = True,
            resources = [
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.SignKey),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.EncryptKey),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.Kconfig),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.Partitions),
            ]
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds our arguments

        :param self:
            Self
        :param parser:
            The parser to add our arguments to

        :return none:
        """

        commands.ProjectCommand.addArguments(self, parser = parser)

        parser.add_argument(
            "-n", "--no-convert",
            dest = "noConvert",
            action = "count",
            default = 0,
            required = False,
            help = "Skip the conversion process before uploading resources"
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

        # If they didn't provide anything to do, assume they want to update all
        # of their project's resources
        if (args.signKey is None) and (args.encryptKey is None) and (args.partitions is None):
            # If we don't have a signing key, that's a paddlin'
            #
            # We want to be more aggressive with our project auto-lookup
            # handling, since a user is less likely to be trying to do something
            # fancy and omitting signing keys.
            if len(args.projects[0].signKeys) < 1:
                self.stdout.error("No signing key(s)")
                return 1

            args.signKey = args.projects[0].signKeys
            args.encryptKey = args.projects[0].encryptKeys
            args.partitions = args.projects[0].partitions

        # If we don't have a signing key, skip it, but if we're converting the
        # device at least let them know
        if ((args.signKey is None) or (len(args.signKey) < 1)) and not args.noConvert:
            self.stdout.warning("No signing key, converted devices without one will likely not run properly")

        # If we don't have an encrypting key, skip it, but at least let them
        # know
        if (args.encryptKey is None) or (len(args.encryptKey) < 1):
            self.stdout.warning("No encrypting key, only initializing signing key")

        # If they didn't request skipping the conversion process, do that first
        if not args.noConvert:
            self.stdout.info("Converting device...")

            # Make sure the device has a blank slate with our 'convert' process
            converted = args.nano.tool.mailbox.convert()

            if not converted:
                self.stdout.error("Failed to convert device")
                return 1

            self.stdout.info("Device converted")

        else:
            self.stdout.info("Skipping converting device")

        self.stdout.info("")
        self.stdout.info(f"Initializing Skywire Nano with project '{args.projects[0]}'")

        # Put together all of the things we'll be updating
        blobs = []

        if args.signKey is not None:
            for signKey in args.signKey:
                self.stdout.info(f"Adding signing key '{signKey}'")

                blobs.append((signKey.data, nano.Dfu.Type.Key))

        if args.encryptKey is not None:
            for encryptKey in args.encryptKey:
                self.stdout.info(f"Adding encrypting key '{encryptKey}'")

                blobs.append((encryptKey.data, nano.Dfu.Type.Key))

        if args.partitions is not None:
            self.stdout.info(f"Adding patitions '{args.partitions}'")

            blobs.append((args.partitions.data, nano.Dfu.Type.Partition))

        # Update!
        for blob in blobs:
            self.stdout.info("Uploading next file...")

            args.nano.app.upload(data = blob[0], type = blob[1])

            self.stdout.info("Upload done!")

        self.stdout.info("Done!")

        return 0
