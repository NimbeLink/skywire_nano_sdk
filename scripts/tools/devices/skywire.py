###
 # \file
 #
 # \brief Interfaces with a Skywire using its AT interface
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

import re
import serial
import time

from tools.at import Response

class Skywire(object):
    """Python class for sending and receiving commands from the NimbeLink
    Skywire family of embedded cellular modems.
    """

    DefaultTimeout = 5.0
    """A default timeout for interacting with a Skywire"""

    def __init__(self, *args, **kwargs):
        """Creates a new Skywire device

        :param self:
            Self
        :param *args:
            Arguments to a serial port
        :param **kwargs:
            Keyword arguments to a serial port

        :return none:
        """

        # Try to make the serial port with our default timeout
        try:
            self.device = serial.Serial(*args, **kwargs, timeout = Skywire.DefaultTimeout)

        # If it appears the user specified their own timeout, just use that
        except SyntaxError:
            self.device = serial.Serial(*args, **kwargs)

        self._clear()

        # Try to get a fresh state by sending a basic AT command
        self.sendCommand("AT", 1)

    def _clear(self):
        """Clears our device's input/output buffers

        :param self:
            Self

        :return none:
        """

        while True:
            self.device.reset_output_buffer()
            self.device.reset_input_buffer()

            if len(self.device.read_all()) < 1:
                break

    def _setTimeout(self, timeout):
        """Sets the device's serial port timeout

        :param self:
            Self
        :param timeout:
            The timeout to set

        :return none:
        """

        # Setting the serial port's timeout can cause issues with buffering of
        # input/output, so only set it if necessary
        #if self.device.timeout != timeout:
        #    self.device.timeout = timeout

    def _waitForResponse(self, timeout = None):
        """Waits for a certain response

        :param timeout:
            How long to wait for the response

        :return None:
            Timed out waiting for response
        :return Response:
            The response
        """

        if timeout == None:
            timeout = Skywire.DefaultTimeout

        self._setTimeout(timeout = timeout)

        startTime = time.time()

        read = ""

        while True:
            # If we've timed out, stop
            if (time.time() - startTime) > timeout:
                return None

            # Get another line of text
            read += self.device.readline().decode()

            # If that timed out, stop
            if (read == None) or (len(read) < 1):
                return None

            # If this is a final result, return it
            try:
                return Response.makeFromString(read)

            # Else, keep waiting
            except Exception:
                pass

    def sendCommand(self, command, timeout = None):
        """Sends a command to the Skywire

        :param command:
            Command to send; must include carriage-return if needed
        :param timeout:
            How long to wait for the response, if any

        :return None:
            Timed out waiting for response
        :return Response:
            The response
        """

        if timeout == None:
            timeout = Skywire.DefaultTimeout

        # If the command doesn't have proper line endings, add them
        if not command.endswith("\r\n"):
            command += "\r\n"

        self._clear()

        # Write the command
        self.device.write(command.encode())

        # Wait for a response
        response = self._waitForResponse(timeout = timeout)

        # If that failed, just use that
        if response == None:
            return None

        # Try to filter out the command itself, if present
        if (len(response.output) > 0) and (response.output[0] == command.rstrip("\r\n")):
            response.output = response.output[1:]

        return response

    def waitUrc(self, urc, timeout = None):
        """Waits for an asynchronous output

        The URC string can be a regular expression, but it must be contained on
        a single line.

        :param self:
            Self
        :param urc:
            The URC to wait for
        :param timeout:
            How long to wait for the URC

        :return None:
            Timed out waiting for URC
        :return String:
            The URC, sans line endings
        """

        if timeout == None:
            timeout = Skywire.DefaultTimeout

        self._setTimeout(timeout = timeout)

        startTime = time.time()

        while True:
            # If we've timed out, stop
            if (time.time() - startTime) > timeout:
                return None

            # Get another line of text
            read = self.device.readline().decode()

            # If that timed out, stop
            if (read == None) or (len(read) < 1):
                return None

            # If the URC matches, great, got it
            if re.match(urc, read) != None:
                return read.rstrip("\r\n")
