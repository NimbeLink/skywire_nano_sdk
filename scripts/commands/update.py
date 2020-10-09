###
 # \file
 #
 # \brief Works with Skywire Nano devices
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##
import argparse
import os
import serial
import time

from commands.skywire import SkywireCommand
from tools.debugger.ctrlAp import CtrlAp
from tools.debugger.mailbox import Mailbox
from tools.xmodem import Xmodem

class SkywireUpdateCommand(SkywireCommand):
    """A command for updating Skywire Nano devices with XMODEM
    """

    def __init__(self, *args, **kwargs):
        """Creates a new update command

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
            name = "update",
            needUsb = True,
            help = "updates Skywire Nano devices",
            about = [
                "This tool will attempt to update a Skywire Nano's firmware."
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

        # Add an argument for handling automatic rebooting after successful DFU
        # transfer
        parser.add_argument(
            "-n",
            "--no-reboot",
            dest = "noReboot",
            action = "count",
            default = 0,
            required = False,
            help = "Prevent the device from automatically rebooting after successful DFU transfer"
        )

        # Add an argument for using a debugger to trigger DFU
        parser.add_argument(
            "-d",
            "--debugger",
            dest = "debugger",
            action = "count",
            default = 0,
            required = False,
            help = "Use a debugger to trigger the update"
        )

        # Add an argument for passing in the AT terminal serial port for the
        # Nano
        parser.add_argument(
            "-a",
            "--at-device",
            dest = "atDevice",
            action = "store",
            required = False,
            metavar = "NAME",
            help = "An AT interface to use to start the update"
        )

        # Add an argument for passing in the XMODEM serial port for the Nano
        parser.add_argument(
            "-x",
            "--xmodem-device",
            dest = "xmodemDevice",
            action = "store",
            required = True,
            metavar = "NAME",
            help = "An XMODEM serial device to use to send the firmware file"
        )

        # Add an argument for defining the XMODEM packet size
        parser.add_argument(
            "-p",
            "--packet-size",
            dest = "packetSize",
            action = "store",
            type = int,
            choices = [128, 1024],
            default = 128,
            required = False,
            metavar = "SIZE",
            help = "The size of XMODEM packets, in bytes"
        )

        # Add an argument for controlling flow control/throttling selection
        parser.add_argument(
            "-t",
            "--throttle",
            dest = "throttle",
            action = "count",
            default = 0,
            required = False,
            help = "Use manual throttling of XMODEM data instead of flow control"
        )

        # Add an argument for passing in files to be flashed
        parser.add_argument(
            "files",
            nargs = argparse.REMAINDER,
            metavar = "FILE",
            help = "DFU file(s) to semd to the device"
        )

    def runCommand(self, args, unknownArgs):
        """Runs the update command

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return none:
        """

        # Make sure the files exist
        for file in args.files:
            if not os.path.isfile("{}".format(file)):
                print("File '{}' doesn't exist!".format(file))
                return

        # Set up our UART parameters
        if args.throttle > 0:
            self.flowControl = False

        else:
            self.flowControl = True

        self.packetSize = args.packetSize

        if (args.atDevice != None) and (args.atDevice != "skip"):
            # Get our AT terminal serial port device
            self.atDevice = serial.Serial(
                port = args.atDevice,
                baudrate = 115200,
                timeout = 1
            )

        else:
            self.atDevice = None

        if args.debugger > 0:
            self.debugger = Mailbox(CtrlAp())

        else:
            self.debugger = None

        # Get our XMODEM interface
        self.xmodem = Xmodem(device = serial.Serial(
            port = args.xmodemDevice,
            baudrate = 115200,
            timeout = 1,
            rtscts = self.flowControl
        ))

        # If we're being verbose, tell XMODEM that
        if args.verbose > 0:
            self.xmodem.verbose = True

        # Set up our interface
        if not self.setupInterface():
            return

        # Update!
        for file in args.files:
            # If this isn't the last file, don't reboot
            if file != args.files[-1]:
                autoReboot = False

            # Else, this is the last file, but if the user specifically doesn't
            # want to reboot after it's done, don't
            elif args.noReboot:
                autoReboot = False

            # Else, this is the last file and the user didn't say they didn't
            # want an automatic reboot when we're finished, so reboot
            else:
                autoReboot = True

            with open(file, "rb") as openedFile:
                self.updateDevice(file = openedFile, autoReboot = autoReboot)

    def abortCommand(self):
        """Handles the user quitting an update

        :param self:
            Self

        :return none:
        """

        print("Stopping update...")

        self.endTransmission()

    def setupInterface(self):
        """Sets up our communication interface
        :param self:
            Self
        :return True:
            Interface set up
        :return False:
            Failed to set up interface
        """

        # If we have an AT interface, crank our XMODEM's baud rate
        if self.atDevice:
            writeLength = self.atDevice.write("AT#UART=0,1000000,,\r".encode())

            # If that failed, that's a paddlin'
            if writeLength < 1:
                print("Failed to update baud rate")
                return False

            response = self.atDevice.read_until(terminator = "OK\r\n")

            if "OK\r\n" not in response.decode():
                print("Failed to get OK for baud rate ('{}')".format(response.decode()))
                return False

            # Update our serial port's baud rate
            settings = self.xmodem.device.get_settings()

            settings["baudrate"] = 1000000

            self.xmodem.device.apply_settings(settings)

        # If we have an AT interface and we're using it, turn on flow control
        if self.atDevice and self.flowControl:
            writeLength = self.atDevice.write("AT#UART=0,,2,2\r".encode())

            # If that failed, that's a paddlin'
            if writeLength < 1:
                print("Failed to turn on flow control")
                return False

            response = self.atDevice.read_until(terminator = "OK\r\n")

            if "OK\r\n" not in response.decode():
                print("Failed to get OK for flow control ('{}')".format(response.decode()))
                return False

        return True

    def updateDevice(self, file, autoReboot):
        """Updates our target device

        :param self:
            Self
        :param file:
            The file to update the device with
        :param autoReboot:
            Whether or not to automatically reboot

        :return True:
            Device updated
        :return False:
            Failed to update device
        """

        # Figure out how much data there is to send
        length = 0

        while True:
            # Get another chunk of data
            data = file.read(1024)

            # If we're out of data, move on
            if len(data) < 1:
                break

            # Note we got another chunk
            length = length + len(data)

        # Go back to the start of the file
        file.seek(0)

        if self.atDevice:
            # Start the AT-based update
            writeLength = self.atDevice.write("AT#FWUPD={},{}\r".format(length, int(autoReboot)).encode())

            # If that failed, that's a paddlin'
            if writeLength < 1:
                print("Failed to start firmware update")
                return False

            response = self.atDevice.read_until(terminator = "\r\n")

            if "\r\n" not in response.decode():
                print("Failed to get OK for update start")
                return False

            print("DFU started via AT command");

        elif self.debugger:
            if not self.debugger.dfu(length = length, autoReboot = autoReboot):
                print("Failed to trigger update with mailbox!")
                return False

            print("DFU started via mailbox")

        else:
            print("!!!! Assuming DFU has already been started")

        # The XMODEM port might have been outputting some kernel logging, so
        # give a little bit of time for that to occur before popping into the
        # XMODEM handling (which will do its own sanity buffer clearing)
        time.sleep(0.5)

        return self.xmodem.transfer(file, self.packetSize)
