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

import tempfile

from commands.command import Command
from tools.dfu import Dfu
from tools.imgtool import imgtool

class FormatCommand(Command):
    """A command for generating DFU-capable images
    """

    FriendlyTypes = {
        "stack":        Dfu.Type.Stack,
        "application":  Dfu.Type.Application,
        "signkey":      Dfu.Type.Key,
        "enckey":       Dfu.Type.Key,
        "partition":    Dfu.Type.Partition,
        "modem":        Dfu.Type.Modem,
    }
    """Strings for a friendlier representation of the DFU-able types"""

    def __init__(self):
        """Creates a new DFU command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "format",
            help = "generates a Skywire Nano DFU-able image",
            description = [
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
            "-i", "--input",
            dest = "input",
            action = "store",
            required = True,
            metavar = "FILE",
            help = "Input file name; or partition data: aStart;aSize;bStart;bSize"
        )

        parser.add_argument(
            "-t", "--type",
            dest = "type",
            action = "store",
            choices = FormatCommand.FriendlyTypes,
            required = True,
            metavar = "TYPE",
            help = "Input file type"
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
        """Runs the format command

        :param self:
            Self
        :param args:
            Our arguments
        :param unknownArgs:
            Unknown arguments

        :return none:
        """

        # If they specified a signing key, extract the key's raw binary
        # contents
        if args.type == "signkey":
            key = imgtool.load_key(keyfile = args.input)
            keyBytes = key.get_public_bytes()

            with tempfile.NamedTemporaryFile(mode = "w+b") as keyFile:
                keyFile.write(bytearray(keyBytes))
                keyFile.flush()

                Dfu.generateBinary(
                    file = keyFile.name,
                    type = FormatCommand.FriendlyTypes[args.type],
                    outputFile = args.outputFile
                )

        # Else, if they specified an encryption key, extract the key's raw
        # binary contents
        elif args.type == "enckey":
            key = imgtool.load_key(keyfile = args.input)
            keyBytes = key.get_private_bytes(minimal = False)

            with tempfile.NamedTemporaryFile(mode = "w+b") as keyFile:
                keyFile.write(bytearray(keyBytes))
                keyFile.flush()

                Dfu.generateBinary(
                    file = keyFile.name,
                    type = FormatCommand.FriendlyTypes[args.type],
                    outputFile = args.outputFile
                )

        # Else, if they specified a partition layout, make a file with them
        elif args.type == "partition":
            values = [int(value) for value in args.input.split(";")]

            if len(values) != 4:
                print("Must have all four fields for partitions!")
                return

            with tempfile.NamedTemporaryFile(mode = "w+b") as partitionFile:
                for value in values:
                    partitionFile.write(
                        value.to_bytes(
                            length = 4,
                            byteorder = "little",
                            signed = False
                        )
                    )

                partitionFile.flush()

                Dfu.generateBinary(
                    file = partitionFile.name,
                    type = FormatCommand.FriendlyTypes[args.type],
                    outputFile = args.outputFile
                )

        # Else, just use their input file directly
        else:
            Dfu.generateBinary(
                file = args.input,
                type = FormatCommand.FriendlyTypes[args.type],
                outputFile = args.outputFile
            )
