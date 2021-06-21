###
 # \file
 #
 # \brief Provides DFU utilities for the Skywire Nano
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
import struct

from tools.imgtool import imgtool

class Dfu:
    HeaderSize = 64
    """How large headers are"""

    class Type:
        """A target image that can be updated via DFU
        """

        Stack       = 0
        Application = 1
        Modem       = 2
        Key         = 3
        Partition   = 4

        @staticmethod
        def validate(type):
            """Validates a type

            :param type:
                The type to validate

            :return True:
                Type is valid
            :return False:
                Type is invalid
            """

            types = [
                Dfu.Type.Stack,
                Dfu.Type.Application,
                Dfu.Type.Modem,
                Dfu.Type.Key,
                Dfu.Type.Partition,
            ]

            if type not in types:
                return False

            return True

    @staticmethod
    def generateBinary(
        file,
        type,
        outputFile
    ):
        """Adds a header to a binary file meant for DFU

        :param file:
            The binary file to add a header to
        :param type:
            The type of file this is
        :param outputFile:
            The output binary file to write to

        :return none:
        """

        # Get the file's raw binary data
        with open(file, "rb") as openFile:
            rawData = openFile.read()

        # Add magic
        headerData = struct.pack("I", 0xecce1347)

        # Add the type
        headerData += struct.pack("I", type)

        # Add the length
        headerData += struct.pack("I", len(rawData))

        # Get how much header space we have left to generate
        padWords = int((Dfu.HeaderSize - len(headerData)) / 4)

        # Pad the rest of the header
        for i in range(padWords):
            headerData += struct.pack("I", 0)

        # Write out the contents
        #
        # We'll do this after pulling the file's contents in the event the
        # caller wants the output file to replace the input file.
        with open(outputFile, "wb") as output:
            output.write(headerData)
            output.write(rawData)
