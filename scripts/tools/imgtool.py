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
import subprocess
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

        # Get our local cache using Python's cache directory
        cache = diskcache.Cache(os.path.join(ourPath, "__pycache__"))

        # If the imgtool script is cached and still exists, keep using it
        if ("imgtoolPath" in cache) and os.path.exists(cache["imgtoolPath"]):
            return cache["imgtoolPath"]

    except OSError:
        cache = None

    # Let the user know we're hunting for imgtool.py
    print("Doing one-time find for imgtool.py...")

    try:
        # Use 'west' to find our top-level directory
        topLevelPath = subprocess.check_output(["west", "topdir"]).decode().strip()

    except subprocess.CalledProcessError:
        raise ImportError("Failed to find top-level directory!")

    # We'll be looking for the imgtool script provided by MCUBoot
    scriptPath = os.path.join("scripts", "imgtool.py")

    # Try to find the file by doing a recursive search
    results = list(Path(topLevelPath).rglob(scriptPath))

    # If we failed to find an existing directory, complain
    if len(results) < 0:
        raise ImportError("Failed to find imgtool.py!")

    # Note that the actual object isn't a string, so we'll need to get the
    # string representation of the path
    imgtoolPath = "{}".format(results[0].absolute())

    # We only care about the path to the file itself, so drop the file's name
    imgtoolPath = os.path.dirname(imgtoolPath)

    # If the file doesn't exist, complain
    if not os.path.exists(imgtoolPath):
        raise ImportError("Failed to find imgtool.py!")

    # If we made our cache earlier
    if cache != None:
        # We found the thing we want, so first cache it to (hopefully) speed
        # this up next time
        cache["imgtoolPath"] = imgtoolPath

    return imgtoolPath

# Get imgtool.py and include its path for importing
sys.path.insert(1, __getImgtoolPath())

# Now include the script's entry as 'imgtool'
import imgtool.main as imgtool
