###
 # \file
 #
 # \brief Provides handling of actions using a DAP's AHB-AP interface
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

from tools.debugger.dap import Dap

class Ahb:
    """A Debug Access Port
    """

    Port = 0
    """The access port we use"""

    class Configs:
        """The various configuration registers we'll use
        """

        ControlStatus       = 0x00
        TransferAddress     = 0x04
        DataReadWrite       = 0x0C

    def __init__(self, *args, **kwargs):
        """Creates a new AHB-AP

        :param self:
            Self
        :param *args:
            Positional arguments
        :param **kwargs:
            Keyword arguments

        :return none:
        """

        self.dap = Dap(*args, **kwargs)

        # Assume we're Secure by default
        self.secure = True

        self._setDefaultConfig()

    def setSecureState(self, secure):
        """Sets our Secure/Non-Secure status

        :param self:
            Self
        :param secure:
            Whether or not we should act as a Secure debugger

        :return none:
        """

        self.secure = secure

    def _setDefaultConfig(self):
        """Sets our control to our default expected values

        :param self:
            Self

        :return none:
        """

        self._configure(size = 32, autoInc = True, secure = self.secure)

    def _configure(self, size = None, autoInc = None, secure = None):
        """Configures our access parameters

        :param self:
            Self
        :param size:
            The transfer size, in bytes
        :param autoInc:
            Whether or not we should try to auto-increment reads/writes
        :param secure:
            Whether or not we should try to be Secure-compatible

        :return True:
            Configured
        :return False:
            Failed to configure
        """

        currentValue = self.dap.read(self.Port, self.Configs.ControlStatus)

        newValue = currentValue

        # Make sure debugging is enabled
        newValue |= (1 << 6)

        # Set up the transfer size
        if size == None:
            pass
        else:
            newValue &= ~(3 << 0)

            if size == 16:
                newValue |= (1 << 0)
            elif size == 32:
                newValue |= (2 << 0)

        # Set up the transfer address handling
        if autoInc == None:
            pass
        else:
            newValue &= ~(3 << 4)

            if autoInc:
                #newValue |= (2 << 4)
                newValue |= (1 << 4)

        # Set up the transfer security state
        if secure == None:
            pass
        elif secure:
            newValue &= ~(1 << 30)
        else:
            newValue |= (1 << 30)

        if newValue == currentValue:
            return True

        # Set the configuration
        self.dap.write(self.Port, self.Configs.ControlStatus, newValue)

        return True

    def _waitReady(self):
        """Waits for the port to be ready to do more AHB transfers

        :param self:
            Self

        :return none:
        """

        while True:
            try:
                status = self.dap.read(self.Port, self.Configs.ControlStatus)

                if (status & (1 << 7)) != 1:
                    break
            except Exception:
                pass

    def read(self, address, length = 1):
        """Reads values from an address range

        :param address:
            The starting address to read from
        :param length:
            The amount of data to read, in words

        :return None:
            Failed to read register
        :return Array of integers:
            Values
        """

        self._waitReady()
        self._setDefaultConfig()

        # Set the starting address we'll read from as our target
        self.dap.write(self.Port, self.Configs.TransferAddress, address)

        values = []

        # Read
        for i in range(length):
            self._waitReady()

            values.append(self.dap.read(self.Port, self.Configs.DataReadWrite))

        return values

    def write(self, address, values, flush = True):
        """Writes values to an address range

        :param address:
            The starting address to write to
        :param values:
            The values to write, in words
        :param flush:
            Whether or not to flush the final write

        :return True:
            Values written
        :return False:
            Failed to write values
        """

        self._waitReady()
        self._setDefaultConfig()

        # Set the starting address we'll write to as our target
        self.dap.write(self.Port, self.Configs.TransferAddress, address)

        for value in values:
            self._waitReady()

            #print("Writing {:08X} to {:08X}".format(
            #    value,
            #    self.dap.read(self.Port, self.Configs.TransferAddress)
            #))

            self.dap.write(self.Port, self.Configs.DataReadWrite, value)

            address += 4

            # Our DAP interface's auto-increment handling will 'roll over' at
            # 1024 bytes, meaning we'll need to manually bump the address past
            # that boundary whenever the data rolls past it
            if (address % 1024) == 0:
                self.dap.write(self.Port, self.Configs.TransferAddress, address)

        # If they need a flush, do something simple
        if flush:
            self._waitReady()

            self.dap.write(self.Port, self.Configs.TransferAddress, address)

        return True
