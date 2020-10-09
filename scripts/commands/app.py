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

from commands.skywire import SkywireCommand
from tools.debugger.ctrlAp import CtrlAp
from tools.debugger.mailbox import Mailbox
from tools.debugger.uicr import Uicr

class SkywireAppCommand(SkywireCommand):
    """A command for communicating with Skywire Nano application firmware
    """

    def __init__(self, *args, **kwargs):
        """Creates a new app command

        :param self:
            Self
        :param *args:
            Positional arguments
        :param **kwargs:
            Keyword arguments

        :return none:
        """

        super().__init__(
            *args,
            **kwargs,
            name = "app",
            needUsb = True,
            help = "communicates with Skywire Nano application firmware",
            about = [
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

        # Add an argument for halting the monitor
        parser.add_argument(
            "-p",
            "--primary-halt",
            type = lambda x: int(x, 0),
            dest = "haltPrimary",
            action = "store",
            required = False,
            metavar = "SEC",
            help = "Attempt to halt the Nano's primary application"
        )

        # Add an argument for halting the widget
        parser.add_argument(
            "-s",
            "--secondary-halt",
            type = lambda x: int(x, 0),
            dest = "haltSecondary",
            action = "store",
            required = False,
            metavar = "SEC",
            help = "Attempt to halt the Nano's secondary application"
        )

        # Add an argument for converting the device
        parser.add_argument(
            "-c",
            "--convert",
            dest = "convert",
            action = "count",
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

        mailbox = Mailbox(ctrlAp = CtrlAp())

        # If they want to halt the monitor, do so
        if args.haltPrimary != None:
            halted = mailbox.halt(
                target = Mailbox.Target.Monitor,
                duration = args.haltPrimary
            )

            if halted:
                print("Primary application halted")
            else:
                print("Failed to halt primary application")

        # If they want to halt the widget, do so
        if args.haltSecondary != None:
            halted = mailbox.halt(
                target = Mailbox.Target.Widget,
                duration = args.haltSecondary
            )

            if halted:
                print("Secondary application halted")
            else:
                print("Failed to halt secondary application")

        # If they want to start a conversion, do so
        if args.convert > 0:
            converted = mailbox.convert()

            if converted:
                print("Unit converted")
            else:
                print("Failed to convert unit")
