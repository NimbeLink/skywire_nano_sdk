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

from commands.skywire import SkywireCommand
from tools.dfu import Dfu
from tools.imgtool import imgtool

class SkywireDfuCommand(SkywireCommand):
    """A command for generating DFU-capable images
    """

    def __init__(self, *args, **kwargs):
        """Creates a new DFU command

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
            name = "dfu",
            help = "generates a Skywire Nano DFU-able image",
            about = [
                "This tool will generate a firmware binary capable of DFU."
            ]
        )

    def addArguments(self, parser):
        """Adds our arguments to a parser

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        parser.add_argument(
            "-f", "--firmware-file",
            dest = "firmwareFile",
            action = "store",
            required = False,
            metavar = "FILE",
            help = "Input firmware file name"
        )

        parser.add_argument(
            "-t", "--firmware-type",
            type = lambda x: int(x, 0),
            dest = "firmwareType",
            action = "store",
            default = Dfu.Type.Widget,
            required = False,
            metavar = "TYPE",
            help = "Input firmware type"
        )

        parser.add_argument(
            "-s", "--signing-key",
            dest = "signingKey",
            action = "store",
            required = False,
            metavar = "KEYFILE",
            help = "Input signing key file name"
        )

        parser.add_argument(
            "-e", "--encryption-key",
            dest = "encryptionKey",
            action = "store",
            required = False,
            metavar = "KEYFILE",
            help = "Input encryption key file name"
        )

        parser.add_argument(
            "-o", "--output-file",
            dest = "outputFile",
            action = "store",
            required = True,
            metavar = "FILE",
            help = "Output file name"
        )

    def runCommand(self, args, unknownArgs):
        """Runs the DFU generation script

        :param self:
            Self
        :param args:
            Our arguments
        :param unknownArgs:
            Unknown arguments

        :return none:
        """

        # If they specified a firmware image, generate a DFU-able image
        if args.firmwareFile != None:
            Dfu.generateBinary(
                file = args.firmwareFile,
                type = args.firmwareType,
                outputFile = args.outputFile
            )

        # Else, if they specified a signing key, extract the key's raw binary
        # contents
        #
        # Keys do not need to have the firmware DFU header information
        # attached. The Nano will auto-detect that a key is being sent.
        elif args.signingKey != None:
            key = imgtool.load_key(keyfile = args.signingKey)
            keyBytes = key.get_public_bytes()

            with open(args.outputFile, "w+b") as binaryFile:
                binaryFile.write(bytearray(keyBytes))

        # Else, if they specified an encryption key, extract the key's raw
        # binary contents
        elif args.encryptionKey != None:
            key = imgtool.load_key(keyfile = args.encryptionKey)
            keyBytes = key.get_private_bytes(minimal = False)

            with open(args.outputFile, "w+b") as binaryFile:
                binaryFile.write(bytearray(keyBytes))
