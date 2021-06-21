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

import nl_sdk.commands as commands

class InitializeCommand(commands.ProjectCommand):
    """Initializes a converted Skywire Nano device
    """

    def __init__(self) -> None:
        """Creates a new update command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "initialize",
            help = "Initializes a Skywire Nano device for application firmware use",
            singleProject = True,
            resources = [
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.SignKey),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.EncryptKey),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.Kconfig),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.Partitions),
            ]
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

        self.stdout.info("Converting device...")

        # Make sure the device has a blank slate with our 'convert' process
        converted = args.nano.tool.mailbox.convert()

        if not converted:
            self.stdout.error("Failed to convert device")
            return 1

        self.stdout.info("Device converted")

        for project in args.projects:
            self.stdout.info("")
            self.stdout.info(f"Initializing Skywire Nano with project '{project}'")

            # If we don't have a signing key, that's a paddlin'
            if len(project.signKeys) < 1:
                self.stdout.error("No signing key(s)")
                return 1

            # If we don't have an encrypting key, skip it, but at least let them
            # know
            if len(project.encryptKeys) < 1:
                self.stdout.warning("No encrypting key, only initializing signing key")

            # Put together all of the things we'll be updating
            blobs = []

            for signKey in project.signKeys:
                self.stdout.info(f"Adding signing key '{signKey}'")

                blobs.append((signKey.data, nano.Dfu.Type.Key))

            for encryptKey in project.encryptKeys:
                self.stdout.info(f"Adding encrypting key '{encryptKey}'")

                blobs.append((encryptKey.data, nano.Dfu.Type.Key))

            if project.partitions is not None:
                self.stdout.info(f"Adding patitions '{project.partitions}'")

                blobs.append((project.partitions.data, nano.Dfu.Type.Partition))

            # Update!
            for blob in blobs:
                self.stdout.info("Uploading next file...")

                args.nano.app.upload(data = blob[0], type = blob[1])

                self.stdout.info("Upload done!")

        self.stdout.info("Done!")

        return 0
