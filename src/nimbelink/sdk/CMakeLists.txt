###
 # \file
 #
 # \brief Builds the Skywire Nano SDK
 #
 # © NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

add_subdirectory(secure_services)

# Always include the peripheral request collector
zephyr_sources(
    peripheral_requests.cpp
)
