"""
Signs Skywire Nano firmware

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import typing

from imgtool.main import imgtool

import nl_sdk.commands as commands

class SignCommand(commands.ProjectCommand):
    """Signs or encrypts Skywire Nano firmware
    """

    def __init__(self) -> None:
        """Creates a new sign command

        :param self:
            Self

        :return none:
        """

        super().__init__(
            name = "sign",
            help = "Signs and encrypts Skywire Nano firmware",
            description =
                """This will generate a signed copy of Skywire Nano firmware,
                and will optionally encrypt the firmware image as well.

                The Skywire Nano MCUBoot boot loader requires header information
                in firmware images, which get added during the
                signing/encrypting process. This information is found in a
                firmware project's configuration and will be automatically
                detected, but can be provided to the command manually.

                If the output file is not specified, a HEX image will be
                generated in the current directory when signing, and an
                additional BIN image will be generated when encrypting.

                If more than one project is specified, their names will
                automatically be added to the output file name(s).

                To avoid having to include the signing/encrypting key paths each
                time, the 'west' configurations for projects and keys can be
                used instead. Refer to this command's parent's help text for
                more information on the available configurations and how to use
                them. """,
            singleProject = False,
            resources = [
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.SignKey, singleValue = True),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.EncryptKey, singleValue = True),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.Kconfig),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.BuildArtifact),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.SignedArtifact),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.UpdateArtifact),
                commands.ProjectCommand.Resource(commands.ProjectCommand.Resource.Type.Version),
            ]
        )

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

        for project in args.projects:
            self.stdout.info("")
            self.stdout.info(f"Signing firmware for project '{project}'")

            # If they don't have at least one key, that's a paddlin'
            if len(project.signKeys) < 1:
                self.stdout.error("No signing keys specified")
                return 1

            # If the version isn't specified, that's a paddlin'
            if project.version is None:
                self.stdout.error("Firmware version not found")
                return 1

            for output in [project.signedArtifact, project.updateArtifact]:
                self.stdout.info(f"Generating '{output}'")

                # Put together our command
                command = [
                    "sign",
                    "--key",            project.signKeys[0].fileName,
                    "--header-size",    project.kconfig["ROM_START_OFFSET"],
                    "--align",          project.kconfig["DT_FLASH_WRITE_BLOCK_SIZE"],
                    "--slot-size",      project.kconfig["FLASH_LOAD_SIZE"],
                    "--load-addr",      project.kconfig["FLASH_LOAD_OFFSET"],
                    "--version",        project.version
                ]

                # If we're encrypting a binary image, add that argument
                if output.lower().endswith(".bin") and (len(project.encryptKeys) > 0):
                    self.stdout.info("    Encrypting image")

                    command += ["--encrypt", project.encryptKeys[0].fileName]

                # If we're generating a binary -- that is, not a HEX output --
                # make sure we also pad the image
                if not output.lower().endswith(".hex"):
                    self.stdout.info("    Padding non-HEX output image")

                    command += ["--pad"]

                # If we have a version dependency, add it
                if "STACK_ABI_VERSION" in project.kconfig:
                    dependency = project.kconfig["STACK_ABI_VERSION"]

                    self.stdout.info(f"    Adding version dependency for '{dependency}'")

                    command += ["--dependencies", f"(0,{dependency})"]

                # Add our input and output files
                command += [project.buildArtifact, output]

                # Run our command
                try:
                    imgtool.main(command)

                except SystemExit as ex:
                    if ex.code != 0:
                        self.stdout.exception(ex)

                        return 1

                self.stdout.info("Generated!")

        return 0
