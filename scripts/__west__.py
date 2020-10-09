###
 # \file
 #
 # \brief Sets up the script package for west's use
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##
import os
import sys

sys.path.insert(
    1,
    os.path.dirname(os.path.realpath(__file__))
)

from commands.app import SkywireAppCommand
from commands.dfu import SkywireDfuCommand
from commands.flash import SkywireFlashCommand
from commands.update import SkywireUpdateCommand
