"""
Works with a Skywire Nano device

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import serial
import typing

import nimbelink.cell.at as at
import nimbelink.cell.modem.nano as nano
import nimbelink.command as command
import nimbelink.debugger as debugger
import nimbelink.utils as utils

from .flash import FlashCommand
from .initialize import InitializeCommand
from .lock import LockCommand
from .ping import PingCommand
from .update import UpdateCommand

class Command(command.Command):
    """A command for communicating with Skywire Nano devices
    """

    def __init__(self) -> None:
        """Creates a new device command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "device",
            help = "Communicates with a Skywire Nano device",
            needUsb = True,
            subCommands = [
                InitializeCommand(),
                FlashCommand(),
                UpdateCommand(),
                LockCommand(),
                PingCommand(),
            ]
        )

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds parser arguments

        A few of our sub-commands will want similar communication parameters, so
        we might as well single-source that setup and handling.

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        # Add an argument for passing in the AT terminal serial port for the
        # Nano
        parser.add_argument(
            "-a", "--at-device",
            dest = "atDevice",
            required = False,
            help = "An AT interface serial device to use to start the update"
        )

        # Add an argument for passing in the AT interface's baud rate
        parser.add_argument(
            "--at-baudrate",
            dest = "atBaudRate",
            default = 115200,
            required = False,
            help = "Specify the AT interface serial device's baud rate"
        )

        # Add an argument for passing in the XMODEM serial port for the Nano
        parser.add_argument(
            "-x", "--xmodem-device",
            dest = "xmodemDevice",
            required = False,
            help = "An XMODEM serial device to use to send the firmware file"
        )

        # Add an argument for passing in the XMODEM's baud rate
        parser.add_argument(
            "--xmodem-baudrate",
            dest = "xmodemBaudRate",
            default = 115200,
            required = False,
            help = "Specify the XMODEM serial device's baud rate"
        )

        # Add an argument for controlling flow control/throttling selection
        parser.add_argument(
            "-t", "--throttle",
            action = "count",
            default = 0,
            required = False,
            help = "Use manual throttling of XMODEM data instead of flow control"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs our command

        :param self:
            Self
        :param args:
            Our arguments

        :return None:
            Command not handled
        :return int:
            Our result
        """

        # If they're throttling UART traffic, assume it's because we don't have
        # flow control
        if args.throttle > 0:
            flowControl = False

        else:
            flowControl = True

        # If they specified the AT interface, make it
        if args.atDevice is not None:
            try:
                interface = at.Interface(
                    port = args.atDevice,
                    baudrate = args.atBaudRate,
                    rtscts = flowControl
                )
            except serial.serialutil.SerialException as ex:
                if "PermissionError" not in f"{ex}":
                    raise ex

                self.stdout.error(f"Failed to access serial port '{args.atDevice}'; is it open elsewhere?")

                return 1

            tool = None

        # Else, assume we'll need to try to use a debugger to trigger this
        else:
            interface = None

            tool = debugger.Tool()

        # If they specified the XMODEM interface, make it
        if args.xmodemDevice is not None:
            try:
                kernelLog = device = serial.Serial(
                    port = args.xmodemDevice,
                    baudrate = args.xmodemBaudRate,
                    timeout = 1,
                    rtscts = flowControl
                )

            except serial.serialutil.SerialException as ex:
                if "PermissionError" not in f"{ex}":
                    raise ex

                self.stdout.error(f"Failed to access serial port '{args.xmodemDevice}'; is it open elsewhere?")

                return 1

        else:
            kernelLog = None

        # Make our Nano
        args.nano = nano.SkywireNano(
            interface = interface,
            kernelLog = kernelLog,
            tool = tool
        )

        # Let sub-commands run
        return None
