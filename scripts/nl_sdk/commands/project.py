"""
A command that provides arguments for setting up a command's project context

(C) NimbeLink Corp. 2021

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import argparse
import typing

import nimbelink.command as command
import nimbelink.utils as utils

import nl_sdk as sdk

class ProjectCommand(command.Command):
    """A command that provides needed arguments for setting up a command's
    project context

    This class is indended to provide a single source for handling command
    arguments that are optional and can be auto-detected from a local software
    project.

    Not all commands will need all project resources, and including all of them
    as command arguments would lead to a confusing user experience -- how would
    you necessarily know which are important, which are needed but you haven't
    specified, etc.? This command will instead provide a means to list all of
    the project resources needed to fulfill the command's actions, and will
    faciliate registering argparse arguments for those parameters.
    """

    class Resource:
        """A project resource needed for a command
        """

        class Type:
            """The available project resources
            """

            SignKey         = 0
            EncryptKey      = 1
            Kconfig         = 2
            Devicetree      = 3
            BuildArtifact   = 4
            SignedArtifact  = 5
            UpdateArtifact  = 6
            Version         = 7
            Partitions      = 8

        class Map:
            """A map from a resource to an argparse command
            """
            def __init__(
                self,
                name: str,
                help: str,
                singleValue: bool = None,
                getValue: typing.Callable = None
            ) -> None:
                """Creates a new map

                :param self:
                    Self
                :param name;
                    Our name
                :param help:
                    Our parameter help text
                :param singleValue:
                    Whether or not we only support a single value/use
                :param getValue:
                    How to get our parameters value

                :return none:
                """

                if singleValue is None:
                    singleValue = True

                if getValue is None:
                    getValue = lambda value: value

                self.name = name
                self.help = help
                self.singleValue = singleValue
                self.getValue = getValue

        Maps = {
            Type.SignKey: Map(
                name = "signKey",
                help = "Signing key",
                singleValue = False,
                getValue = lambda value: sdk.Project.Key(type = sdk.Project.Key.Type.Sign, fileName = value)
            ),
            Type.EncryptKey: Map(
                name = "encryptKey",
                help = "Encryption key",
                singleValue = False,
                getValue = lambda value: sdk.Project.Key(type = sdk.Project.Key.Type.Encrypt, fileName = value)
            ),
            Type.Kconfig: Map(
                name = "kconfig",
                help = "A Kconfig build file",
                getValue = lambda value: utils.Kconfig.makeFromConfig(fileName = value)
            ),
            Type.Devicetree: Map(
                name = "devicetree",
                help = "A Devicetree build file",
                getValue = lambda value: utils.Devicetree.makeFromConfig(fileName = value)
            ),
            Type.BuildArtifact: Map(
                name = "buildArtifact",
                help = "An unsigned Zephyr HEX build artifact"
            ),
            Type.SignedArtifact: Map(
                name = "signedArtifact",
                help = "A signed HEX generated artifact"
            ),
            Type.UpdateArtifact: Map(
                name = "updateArtifact",
                help = "A signed and optionally encrypted BIN generated artifact"
            ),
            Type.Version: Map(
                name = "version",
                help = "A software version"
            ),
            Type.Partitions: Map(
                name = "partitions",
                help = "Application firmware partitions"
            )
        }

        def __init__(
            self,
            type: "ProjectCommand.Resource.Type",
            name: str = None,
            singleValue: bool = None
        ) -> None:
            """Creates a new project resource

            :param self:
                Self
            :param type:
                The type of project resource this is managing
            :param name:
                The argparse name to use instead of our default
            :param singleValue:
                Whether or not only a single instance of the resource is needed

            :raise ValueError:
                Invalid 'type' parameter value

            :return none:
            """

            if type not in ProjectCommand.Resource.Maps:
                raise ValueError(f"Unknown resource type '{type}'")

            self._map = ProjectCommand.Resource.Maps[type]

            # If specified, override the resource map's default single/multiple
            # setting
            if singleValue is not None:
                self._singleValue = singleValue

            # Else, defer to the map's default
            else:
                self._singleValue = self._map.singleValue

            # If specified, note the incoming name as our argparse 'attribute'
            # name
            if name is not None:
                self.attributeName = name

            # Else, use our resource map's name
            else:
                self.attributeName = self._map.name

            # Our Project-specific 'kwarg' always come from our resource map
            self.kwargName = self._map.name

        @staticmethod
        def _getArgparseName(name: str) -> str:
            """Gets our argparse-friendly argument name

            :param name:
                The name to convert

            :return str:
                The argument name
            """

            # Replace capital letters with a dash and their lowercase value
            for i in range(len(name)):
                if name[i].isupper():
                    name = name[:i] + f"-{name[i].lower()}" + name[i + 1:]

            return "--" + name

        def addArguments(self, parser: argparse.ArgumentParser) -> None:
            """Adds arguments for our command

            :param self:
                Self
            :param parser:
                The parser to add arguments to

            :return none:
            """

            if self._singleValue:
                action = "store"
                help = self._map.help
            else:
                action = "append"
                help = self._map.help + "; use multiple times for multiple entries"

            parser.add_argument(
                ProjectCommand.Resource._getArgparseName(self.attributeName),
                action = action,
                dest = self.attributeName,
                required = False,
                help = help
            )

        def getValue(self, args: typing.List[object]) -> int:
            """Gets this resource's value from the argument list

            :param self:
                Self
            :param args:
                The argument list

            :raise ValueError:
                Failed to get resource value

            :return None:
                No resource value
            :return object:
                The resource's Project-ready value
            """

            # Get our value from the argument list
            value = getattr(args, self.attributeName)

            # If the value wasn't used, nothing to do
            if value is None:
                return None

            # If this is a list of arguments
            if isinstance(value, list):
                # If we are supposed to only be used once but multiple were
                # provided, complain
                if self._singleValue and (len(value) > 1):
                    raise ValueError(f"Argument '{self.attributeName}' used multiple times, but only one allowed")

                # Convert each value
                for i in range(len(value)):
                    value[i] = self._map.getValue(value[i])

            else:
                # Convert the value
                value = self._map.getValue(value)

                # If we or the default map support multiple entries, make sure
                # this looks like a list
                if not self._singleValue or not self._map.singleValue:
                    value = [value]

            return value

    def __init__(
        self,
        *args,
        singleProject: bool,
        resources: typing.List["ProjectCommand.Resource"],
        **kwargs
    ) -> None:
        """Creates a new project command

        :param self:
            Self
        :param *args:
            Positional Command arguments
        :param **kwargs:
            Keyword Command arguments
        :param singleProject:
            Whether or not this command should only accept a single project
        :param resources:
            The project resources needed

        :return none:
        """

        super().__init__(*args, **kwargs)

        self._singleProject = singleProject
        self._resources = resources

    def addArguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds arguments for our command

        :param self:
            Self
        :param parser:
            The parser to add arguments to

        :return none:
        """

        parser.add_argument(
            "-p", "--project",
            action = "append",
            dest = "projects",
            required = False,
            help = "Project(s) to run a command on"
        )

        parser.add_argument(
            "-d", "--directory",
            required = False,
            help = "The root directory containing projects and their build directories"
        )

        for resource in self._resources:
            resource.addArguments(parser = parser)

    def runCommand(self, args: typing.List[object]) -> None:
        """Runs the root command

        :param self:
            Self
        :param args:
            Our arguments

        :return >0:
            Failed to handle command arguments
        :return None:
            Command arguments set up
        """

        # If no project names were specified, try to find them
        if args.projects is None:
            args.projects = sdk.Project.getNames()

        # If we should have only had a single project but multiple were
        # specified, that's a paddlin'
        if self._singleProject and (len(args.projects) > 1):
            self.stdout.error("Must have a unique project for this:")

            for project in args.projects:
                self.stdout.error(f"    {project}")

            return 1

        kwargs = {}

        # If they specified the root directory, note it
        #
        # It's fine if this is specified only once for multiple projects, as
        # they all are likely run out of the same directory.
        if args.directory is not None:
            kwargs["directory"] = args.directory

        # Collect our resources in our dictionary
        for resource in self._resources:
            try:
                value = resource.getValue(args = args)

                if value is not None:
                    kwargs[resource.kwargName] = value

            except ValueError as ex:
                self.stdout.error(f"{ex}")

                return 1

        # If only some project resources were provided manually but we found multiple
        # projects, we won't be able to fill unique profiles for each project
        #
        # Auto-detection would fill in all project resources, and specifying all
        # needed resources would sufficiently fill out the intended project, but
        # only partially filling out a single project -- and leaving the other
        # dangling -- is not valid.
        if (len(args.projects) > 1) and (len(kwargs) > 0):
            if len(kwargs) != len(self._resources):
                self.stdout.error("Cannot specify subset of arguments when multiple projects present:")

                for project in args.projects:
                    self.stdout.error(f"    {project}")

                return 1

            # We specified everything found in a 'project' that's needed by our
            # child command, so there's no reason to carry around valid
            # projects; just replace them with an anonymous one
            args.projects = [None]

        # Our projects will want their keys combined into a single argument, so
        # if we have any specified, make a total list of them
        keys = []

        if ("signKey" in kwargs) and (kwargs["signKey"] is not None):
            keys += kwargs["signKey"]

            del kwargs["signKey"]

        if ("encryptKey" in kwargs) and (kwargs["encryptKey"] is not None):
            keys += kwargs["encryptKey"]

            del kwargs["encryptKey"]

        # If we got keys, add them to the argument list
        if len(keys) > 0:
            kwargs["keys"] = keys

        # Convert each project into a Project object for the command to use
        for i in range(len(args.projects)):
            args.projects[i] = sdk.Project(name = args.projects[i], **kwargs)

        return None
