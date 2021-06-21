"""
Pings a Skywire Nano device

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

import nimbelink.command as command

class PingCommand(command.Command):
    """Pings a Skywire Nano device
    """

    def __init__(self) -> None:
        """Creates a new ping command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "ping",
            needUsb = True,
            help = "Pings a connected Skywire Nano device"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs our command

        :param self:
            Self
        :param args:
            Our arguments

        :return none:
        """

        self.stdout.info("Pinging device...")

        pinged = args.nano.tool.mailbox.ping()

        if not pinged:
            self.stdout.error("Failed to ping device")
            return 1

        self.stdout.info("Pinged!")

        return 0
