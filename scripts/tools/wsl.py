###
 # \file
 #
 # \brief Handles WSL
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import platform
import subprocess
import sys

class Wsl:
    @staticmethod
    def isWsl():
        """Gets if the current environment is WSL

        :param none:

        :return True:
            This is WSL
        :return False:
            This is not WSL
        """

        # Get where we're running
        environment = platform.platform()

        # If both 'Microsoft' and 'Linux' are in the environment, this is the
        # Frankenstein's monster that is Windows Subsystem for Linux
        if ("Microsoft" in environment) and ("Linux" in environment):
            return True

        # We must be running under either Windows or Linux like a normal person
        return False

    @staticmethod
    def convertPath(path):
        """Converts a WSL path to a Windows path

        :param path:
            The path to convert

        :return String:
            The converted path
        """

        # Attempt to run 'wslpath' in the path
        try:
            output = subprocess.check_output(
                ["wslpath", "-w", path],
                stderr = subprocess.DEVNULL
            ).decode().strip()

            return output

        # If something goes wrong, just defer to the original argument
        except subprocess.CalledProcessError:
            return path

    @staticmethod
    def forward():
        # We'll always elevate this to PowerShell
        command = ["PowerShell.exe"]

        oldArgs = sys.argv

        # If this looks like it's being called with the 'west' command, we can
        # run that directly, making the assumption that it's in PowerShell's
        # (Windows') path
        if (len(oldArgs) > 0) and ("west" in oldArgs[0]):
            command += ["west"]
            oldArgs = oldArgs[1:]

        # Else, we're probably being run in a more native Python manner, so
        # make sure we reinvoke Python
        else:
            command += ["python"]

        args = []

        for arg in oldArgs:
            args.append(Wsl.convertPath(path = arg))

        subprocess.call(command + args)
