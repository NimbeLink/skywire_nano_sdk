"""
Works with Skywire Nano devices

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import logging
import pynrfjprog
import time
import typing

from intelhex import IntelHex

import nimbelink.command as command
import nimbelink.utils as utils

import nl_sdk.commands as commands

class FlashCommand(commands.ProjectCommand):
    """A command for flashing Skywire Nano devices
    """

    def __init__(self) -> None:
        """Creates a new flash command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "flash",
            help = "Flashes Skywire Nano devices",
            singleProject = False,
            resources = [
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.SignedArtifact),
            ]
        )

        self._logger = logging.getLogger(__name__)

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds parser arguments

        :param self:
            Self
        :param parser:
            The parser

        :return none:
        """

        commands.ProjectCommand.addArguments(self, parser = parser)

        parser.add_argument(
            "-e", "--erase",
            action = "count",
            default = 0,
            required = False,
            help = "First perform a mass erase of the device"
        )

        parser.add_argument(
            "-c", "--config",
            required = False,
            help = "A west configuration profile to get a file list from"
        )

        parser.add_argument(
            "files",
            nargs = argparse.REMAINDER,
            help = "HEX file(s) to program the device with"
        )

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs the flash command

        :param self:
            Self
        :param args:
            Our known/expected arguments

        :return int:
            Our result
        """

        result = commands.ProjectCommand.runCommand(self, args = args)

        if result is not None:
            return result

        files = []

        # Add in any specified files
        for file in args.files:
            self.stdout.info(f"Adding file '{file}'")

            files.append(file)

        config = None

        # If they specified a flash configuration project, try to use it
        if args.config is not None:
            config = args.config

            self._logger.info("Config supplied, using it")

        # Else, if no files were supplied, choose between a project and a
        # default configuration
        elif len(files) < 1:
            # Try to use our standard project signed app image(s)
            for project in args.projects:
                files.append(project.signedArtifact)

                self.stdout.info(f"Adding '{project.name}' signed firmware image '{project.signedArtifact}'")

            # If we didn't find anything, try use the default configuration
            if len(files) < 1:
                config = "default"

                self._logger.info("No configuration but no files, attempting to find 'default'")

        # Else, nothing to find
        else:
            self._logger.info("No configuration but have files, not bothering finding 'default'")

        # If we're looking for a configuration, do so
        if config is not None:
            self._logger.info(f"Searching for config '{config}'")

            # Assume the configuration won't be found anywhere
            configFiles = []

            # First try to see if this configuration is available for the
            # project(s)
            for project in args.projects:
                # If this project has a 'flash' configuration for its namespace
                # and that flash configuration has the profile we're looking
                # for, use it
                if ((project.name in project.configuration) and
                    ("flash" in project.configuration[project.name]) and
                    (config in project.configuration[project.name]["flash"])
                ):
                    configFiles.extend(project.configuration[project.name]["flash"][config].split(";"))

                    self.stdout.info(f"Found flash config '{config}' in project '{project.name}'")

            # If we didn't find the project in any of the projects, see if it
            # exists in the 'global' namespace
            if len(configFiles) < 1:
                if (("flash" in args.projects[0].configuration) and
                    (config in args.projects[0].configuration["flash"])
                ):
                    configFiles.extend(args.projects[0].configuration["flash"][config].split(";"))

                    self.stdout.info(f"Found flash config '{config}'")

            # If we *still* didn't find this configuration and they specified
            # it, that's a paddlin'
            #
            # Otherwise, if we didn't auto-find a 'default' one, no worries.
            if (len(configFiles) < 1) and (args.config is not None):
                self.stdout.error(f"Failed to find flash configuration profile '{args.config}'")
                self.stdout.error(f"{project.configuration}'")

                return 1

            elif len(configFiles) > 0:
                for configFile in configFiles:
                    files.append(configFile)

                    self.stdout.info(f"Adding configured file '{configFile}'")

        self.stdout.info("Resetting and halting device...")

        try:
            # First see if we can do a 'system' reset
            #
            # We'll try this first rather than just use the 'debug' reset so
            # that we can suss out early on whether or not we have Secure
            # debugger permission.
            args.nano.tool.dap.api.sys_reset()

            self.stdout.info("Secure debugger permitted")

        except pynrfjprog.APIError.APIError as ex:
            # If this isn't because of 'protection', re-raise it
            if ex.err_code != pynrfjprog.APIError.NrfjprogdllErr.NOT_AVAILABLE_BECAUSE_PROTECTION:
                raise ex

            self.stdout.info("Secure debugger not permitted")

            # If they are going to try to do an erase, let them know now that it
            # won't work
            if args.erase > 0:
                self.stdout.error("Erase not available without Secure debugger")

                return 1

            # That failed due to 'protection', so set our Secure/Non-Secure
            # state to only do Non-Secure stuff
            args.nano.tool.ahb.setSecureState(secure = False)

            # Do a Non-Secure-permitted 'debug' reset
            args.nano.tool.dap.api.debug_reset()

        # Try to halt the core
        #
        # The halt operation appears to be the most unreliable operation, likely
        # because of needing a Non-Secure core context to perform the action.
        # So, give it a few tries.
        #
        # Note that we will not consider it a complete failure if we don't halt
        # the core, as it's still entirely possible to flash Non-Secure firmware
        # without the core being halted. We really only care about halting the
        # core if it's going to be actively running Non-Secure code while we do
        # the flashing.
        for i in range(10):
            try:
                args.nano.tool.dap.api.halt()
                break

            except pynrfjprog.APIError.APIError as ex:
                # If this isn't because of the DLL error, re-raise it
                if ex.err_code != pynrfjprog.APIError.NrfjprogdllErr.JLINKARM_DLL_ERROR:
                    raise ex

                # Wait a little bit before trying again
                time.sleep(1.0)

        if not args.nano.tool.dap.api.is_halted():
            self.stdout.warning("Failed to halt core; continuing anyway")

        # If they want an erase, do that first
        #
        # We expect this to work, since we validated if it's available above, so
        # don't bother catching any exceptions.
        if args.erase > 0:
            self.stdout.info("Mass erasing device...")

            args.nano.tool.dap.api.recover()

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
                chunks.append(utils.Flash.Chunk(start = segment[0], data = data))

        self.stdout.info("Flashing all contents...")

        # Write the chunks out
        utils.Flash.writeChunks(ahb = args.nano.tool.ahb, chunks = chunks)

        self.stdout.info("Flash done!")

        self.stdout.info("Resetting and running device...")

        # Reboot and run the device now that it should be programmed
        args.nano.tool.dap.api.debug_reset()
        args.nano.tool.dap.api.go()

        return 0
