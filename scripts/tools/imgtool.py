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

        # Hop up our of our scripts/ and project directories and into MCUBoot
        theirPath = os.path.join(ourPath, "../../../mcuboot/scripts")

        # Get the Python script's path
        imgtoolFile = os.path.join(theirPath, "imgtool.py")

        # If the file doesn't exist, complain
        if not os.path.exists(imgtoolFile):
            raise OSError()

        return theirPath

    except OSError:
        raise Exception("Failed to find imgtool.py at '{}'!".format(theirPath))

# Get imgtool.py and include its path for importing
sys.path.insert(1, __getImgtoolPath())

# Now include the script's entry as 'imgtool'
import imgtool.main as imgtool
