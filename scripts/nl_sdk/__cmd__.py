"""
The main entry point for the SDK commands

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import os
import typing

import nimbelink.command as command
import nimbelink.config as config

command.WestCommand.setupImports(__file__, "../")

import nl_sdk.commands as commands

class SdkCommand(command.RootCommand, command.WestCommand):
    """Our NimbeLink SDK command
    """

    def __init__(self) -> None:
        """Creates a new NimbeLink SDK command

        :param self:
            Self

        :return none:
        """

        rootSingleSignConfig = config.Config()
        rootSingleSignConfig.add(config.WestBackend())
        rootSingleSignConfig.add(config.Config("keys"))
        rootSingleSignConfig["keys"].add(config.Option("sign", "../rel/key/path/sign.pem"))

        rootSingleEncryptConfig = config.Config()
        rootSingleEncryptConfig.add(config.WestBackend())
        rootSingleEncryptConfig.add(config.Config("keys"))
        rootSingleEncryptConfig["keys"].add(config.Option("encrypt", "/abs/key/path/encrypt.pem"))

        rootMultipleSignConfig = config.Config()
        rootMultipleSignConfig.add(config.WestBackend())
        rootMultipleSignConfig.add(config.Config("keys"))
        rootMultipleSignConfig["keys"].add(config.Option("sign", "key/path/sign_1.pem;key/path/sign_2.pem"))

        rootSingleSignGlobConfig = config.Config()
        rootSingleSignGlobConfig.add(config.WestBackend())
        rootSingleSignGlobConfig.add(config.Config("keys"))
        rootSingleSignGlobConfig["keys"].add(config.Option("sign", "key/path/sign*.pem;key/differentpath/sign*.pem"))

        singleProjectConfig = config.Config()
        singleProjectConfig.add(config.WestBackend())
        singleProjectConfig.add(config.Option("projects", "myproject"))

        multipleProjectConfig = config.Config()
        multipleProjectConfig.add(config.WestBackend())
        multipleProjectConfig.add(config.Option("projects", "project1;project2"))

        projectMultipleSignGlobConfig = config.Config()
        projectMultipleSignGlobConfig.add(config.WestBackend())
        projectMultipleSignGlobConfig.add(config.Config("project1"))
        projectMultipleSignGlobConfig["project1"].add(config.Config("keys"))
        projectMultipleSignGlobConfig["project1"]["keys"].add(config.Option("sign", "key/path/sign.pem"))

        projectSingleEncryptConfig = config.Config()
        projectSingleEncryptConfig.add(config.WestBackend())
        projectSingleEncryptConfig.add(config.Config("project2"))
        projectSingleEncryptConfig["project2"].add(config.Config("keys"))
        projectSingleEncryptConfig["project2"]["keys"].add(config.Option("sign", "key/path/sign.pem"))

        multiFlashConfig = config.Config()
        multiFlashConfig.add(config.Config(name = "flash"))
        multiFlashConfig["flash"].add(config.Option(name = "default", value = "app.hex;data.hex;settings.hex"))

        singleFlashConfig = config.Config()
        singleFlashConfig.add(config.Config(name = "flash"))
        singleFlashConfig["flash"].add(config.Option(name = "app", value = "app.hex"))

        super().__init__(
            name = "nano",
            help = "Provides SDK functionality",
            description =
                f"""The SDK command provides sub-commands for working with
                application firmware and devices.

                The application firmware commands provide post-processing
                functions to prepare built application firmware images for
                uploading to a Skywire Nano device.

                The device commands provide various tools for working with a
                Skywire Nano device, including first-time setup and continuous
                firmware deployment.

                Some commands will require your software project's files. These
                files are your signing and optional encrypting keys, Kconfig,
                Devicetree, and firmware build output files. Your keys should
                only be generated once, and the additional files are all
                generated after running 'west build' at least once.

                Commands that require some or all of these files will provide
                arguments for manually specifying the target files, but will
                also allow automatically detecting the files.

                Your key location(s) are unique to your software project, and
                will need to be configured at least once using 'west config'
                (see 'west config --help' for usage information). The keys can
                be specified using absolute or relative paths. Relative paths
                will be used against the current directory a command is run out
                of. The key file names can be exact file names or GLOB patterns.
                Multiple keys can be matched with a single GLOB pattern.
                Multiple key names and/or GLOB patterns can be specified in the
                same configuration with a ';' separating each entry. Some
                examples of key configurations:

                    {rootSingleSignConfig}

                    {rootSingleEncryptConfig}

                    {rootMultipleSignConfig}

                    {rootSingleSignGlobConfig}

                In most cases, the remaining project files will use the default
                Zephyr project output paths, and no configuration will be
                needed. If, however, you are using a project with a manual
                setup, some additional configuration might be needed.

                If you are changing the name of the project and the build output
                directory contains the project's name (e.g.
                'build/myproject/zephyr/'), you will need to configure the name
                of the project:

                    {singleProjectConfig}

                Single-project environments can still use the key configurations
                listed above.

                If you are building multiple projects at once, you will need to
                configure the name of each project:

                    {multipleProjectConfig}

                You will also need to configure each project's keys using an
                additional scope in the configuration:

                    {projectMultipleSignGlobConfig}

                    {projectSingleEncryptConfig}

                Once your project is building and your keys are generated and
                configured, you can perform the one-time 'initialization' of
                your Skywire Nano device. This will 'convert' it and upload your
                keys and any relevant application configurations:

                    west nano device initialize

                Reboot your device at least once after initialization.

                When you are ready to update the Skywire Nano application with
                your firmware, first sign and optionally encrypt the image

                    west nano app sign

                You can now upload the firmware image to your device:

                    west nano device -x "<port>" update

                """,
            subCommands = [
                commands.app.Command(),
                commands.device.Command()
            ]
        )
