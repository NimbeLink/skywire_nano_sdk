"""
Setup for the NimbeLink SDK package

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

from distutils.core import setup
from setuptools import find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

class PostDevelopCommand(develop):
    """Post-installation for development mode
    """

    def run(self) -> None:
        """Runs our post-installation handling

        :param self:

        :return none:
        """

        develop.run(self)

        import nimbelink.module as module
        module.register(module.Module(name = "nl_sdk", alias = "sdk"))

class PostInstallCommand(install):
    """Post-installation for install mode
    """

    def run(self) -> None:
        """Runs our post-installation handling

        :param self:

        :return none:
        """

        install.run(self)

        import nimbelink.module as module
        module.register(module.Module(name = "nl_sdk", alias = "sdk"))

setup(
    name = "pynl-sdk",
    description = "NimbeLink SDK",
    version = "1.0.0",
    packages = find_packages(),
    cmdclass = {
        "develop": PostDevelopCommand,
        "install": PostInstallCommand
    },
    install_requires = [
        "imgtool",

        "pynl-base @ git+https://github.com/NimbeLink/pynl-base@v1.1.0"
    ]
)
