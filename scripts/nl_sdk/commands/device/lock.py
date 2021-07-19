"""
Locks a Skywire Nano device

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import typing

import nimbelink.command as command

class LockCommand(command.Command):
    """Locks a Skywire Nano device
    """

    def __init__(self) -> None:
        """Creates a new lock command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "lock",
            needUsb = True,
            help = "Locks a connected Skywire Nano device"
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        # Add an argument for which image to lock
        parser.add_argument(
            "-i", "--image",
            choices = ["secure", "nonsecure"],
            required = True,
            help = "Lock an application image on the device ('secure' or 'nonsecure')"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs our command

        :param self:
            Self
        :param args:
            Our arguments

        :return none:
        """

        if args.image == "secure":
            secure = True

        elif args.image == "nonsecure":
            secure = False

        else:
            self.stdout.error(f"Unknown image '{args.image}'")
            return 1

        self.stdout.info(f"Locking device '{args.image}' context...")

        args.nano.tool.uicr.enableApProtect(secure = secure)

        self.stdout.info("Locked!")

        return 0
