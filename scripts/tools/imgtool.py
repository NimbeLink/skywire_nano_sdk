###
 # \file
 #
 # \brief Provides importing the actual imgtool from MCUBoot
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import os
import sys

def __getImgtoolPath():
    """Gets the imgtool.py location

    :param none:

    :raise Exception:
        imgtool.py not found

    :return String:
        The imgtool.py location
    """

    try:
        # Get this script's directory
        ourPath = os.path.dirname(os.path.realpath(__file__))

        scriptPath = "mcuboot/scripts"

        # Hop up out of our scripts/ and project directories and into MCUBoot,
        # accounting for a few nestings of directories
        for i in range(5):
            try:
                # Hop up one more
                scriptPath = os.path.join("../", scriptPath)

                # Form the full path, relative to us
                theirPath = os.path.join(ourPath, scriptPath)

                # If that's the ticket, move on
                if os.path.exists(theirPath):
                    break

                # In the event this is the last iteration, make sure this is a
                # failure
                theirPath = None

            except OSError:
                theirPath = None

        # If we failed to find an existing directory, complain
        if theirPath == None:
            raise OSError()

        # Get the Python script's path
        imgtoolFile = os.path.join(theirPath, "imgtool.py")

        # If the file doesn't exist, complain
        if not os.path.exists(imgtoolFile):
            raise OSError()

        return theirPath

    except OSError:
        raise ImportError("Failed to find imgtool.py at '{}'!".format(theirPath))

# Get imgtool.py and include its path for importing
sys.path.insert(1, __getImgtoolPath())

# Now include the script's entry as 'imgtool'
import imgtool.main as imgtool
