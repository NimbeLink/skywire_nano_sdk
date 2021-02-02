###
 # \file
 #
 # \brief Sends data using an XMODEM interface
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

class Xmodem:
    """An XMODEM interface
    """

    ChunkSize = 256
    """How much we'll chunk transmission data into"""

    class Packet:
        """An XMODEM packet
        """

        TransferSizes = [128, 1024]
        """The available packet sizes"""

        SmallStart = 0x01
        """A start-of-header byte value for small packets"""

        LargeStart = 0x02
        """A start-of-header byte value for large packets"""

        EndOfTransmission = 0x04
        """An end of transmission byte value"""

        Ack = 0x06
        """A packet acknowledgement byte value"""

        Nak = 0x15
        """A packet no-acknowledgement bytes value"""

        @classmethod
        def getInversePacketId(cls, packetId):
            """Gets the 'inverse' packet ID

            :param cls:
                Class
            :param packetId:
                The packet ID to get the inverse of

            :return inversePacketId:
                The inverse packet ID
            """

            return (255 - packetId) & 0xFF

        @classmethod
        def getPacket(cls, packetData, packetId):
            """Gets an XMODEM packet from data and an ID

            :param cls:
                Class
            :param packetData:
                The data to packetize
            :param packetId:
                The ID of this packet

            :return Array of bytes:
                The packet
            """

            padLength = 0

            if len(packetData) <= 128:
                packetStart = cls.SmallStart
                padLength = 128 - len(packetData)
            else:
                packetStart = cls.LargeStart
                padLength = 1024 - len(packetData)

            # If we should pad the packet, do so
            if padLength > 0:
                for i in range(padLength):
                    packetData += bytearray([0xFF])

            # Figure out the next packet's ID, making sure we always stay a byte
            inversePacketId = cls.getInversePacketId(packetId = packetId)

            # Compile the header and footer
            packetHeader = bytearray([packetStart, packetId, inversePacketId])

            # Checksum always starts at 0
            checksum = 0

            # Add together each byte, making sure we always stay a byte
            for byte in packetData:
                checksum = (checksum + byte) & 0xFF

            packetFooter = bytearray([checksum])

            # Compile the full packet
            return packetHeader + packetData + packetFooter

        @classmethod
        def getFirstPacketId(cls):
            """Gets the first packet ID in the sequence

            :param cls:
                Class

            :return 0x01:
                Always
            """

            return 0x01

        @classmethod
        def getNextPacketId(cls, packetId):
            """Gets the next packet ID in the sequence

            :param cls:
                Class
            :param packetId:
                The current packet ID

            :return Byte:
                The next packet ID
            """

            return (packetId + 1) & 0xFF

    def __init__(self, device):
        """Creates a new XMODEM interface

        :param self:
            Self
        :param device:
            Our UART device

        :return none:
        """

        self.device = device

        # Assume we should be mostly quiet
        self.verbose = False

    def clearDevice(self):
        """Clears our device's input/output buffers

        :param self:
            Self

        :return none:
        """

        while len(self.device.read_all()) > 0:
            self.device.reset_output_buffer()
            self.device.reset_input_buffer()

    def startTransmission(self):
        """Starts XMODEM transmission

        :param self:
            Self

        :return True:
            Transmission started
        :return False:
            Failed to start transmission
        """

        # Initialize our packet ID
        self.packetId = Xmodem.Packet.getFirstPacketId()

        # Try for a bit to get our initial NAK byte
        for i in range(5):
            start = self.device.read()

            # If we got the initial NAK, great, move on
            if (len(start) > 0) and (start[0] == Xmodem.Packet.Nak):
                return True

            time.sleep(1)

        print("Failed to get starting NAK ({})".format(start.decode()))

        return False

    def sendData(self, packetData):
        """Sends a packet to a device

        :param self:
            Self
        :param data:
            The data to send

        :return True:
            Packet sent and acknowledged
        :return False:
            Failed to send packet
        """

        # Get the packet
        packet = Xmodem.Packet.getPacket(
            packetData = packetData,
            packetId = self.packetId
        )

        # If we're being verbose, print the packet out
        if self.verbose:
            print(packet.hex())

        # If we aren't using flow control, chunk the data
        if not self.device.rtscts:
            writeLength = 0

            bytes = list(packet)

            while True:
                if len(bytes) < 1:
                    break

                time.sleep(0.1)

                writeLength += self.device.write(bytes[0:Xmodem.ChunkSize])

                bytes = bytes[Xmodem.ChunkSize:]

        # Else, just spit everything out
        else:
            writeLength = self.device.write(packet)

        # If that failed, that's a paddlin'
        if writeLength != len(packet):
            print("Failed to send all bytes ({})".format(writeLength))
            return False

        # Wait for a response
        response = self.device.read(1)

        # If that failed, that's a paddlin'
        if (response == None) or (len(response) < 1):
            print("Failed to get response")
            return False

        # If it wasn't acknowledged, that's a paddlin'
        if response[0] != Xmodem.Packet.Ack:
            print("Failed to get ACK ({})".format(response[0]))
            return False

        # Use the next packet ID next time
        self.packetId = Xmodem.Packet.getNextPacketId(packetId = self.packetId)

        return True

    def endTransmission(self):
        """Ends XMODEM transmission

        :param self:
            Self

        :return True:
            Always
        """

        # Stop transmission
        self.device.write([Xmodem.Packet.EndOfTransmission])

        return True

    def transfer(self, file, packetSize = 1024):
        """Transfers a file using XMODEM

        :param self:
            Self
        :param file:
            An opened file
        :param packetSize:
            The size of the packets to use

        :raise Exception:
            Invalid packet size

        :return True
            File sent
        :return False
            Failed to send file
        """

        if packetSize not in Xmodem.Packet.TransferSizes:
            raise Exception("Can't use packet size of {}!".format(packetSize))

        # Guilty until proven innocent
        success = False

        count = 0

        # Make sure nothing is left over
        self.clearDevice()

        # If we fail to kick off transmission, that's a paddlin'
        if not self.startTransmission():
            print("Failed to start transmission")
            return False

        self.clearDevice()

        while True:
            time.sleep(0.01)

            # Try to read the next chunk of data
            packetData = file.read(packetSize)

            # If we're out of data, move on
            if len(packetData) < 1:
                print("No more data, done!")

                success = True
                break

            # If we fail to send the data, stop
            if not self.sendData(packetData = packetData):
                print("Failed to send packet {}".format(count))
                break

            count = count + 1

        # Let the device know we're done
        self.endTransmission()

        return success
