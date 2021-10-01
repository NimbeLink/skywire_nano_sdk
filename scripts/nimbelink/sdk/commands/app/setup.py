"""
Sets up a Skywire Nano project

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import logging
import os
import typing

from imgtool.main import imgtool

import nimbelink.config as config

import nimbelink.sdk as sdk
import nimbelink.sdk.commands as commands

class SetupCommand(commands.ProjectCommand):
    """Sets up a Skywire Nano project

    This will generate signing and encrypting keys for a Skywire Nano project
    and configure local settings for accessing them automatically from other
    NimbeLink SDK commands. You can view all local settings using:

        'west config -l'

    By default, the signing key will be named 'sign.pem', and the encrypting key
    will be named 'encrypt.pem'. If different names are desired, they can be
    specified manually.

    If keys are specified using arguments and their target file already exists,
    this command will assume the keys have been generated and will only create
    configurations for them.
    """

    def __init__(self) -> None:
        """Creates a new setup command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            singleProject = True,
            resources = [
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.SignKey),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.EncryptKey),
            ]
        )

        self._logger = logging.getLogger(__name__)

    def runCommand(self, args: typing.List[object]) -> int:
        """Runs our command

        :param self:
            Self
        :param args:
            Our arguments

        :return int:
            Our result
        """

        result = commands.ProjectCommand.runCommand(self, args = args)

        if result is not None:
            return result

        # If they didn't specify any keys, add our default signing and encrypting keys
        if len(args.projects[0].keys) < 1:
            args.projects[0].keys.append(sdk.Project.Key(type = sdk.Project.Key.Type.Sign, fileName = "sign.pem"))
            args.projects[0].keys.append(sdk.Project.Key(type = sdk.Project.Key.Type.Encrypt, fileName = "encrypt.pem"))

            self.stdout.info("Using default signing and encrypting keys 'sign.pem' and 'encrypt.pem'")

        for key in args.projects[0].keys:
            # If this key already exists, nothing to do
            if os.path.exists(key.fileName):
                self.stdout.info(f"Key '{key.fileName}' exists, not generating it")
                continue

            self.stdout.info(f"Generating key '{key.fileName}'")

            # Try to generate the key
            try:
                imgtool.main(["keygen", "-k", key.fileName, "-t", "rsa-2048"])

            except SystemExit as ex:
                if ex.code != 0:
                    self.stdout.exception(ex)

                    return 1

            self.stdout.info("Generated!")

        # Start at the top-level configuration
        configuration = args.projects[0].configuration

        # If this project is not a default one, make sure we use a
        # project-specific sub-configuration
        if not args.projects[0].isDefault:
            configuration.add(config.Config(name = args.projects[0].name))

            configuration = configuration[args.projects[0].name]

            self._logger.info(f"Using project-specific key namespace")

        # Make sure the 'key' sub-configuration exists
        if "keys" not in configuration:
            configuration.add(config.Config(name = "keys"))

            self._logger.info("Added 'keys' sub-configuration")

        # Go into the 'keys' sub-configuration
        configuration = configuration["keys"]

        # Make sure we start our key configurations anew
        if "sign" in configuration:
            del configuration["sign"]

        if "encrypt" in configuration:
            del configuration["encrypt"]

        # Generate configuration values for our collections of keys
        signKeyNames = ";".join([key.fileName for key in args.projects[0].signKeys])
        encryptKeyNames = ";".join([key.fileName for key in args.projects[0].encryptKeys])

        # If we have signing keys, add a configuration for them
        if signKeyNames != "":
            configuration.add(config.Option("sign", signKeyNames))

            self._logger.info(f"Added 'sign' configuration '{signKeyNames}'")

        # If we have encrypting keys, add a configuration for them
        if encryptKeyNames != "":
            configuration.add(config.Option("encrypt", encryptKeyNames))

            self._logger.info(f"Added 'encrypt' configuration '{encryptKeyNames}'")

        # Save the configurations
        args.projects[0].configuration.save()

        self.stdout.info("Configuration saved!")

        return 0
