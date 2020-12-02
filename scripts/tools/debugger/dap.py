###
 # \file
 #
 # \brief Provides base Debug Access Port functionality
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import time

from pynrfjprog import API
from pynrfjprog import APIError

class Dap:
    """A Debug Access Port
    """

    def __init__(self, *args, serialNumber = None, **kwargs):
        """Creates a new DAP

        :param self:
            Self
        :param *args:
            Positional arguments
        :param serialNumber:
            The serial number of the debugger to select; None if any/the only
            debugger
        :param **kwargs:
            Keyword arguments

        :return none:
        """

        self.api = API.API(*args, **kwargs, device_family = "NRF91")

        self.api.open()

        if serialNumber == None:
            self.api.connect_to_emu_without_snr()
        else:
            self.api.connect_to_emu_with_snr(serial_number = serialNumber)

    def __del__(self):
        """Deletes a DAP

        :param self:
            Self

        :return none:
        """

        self.api.close()

    def read(self, port, register):
        """Reads from an address in an access port

        :param self:
            Self
        :param port:
            The access port to read from
        :param register:
            The register to read

        :return Integer:
            The value in the register
        """

        return self.api.read_access_port_register(port, register)

    def write(self, port, register, value):
        """Writes a value to an access port

        :param self:
            Self
        :param port:
            The access port to write to
        :param register:
            The register to write
        :param value:
            The value to write to the register

        :return none:
        """

        self.api.write_access_port_register(port, register, value)
