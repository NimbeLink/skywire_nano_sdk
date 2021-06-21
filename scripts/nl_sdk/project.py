"""
Provides common helpers for working with Skywire Nano projects

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import imgtool.main as imgtool
import logging
import os
import pathlib
import struct
import typing

import nimbelink.config as config
import nimbelink.utils as utils

class Project:
    """Provides common helpers for working with Skywire Nano projects
    """

    class Key:
        """A key used with the application
        """

        class Type:
            """The types of keys available
            """

            Sign    = 1
            Encrypt = 2

        def __init__(
            self,
            type: "Project.Key.Type",
            fileName: str = None,
            data: bytearray = None
        ) -> None:
            """Creates a new project key

            :param self:
                Self
            :param type:
                The type of key this is
            :param fileName:
                This key's file
            :param data:
                The data of this key

            :return none:
            """

            self.type = type
            self.fileName = fileName
            self._data = data

        def __str__(self) -> str:
            """Gets a string representation of us

            :param self:
                Self

            :return str:
                Us
            """

            return f"{self.fileName}"

        @property
        def data(self) -> bytearray:
            """Gets this key's data

            :param self:
                Self

            :raise ValueError:
                Invalid key type

            :return bytearray:
                This key's data
            """

            # If we haven't gotten our data yet, do so
            if self._data is None:
                key = imgtool.load_key(keyfile = self.fileName)

                if self.type == Project.Key.Type.Sign:
                    self._data = key.get_public_bytes()

                elif self.type == Project.Key.Type.Encrypt:
                    self._data = key.get_private_bytes(minimal = False)

                else:
                    raise ValueError(f"Invalid key type '{self.type}'")

            return self._data

    class Partitions:
        """Partitions for a project's app
        """

        @staticmethod
        def makeFromString(string: str) -> "Project.Partitions":
            """Makes a set of partitions from a formatted string

            :param string:
                The string to parse

            :raise ValueError:
                Failed to parse string

            :return Project.Partitions:
                The parsed set of partitions
            """

            values = [int(value) for value in args.input.split(";")]

            if len(values) != 4:
                raise ValueError(f"Failed to parse partitions in '{string}'")

            return Project.Partitions(
                aStart = values[0],
                aSize = values[1],
                bStart = values[2],
                bSize = values[3]
            )

        def __init__(self, aStart: int, aSize: int, bStart: int, bSize: int) -> None:
            """Creates a new set of partitions

            :param self:
                Self
            :param aStart:
                A image start address
            :param aSize:
                A image size
            :param bStart:
                B image start address
            :param bSize:
                B image size

            :return none:
            """

            self.aStart = aStart
            self.aSize = aSize
            self.bStart = bStart
            self.bSize = bSize

        def __str__(self) -> str:
            """Gets a string representation of us

            :param self:
                Self

            :return str:
                Us
            """

            return f"{self.aStart}:{self.aSize};{self.bStart}:{self.bSize}"

        @property
        def data(self) -> bytearray:
            """Gets the partition values

            :param self:
                Self

            :return bytearray:
                Our partition values
            """

            return                                  \
                struct.pack("I", self.aStart)   +   \
                struct.pack("I", self.aSize)    +   \
                struct.pack("I", self.bStart)   +   \
                struct.pack("I", self.bSize)

    ConfigNames = {
        Key.Type.Sign:      "sign",
        Key.Type.Encrypt:   "encrypt"
    }
    """The configuration names we'll use for each key type"""

    BuildArtifact = "zephyr.hex"
    """The build artifact for an app"""

    SignedArtifact = "app_signed.hex"
    """The signed and unencrypted artifact for an app"""

    UpdateArtifact = "app_update.bin"
    """The signed and optionally encrypted update file for an app"""

    @staticmethod
    def getNames() -> typing.List[str]:
        """Gets all of the configured project names

        If no projects are configured, the default setup will be specified in
        the return value as a single empty string in the array.

        :param none:

        :return typing.List[str]:
            The configured project names
        """

        logger = logging.getLogger(__name__)

        # Get the root configuration, add our 'west' backend, and load it
        configuration = config.Config()
        configuration.add(config.WestBackend())

        try:
            configuration.load(allowCreate = True)
        except OSError:
            pass

        projectNames = []

        # If projects are configured, make instances for them
        if "projects" in configuration:
            for projectName in configuration["projects"].split(";"):
                logger.info(f"Found configured project '{projectName}'")

                projectNames.append(projectName)

        # If there weren't any configured projects, just assume the default
        # single project setup
        if len(projectNames) < 1:
            projectNames.append("")

        return projectNames

    def __init__(
        self,
        name: str = None,
        directory: str = None,
        buildDirectory: str = None,
        keys: typing.List["Project.Key"] = None,
        kconfig: utils.Kconfig = None,
        devicetree: utils.Devicetree = None,
        buildArtifact: str = None,
        signedArtifact: str = None,
        updateArtifact: str = None,
        version: str = None,
        partitions: "Project.Partitions" = None,
        configuration: config.Config = None
    ) -> None:
        """Creates a new Skywire Nano project

        :param self:
            Self
        :param name:
            The name of the project
        :param directory:
            The root directory of the project
        :param buildDirectory:
            The build directory of the project
        :param configuration:
            This project's configuration
        :param keys:
            This project's signing and encrypting keys
        :param kconfig:
            This project's Kconfig
        :param devicetree:
            This project's Devicetree
        :param buildArtifact:
            This project's build artifact
        :param signedArtifact:
            This project's signed artifact
        :param updateArtifact:
            This project's update artifact
        :param version:
            This project's firmware version
        :param partitions:
            This project's application partitions

        :return none:
        """

        # If the name of the project is empty, assume it's intended to be the
        # same meaning as None (which we treat specially)
        if name == "":
            name = None

        # We'll leave the name as None (if it's None), which lets us know we're
        # using the default anonymous setup
        self._name = name

        # Don't bother looking for or loading/parsing anything else until
        # requested if the provided initial values aren't provided
        #
        # If we do look for files, we'll cache whatever we load, but there's no
        # reason to slow down something using a project with parsing, say, a
        # Kconfig file when the user won't use Kconfig information anyway.
        self._directory = directory
        self._buildDirectory = buildDirectory
        self._configuration = configuration
        self._keys = keys
        self._kconfig = kconfig
        self._devicetree = devicetree
        self._buildArtifact = buildArtifact
        self._signedArtifact = signedArtifact
        self._updateArtifact = updateArtifact
        self._version = version
        self._partitions = partitions

        self._logger = logging.getLogger(__name__)

    def __str__(self) -> str:
        """Gets a string representation of us

        :param self:
            Self

        :return str:
            Us
        """

        return self.name

    def _getProjectFile(self, fileName: str) -> str:
        """Finds a file in a build directory

        :param self:
            Self
        :param fileName:
            The name of the file to find

        :raise OSError:
            Failed to find file

        :return str:
            The path to the file
        """

        self._logger.debug(f"Searching for project file '{fileName}'")

        files = sorted(list(pathlib.Path(self.buildDirectory).rglob(fileName)))

        # If there isn't a target in here, that's a paddlin'
        if len(files) < 1:
            raise OSError(f"Failed to find a '{fileName}' project file")

        # If there are more than one, we won't be able to choose
        if len(files) > 1:
            message = f"Failed to find a unique '{fileName}' project file:"

            for file in files:
                message += "\n" + f"    Candidate '{file}'"

            raise OSError(message)

        # Found it, so use it
        #
        # Make sure the file we found is a proper string, which rglob doesn't
        # return.
        file = f"{files[0]}"

        self._logger.info(f"Found '{fileName}' project file at '{file}'")

        return file

    def _getKeys(self, type: "Project.Key.Type") -> typing.List[str]:
        """Gets our keys of a specified type

        Multiple signing keys are usable by a project.

        :param self:
            Self
        :param type:
            The type of keys to get

        :raise OSError:
            Failed to find key(s) for type

        :return typing.List[str]:
            Our keys of the specified type
        """

        # If our project is named, first see if we have project-specific keys
        # configured
        if ((self._name is not None) and
            (self._name in self.configuration) and
            ("keys" in self.configuration[self._name]) and
            (Project.ConfigNames[type] in self.configuration[self._name]["keys"])
        ):
            patterns = self.configuration[self._name]["keys"][Project.ConfigNames[type]].split(";")

        # Else, try to find keys in the project-less configuration namespace
        elif (("keys" in self.configuration) and
            (Project.ConfigNames[type] in self.configuration["keys"])
        ):
            patterns = self.configuration["keys"][Project.ConfigNames[type]].split(";")

        # Else, we must not have keys configured
        else:
            patterns = []

        keys = []

        # The key(s) might be GLOB patterns, so try to resolve the file name(s)
        #
        # If the file's name is specified, this will still result in the file
        # being found.
        for pattern in patterns:
            self._logger.debug(f"Searching for key(s) with '{pattern}'")

            directory = os.path.join(self.directory, os.path.dirname(pattern))
            filePattern = os.path.basename(pattern)

            foundKeys = sorted(list(pathlib.Path(directory).rglob(filePattern)))

            # If there isn't a key, that's a paddlin'
            if len(foundKeys) < 1:
                raise OSError(f"Failed to find a key for '{pattern}'")

            # Make sure each key we found is a proper string, which rglob
            # doesn't return
            for i in range(len(foundKeys)):
                foundKeys[i] = f"{foundKeys[i]}"

                self._logger.info(f"Found a '{Project.ConfigNames[type]}' key '{foundKeys[i]}'")

            keys += foundKeys

        return [Project.Key(type = type, fileName = key) for key in keys]

    def isOutdated(self, artifact):
        """Checks if a build artifact is older than the primary build artifact

        This essentially warns if a signed artifact or an update artifact looks
        out of date relative to the most recent build.

        :param self:
            Self
        :param artifact:
            The artifact to check

        :return True:
            Artifact outdated
        :return False:
            Artifact up-to-date
        """

        # If the file doesn't exist, it obviously can't be outdated
        if not os.path.exists(artifact):
            return False

        # Get the modified times for the build artifact and this one
        buildArtifactTime = pathlib.Path(self.buildArtifact).stat().st_mtime
        artifactTime = pathlib.Path(artifact).stat().st_mtime

        # If this artifact is older than the project's build artifact, it's
        # outdated
        if buildArtifactTime > artifactTime:
            return True

        return False

    @property
    def name(self) -> str:
        """Gets this project's name

        :param self:
            Self

        :return str:
            Our name
        """

        if self._name is None:
            return "app"

        return self._name

    @property
    def isDefault(self) -> bool:
        """Gets if this project is a 'default' setup

        That is, if it doesn't have a non-standard name and layout.

        :param self:
            Self

        :return True:
            We are a default project
        :return False:
            We are a non-standard project
        """

        if self._name is None:
            return True

        return False

    @property
    def directory(self) -> str:
        """Gets this project's root directory path

        :param self:
            Self

        :return str:
            Our root directory
        """

        # If we haven't already gotten our root directory, do it now
        if self._directory is None:
            self._directory = os.getcwd()

            self._logger.debug(f"Assuming project directory is current '{self._directory}'")

        return self._directory

    @property
    def buildDirectory(self) -> str:
        """Gets this project's build directory path

        :param self:
            Self

        :raise OSError:
            Failed to find build directory

        :return str:
            Our build directory
        """

        # If we haven't already gotten our build directory, do it now
        if self._buildDirectory is None:
            buildDirectories = []

            for directory in os.listdir(self.directory):
                # If this doesn't start with 'build', skip it
                if not directory.startswith("build"):
                    continue

                # The directories are listed relative to the path we searched,
                # so recompile the path to it
                #
                # Note that we did this after the check above, since we'll
                # likely be clobbering the beginning part of the string.
                directory = os.path.join(self.directory, directory)

                # If this isn't a directory, skip it
                if not os.path.isdir(directory):
                    continue

                # Found another contender
                buildDirectories.append(directory)

            # If there weren't any build directories, that's a paddlin'
            if len(buildDirectories) < 1:
                raise OSError(f"Failed to find any 'build' directories in '{self.directory}'")

            # If there was more than one, that's a paddlin'
            if len(buildDirectories) > 1:
                raise OSError(f"Failed to find unique 'build' directory in '{buildDirectories}'")

            # Grab the build directory
            self._buildDirectory = buildDirectories[0]

            self._logger.debug(f"Found top-level build directory '{self._buildDirectory}'")

            # If our project has a non-default name, assume it has its own build
            # sub-directory
            if self._name is not None:
                self._buildDirectory = os.path.join(self._buildDirectory, self._name)

                self._logger.debug(f"Adding '{self._name}' project build sub-directory")

            # Add the standard 'zephyr' sub-directory
            self._buildDirectory = os.path.join(self._buildDirectory, "zephyr")

            self._logger.debug(f"Final build directory '{self._buildDirectory}'")

        return self._buildDirectory

    @property
    def configuration(self) -> config.Config:
        """Gets our project's configurations

        :param self:
            Self

        :return config.Config:
            Our project's configuration
        """

        # If we haven't already gotten our configurations, do it now
        if self._configuration is None:
            self._configuration = config.Config()
            self._configuration.add(config.WestBackend())

            self._logger.debug("Loading 'west' configuration")

            try:
                self._configuration.load(allowCreate = True)

            except OSError:
                self._logger.warning("Failed to load west configuration")

        return self._configuration

    @property
    def keys(self) -> typing.List["Project.Key"]:
        """Gets our key(s)

        :param self:
            Self

        :return typing.List[Project.Key]:
            Our key(s)
        """

        # If we haven't already gotten our signing key(s), do it now
        if self._keys is None:
            self._keys =                                            \
                self._getKeys(type = Project.Key.Type.Sign)     +   \
                self._getKeys(type = Project.Key.Type.Encrypt)

        return self._keys

    @property
    def signKeys(self) -> typing.List["Project.Key"]:
        """Gets our signing key(s)

        :param self:
            Self

        :return typing.List[Project.Key]:
            Our signing key(s)
        """

        return [key for key in self.keys if key.type == Project.Key.Type.Sign]

    @property
    def encryptKeys(self) -> typing.List["Project.Key"]:
        """Gets our encrypting key(s)

        :param self:
            Self

        :return typing.List[Project.Key]:
            Our encrypting key(s)
        """

        return [key for key in self.keys if key.type == Project.Key.Type.Encrypt]

    @property
    def kconfig(self) -> utils.Kconfig:
        """Gets this project's Kconfig

        :param self:
            Self

        :raise OSError:
            Failed to find this project's Kconfig

        :return utils.Kconfig:
            This project's Kconfig
        """

        # If we haven't already gotten our Kconfig, do it now
        if self._kconfig is None:
            fileName = self._getProjectFile(fileName = utils.Kconfig.FileName)

            self._kconfig = utils.Kconfig.makeFromConfig(fileName = fileName)

        return self._kconfig

    @property
    def devicetree(self) -> utils.Devicetree:
        """Gets this project's Devicetree

        :param self:
            Self

        :raise OSError:
            Failed to find this project's Devicetree

        :return utils.Devicetree:
            This project's Devicetree
        """

        # If we haven't already gotten our Devicetree, do it now
        if self._devicetree is None:
            fileName = self._getProjectFile(fileName = utils.Devicetree.FileName)

            self._devicetree = utils.Devicetree.makeFromConfig(fileName = fileName)

        return self._devicetree

    @property
    def buildArtifact(self) -> str:
        """Gets this project's build artifact

        :param self:
            Self

        :raise OSError:
            Failed to find this project's build artifact

        :return str:
            The path to this project's build artifact
        """

        # If we haven't already gotten our build artifact's path, do it now
        if self._buildArtifact is None:
            self._logger.debug(f"Assuming default '{Project.BuildArtifact}' build artifact")

            self._buildArtifact = self._getProjectFile(fileName = Project.BuildArtifact)

        return self._buildArtifact

    @property
    def signedArtifact(self) -> str:
        """Gets this project's signed artifact

        :param self:
            Self

        :return str:
            The path to this project's signed artifact
        """

        # If we haven't already gotten our signed artifact's path, do it now
        if self._signedArtifact is None:
            self._logger.debug(f"Assuming default '{Project.SignedArtifact}' signed artifact")

            # Try to find an existing file first
            try:
                self._signedArtifact = self._getProjectFile(fileName = Project.SignedArtifact)

            # If it doesn't exist, assume it'll be next to our build artifact
            except OSError:
                self._logger.debug("Signed artifact not found, assuming in same directory as build artifact")

                self._signedArtifact = os.path.join(
                    os.path.dirname(self.buildArtifact),
                    Project.SignedArtifact
                )

        return self._signedArtifact

    @property
    def updateArtifact(self) -> str:
        """Gets this project's update artifact

        :param self:
            Self

        :return str:
            The path to this project's update artifact
        """

        # If we haven't already gotten our update artifact's path, do it now
        if self._updateArtifact is None:
            self._logger.debug(f"Assuming default '{Project.UpdateArtifact}' update artifact")

            # Try to find an existing file first
            try:
                self._updateArtifact = self._getProjectFile(fileName = Project.UpdateArtifact)

            # If it doesn't exist, assume it'll be next to our build artifact
            except OSError:
                self._logger.debug("Update artifact not found, assuming in same directory as build artifact")

                self._updateArtifact = os.path.join(
                    os.path.dirname(self.buildArtifact),
                    Project.UpdateArtifact
                )

        return self._updateArtifact

    @property
    def version(self) -> str:
        """Gets this project's build version

        :param self:
            Self

        :return None:
            Failed to find this project's version
        :return str:
            Our build version
        """

        # If we haven't already gotten our build version, do it now
        if self._version is None:
            self._logger.debug("Looking up NimbeLink version files with 'NIMBELINK_VERSION_MCUBOOT_FILE' in Kconfig")

            # If the NimbeLink SDK firmware version wasn't used in this
            # firmware, we can't auto-detect it
            if "NIMBELINK_VERSION" not in self.kconfig:
                self._logger.warning("Cannot auto-detect firmware version without 'NIMBELINK_VERSION' in Kconfig")

                return None

            # If the MCUBoot version file name isn't set, that's a paddlin'
            if "NIMBELINK_VERSION_MCUBOOT_FILE" not in self.kconfig:
                self._logger.warning("Could not find MCUBoot version file ('NIMBELINK_VERSION_MCUBOOT_FILE') in Kconfig")

                return None

            versionFileName = self.kconfig["NIMBELINK_VERSION_MCUBOOT_FILE"]

            # Get the MCUBoot firmware version file path
            versionFile = self._getProjectFile(fileName = versionFileName)

            # Use the contents as our version
            self._version = open(versionFile, "r").read().strip()

            self._logger.info(f"Read firmware version '{self._version}'")

        return self._version

    @property
    def partitions(self) -> str:
        """Gets this project's image partitions

        :param self:
            Self

        :return None:
            Failed to find this project's partitions
        :return Project.Partitions:
            This project's partitions
        """

        # If we haven't already gotten our partitions, do it now
        if self._partitions is None:
            self._logger.debug("Looking up partition values with 'DT_FLASH_AREA_IMAGE_0/1_IMAGE/SIZE' in Devicetree")

            # If images 0 and 1 don't have their values, we can't detect
            # partitions
            if (("DT_FLASH_AREA_IMAGE_0_OFFSET" not in self.devicetree) or
                ("DT_FLASH_AREA_IMAGE_0_SIZE" not in self.devicetree) or
                ("DT_FLASH_AREA_IMAGE_1_OFFSET" not in self.devicetree) or
                ("DT_FLASH_AREA_IMAGE_1_SIZE" not in self.devicetree)
            ):
                self._logger.warning("Cannot auto-detect partitions without 'DT_FLASH_AREA_IMAGE_0/1_IMAGE/SIZE' in Devicetree")

                return None

            # Compile our partitions
            self._partitions = Project.Partitions(
                aStart = self.devicetree["DT_FLASH_AREA_IMAGE_0_OFFSET"],
                aSize = self.devicetree["DT_FLASH_AREA_IMAGE_0_SIZE"],
                bStart = self.devicetree["DT_FLASH_AREA_IMAGE_1_OFFSET"],
                bSize = self.devicetree["DT_FLASH_AREA_IMAGE_1_SIZE"]
            )

            self._logger.info(f"Found partition info '{self._partitions}'")

        return self._partitions
