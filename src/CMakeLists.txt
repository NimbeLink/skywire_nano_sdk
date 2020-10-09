###
 # \file
 #
 # \brief Builds the Skywire Nano SDK
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

# The SDK will assume the top-level src/ directory is in the include path
zephyr_include_directories("${CMAKE_CURRENT_LIST_DIR}")

add_subdirectory(nimbelink)
