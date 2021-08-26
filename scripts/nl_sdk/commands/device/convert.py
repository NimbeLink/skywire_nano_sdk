"""
Converts a Skywire Nano device

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

import nimbelink.command as command

class ConvertCommand(command.Command):
    """Converts a Skywire Nano device
    """

    def __init__(self) -> None:
        """Creates a new convert command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "convert",
            needUsb = True,
            help = "Converts a Skywire Nano device for application firmware use"
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

        self.stdout.info("Converting device...")

        # Make sure the device has a blank slate with our 'convert' process
        converted = args.nano.tool.mailbox.convert()

        if not converted:
            self.stdout.error("Failed to convert device")
            return 1

        self.stdout.info("Device converted")

        return 0
