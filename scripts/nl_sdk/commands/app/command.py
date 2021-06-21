"""
Works with Skywire Nano firmware

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

import nimbelink.command as command
import nimbelink.config as config

from .format import FormatCommand
from .setup import SetupCommand
from .sign import SignCommand

class Command(command.WestCommand):
    """A command for working with Skywire Nano firmware
    """

    def __init__(self) -> None:
        """Creates a new app command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "app",
            help = "Manages built Skywire Nano firmware images",
            subCommands = [
                SetupCommand(),
                SignCommand(),
                FormatCommand()
            ]
        )
