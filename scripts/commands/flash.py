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

from intelhex import IntelHex

from commands.skywire import SkywireCommand
from tools.debugger.ahb import Ahb
from tools.flash import Flash

class SkywireFlashCommand(SkywireCommand):
    """A command for flashing Skywire Nano devices
    """

    def __init__(self, *args, **kwargs):
        """Creates a new flash command

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
            name = "flash",
            needUsb = True,
            configs = [
                "flash.<profile>"
            ],
            help = "flashes Skywire Nano devices",
            about = [
                "This tool will auto-detect the current environment and select the\
                correct programming interface to flash an attached Skywire Nano\
                device."
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

        # Add an argument for an initial mass erase of the device
        parser.add_argument(
            "-e",
            "--erase",
            dest = "erase",
            action = "count",
            default = 0,
            required = False,
            help = "First perform a mass erase of the device"
        )

        # Add an argument for passing in files using a configuration
        parser.add_argument(
            "-c",
            "--config",
            dest = "config",
            action = "store",
            required = False,
            metavar = "CFGNAME",
            help = "A west configuration to get a file list from (multiple files separated by ';')"
        )

        # Add an argument for passing in files to be flashed
        parser.add_argument(
            "files",
            nargs = argparse.REMAINDER,
            metavar = "FILE",
            help = "HEX file(s) to program the device with"
        )

    def runCommand(self, args, unknownArgs):
        """Runs the flash command

        :param self:
            Self
        :param args:
            Our known/expected arguments
        :param unknownArgs:
            Our unknown arguments

        :return none:
        """

        files = []

        # If they're using a configuration, grab those files first
        if args.config != None:
            config = self.getConfig("flash.{}".format(args.config))

            # If that failed, that's a paddlin'
            if config == None:
                print("Failed to find configuration {}:flash.{}".format(
                    SkywireCommand.ConfigPrefix,
                    args.config
                ))

                return

            files = config.split(";")

        # If they provided any, add in their specified files
        if args.files != None:
            files.extend(args.files)

        # Make our AHB access port
        ahb = Ahb()

        # Try to reset and halt our target
        try:
            print("Resetting and halting device...")

            ahb.dap.api.sys_reset()
            ahb.dap.api.halt()

            # If they want an erase, do that first
            if args.erase > 0:
                print("Mass erasing device...")

                ahb.dap.api.recover()

        # If we failed to reset and halt, we're probably not going to be able
        # to use Secure AHB-AP functionality
        except Exception as ex:
            print("Secure debugger functionality likely not available:")
            print("{}".format(ex))

            ahb.setSecureState(secure = False)

        chunks = []

        for file in files:
            # Get the file's HEX info and contents
            hex = IntelHex(file)

            # For each segment of data
            for segment in hex.segments():
                # Get the binary data
                data = hex.tobinarray(start = segment[0], end = segment[1])

                # Make sure there are full words to be flashed
                padLength = 4 - (len(data) % 4)

                for i in range(padLength):
                    data.append(0xFF)

                # Chunk the data further into collections of page data
                chunks.append(Flash.Chunk(start = segment[0], data = data))

        # Write the chunks out
        Flash.writeChunks(ahb = ahb, chunks = chunks)

        # Try to reboot the device now that it should be programmed
        try:
            print("Resetting and running device...")

            ahb.dap.api.sys_reset()
            ahb.dap.api.go()

        # If we fail for some reason, meh, ignore that
        #
        # It's likely just from being Non-Secure anyway.
        except Exception as ex:
            pass
