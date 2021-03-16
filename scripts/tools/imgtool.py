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

import diskcache
import os
import sys

from functools import lru_cache
from pathlib import Path

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
    except OSError:
        raise ImportError("Failed to get our script's directory!")

    try:
        # Get our local cache
        cache = diskcache.Cache(os.path.join(ourPath, ".cache"))

        # If the imgtool script is cached and still exists, keep using it
        if ("imgtoolPath" in cache) and os.path.exists(cache["imgtoolPath"]):
            return cache["imgtoolPath"]

    except OSError:
        cache = None

    try:
        # We'll be looking for the imgtool script provided by MCUBoot
        scriptPath = "mcuboot/scripts/imgtool.py"

        # We'll start one directory up the first go-round
        nextPath = ""

        # Hop up out of our scripts/ and project directories and into MCUBoot,
        # accounting for a few nestings of directories
        #
        # We'll do this to try and find what it likely to be the most relevant
        # MCUBoot repository, in the event there are more. Additionally,
        # hopefully it'll cut down on time spent searching if we incrementally
        # do wider searches rather than potentially searching through an entire
        # file system, say.
        for i in range(5):
            try:
                # Hop up one more directory for the script's relative path
                nextPath = os.path.join("../", nextPath)

                # Try to find the file by doing a recursive search
                results = list(Path(nextPath).rglob(scriptPath))

                # If that's the ticket, move on
                if len(results) > 0:
                    # Note that the actual object isn't a string, so we'll need
                    # to get the string representation of the path
                    theirPath = "{}".format(results[0].absolute())
                    break

                # In the event this is the last iteration, make sure this is a
                # failure
                theirPath = None

            except OSError:
                theirPath = None

        # If we failed to find an existing directory, complain
        if theirPath == None:
            raise OSError()

        # If the file doesn't exist, complain
        if not os.path.exists(theirPath):
            raise OSError()

        # We only care about the path to the file itself, so drop the file's
        # name
        theirPath = os.path.dirname(theirPath)

        # If we made our cache earlier
        if cache != None:
            # We found the thing we want, so first cache it to (hopefully) speed
            # this up next time
            cache["imgtoolPath"] = theirPath

        return theirPath

    except OSError:
        raise ImportError("Failed to find imgtool.py at '{}'!".format(theirPath))

# Get imgtool.py and include its path for importing
sys.path.insert(1, __getImgtoolPath())

# Now include the script's entry as 'imgtool'
import imgtool.main as imgtool
