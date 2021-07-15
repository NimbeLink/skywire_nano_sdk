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

# Users of the SDK will likely not have nrfxlib in the include path without the
# BSD library being selected (including at least nRF SDK version v1.4.x), so
# include it manually here
if (EXISTS "${NRF_DIR}/../nrfxlib/bsdlib/include")
    zephyr_include_directories("${NRF_DIR}/../nrfxlib/bsdlib/include")
else()
    message(WARNING "BSDLIB include path not found, might need to include it manually")
endif()

add_subdirectory(nimbelink)
