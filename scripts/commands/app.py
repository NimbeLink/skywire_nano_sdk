###
 # \file
 #
 # \brief Works with Skywire Nano application firmware
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##
import math
import os
import platform
import subprocess

from commands.command import Command
from tools.debugger.ctrlAp import CtrlAp
from tools.debugger.mailbox import Mailbox
from tools.debugger.uicr import Uicr

class AppCommand(Command):
    """A command for communicating with Skywire Nano application firmware
    """

    def __init__(self):
        """Creates a new app command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "app",
            needUsb = True,
            help = "communicates with Skywire Nano application firmware",
            description = [
                "This tool will attempt to communicate with a Nano."
            ]
        )

    def addArguments(self, parser):
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        # Add an argument for pinging the device
        parser.add_argument(
            "-p",
            "--ping",
            dest = "ping",
            action = "count",
            default = 0,
            required = False,
            help = "Ping the connected device"
        )

        # Add an argument for converting the device
        parser.add_argument(
            "-c",
            "--convert",
            dest = "convert",
            action = "count",
            default = 0,
            required = False,
            help = "Convert the device to a flash-able setup"
        )

        # Add an argument for actually locking the device
        parser.add_argument(
            "-l",
            "--lock",
            dest = "lock",
            action = "store",
            choices = ["secure", "nonsecure"],
            required = False,
            metavar = "IMG",
            help = "Lock an application image on the device, 'secure' or 'nonsecure'"
        )

    def runCommand(self, args, unknownArgs):
        """Runs the unlock command

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return none:
        """

        if args.lock != None:
            uicr = Uicr()

            if args.lock == "secure":
                secure = True
            elif args.lock == "nonsecure":
                secure = False

            uicr.enableApProtect(secure = secure)

            del uicr

        mailbox = Mailbox(ctrlAp = CtrlAp())

        # If they want to ping, do so
        if args.ping > 0:
            pinged = mailbox.ping()

            if pinged:
                print("Pinged!")
            else:
                print("Failed to ping device")

        # If they want to start a conversion, do so
        if args.convert > 0:
            converted = mailbox.convert()

            if converted:
                print("Device converted")
            else:
                print("Failed to convert device")
