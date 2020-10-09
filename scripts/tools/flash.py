###
 # \file
 #
 # \brief Provides handling of Skywire Nano flash contents
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##
import math
import time

class Flash:
    """nRF9160 flash
    """

    class Chunk:
        """A chunk of data that goes into a contiguous memory region
        """

        def __init__(self, start, data):
            """Creates a new chunk

            :param self:
                Self
            :param start:
                The starting address of the region
            :param data:
                The data, in bytes

            :return none:
            """

            self.start = start
            self.data = data

    PageSize        = 4096
    """The number of bytes in a page of flash"""

    SecureNvmc      = 0x50039000
    NonSecureNvmc   = 0x40039000
    """The Secure and Non-Secure NVMC peripherals"""

    Ready           = 0x400
    ReadyNext       = 0x408
    Config          = 0x504
    ConfigNs        = 0x584
    """Various NVMC registers in the peripheral, as offsets"""

    @staticmethod
    def paginateChunk(chunk):
        """Breaks a chunk into page-binned data

        If the starting and/or ending data doesn't fill an entire page, that
        page's data length will be less than a full page, and its starting
        address will be offset from the start of a page boundary.

        The provided chunk will be mutated and unusable after this function
        finishes. Don't get too attached.

        :param chunk:
            The bulk data chunk to break down into page chunks

        :return Array of chunks:
            The data chunked into page chunks
        """

        chunks = []

        # Get how far into the first page the address starts
        offset = chunk.start % Flash.PageSize

        # We might not start at the beginning of a page, so handle the first
        # page specially
        #
        # If this is a full page's worth, grab everything we can
        if offset == 0:
            length = Flash.PageSize
        # Else, only grab a page minus the missing data at the front
        else:
            length = Flash.PageSize - offset

        # It's possible they are only flashing a single page, and it's not the
        # entire page, so make sure we don't try grabbing too much data
        if length > len(chunk.data):
            length = len(chunk.data)

        # Get our first chunk
        chunks.append(Flash.Chunk(chunk.start, chunk.data[:length]))

        # We've handled that, so remove the data
        chunk.data = chunk.data[length:]

        # Move our start down to the next chunk
        chunk.start += length

        # The remaining data will always start on a page boundary, so handle
        # that generically
        #
        # Our final chunk may or may not fill the entire last page, but that
        # doesn't need any special handling beyond length checking. Since
        # Python is good about not complaining about array indexing that goes
        # past the end -- it just silently adjusts the ending index -- we won't
        # even bother with length checking.
        while len(chunk.data) > 0:
            # Get the next chunk
            chunks.append(Flash.Chunk(chunk.start, chunk.data[:Flash.PageSize]))

            # Remove that from our remaining data
            chunk.data = chunk.data[Flash.PageSize:]

            # Move our start down to the next page
            chunk.start += Flash.PageSize

        return chunks

    @staticmethod
    def getChunkSort(chunk):
        """Gets a value for sorting chunks

        :param chunk:
            The chunk to get a sort-able value for

        :return Integer:
            The chunk's sort value
        """

        # Our flash contents' starting addresses are naturally comparable to
        # each other, so just order chunks by their starting addresses
        return chunk.start

    @staticmethod
    def sortChunks(chunks):
        """Organizes chunks of data into ordered pages

        This will also combine page data if there are two entries for a single
        page.

        If any page has more than one entry for a single word of flash, an
        exception will be raised.

        :param chunks:
            Chunks of page data

        :raise Exception:
            More than one data entry for a word of flash

        :return none:
        """

        # First order our chunks by their starting addresses
        chunks.sort(key = Flash.getChunkSort)

        # We'll always check out page data by seeing if it can be compacted
        # into the previous chunk, so skip the first entry
        next = 1

        while True:
            # If we're done, move on
            if next >= len(chunks):
                break

            # If this chunk's page doesn't apply to the previous chunk's page,
            # nothing to do with this chunk
            if Flash.getPage(chunks[next].start) != Flash.getPage(chunks[next - 1].start):
                next += 1
                continue

            # We have already ordered the chunks by their starting addresses,
            # so we can just assume chunk A comes before chunk B. If the
            # addresses are the same -- and the data thus overlaps -- we'll
            # detect that all the same.
            #
            # Get where the first chunk ends
            chunkAEnd = chunks[next - 1].start + len(chunks[next - 1].data)
            chunkBStart = chunks[next].start

            # If the first chunk flows into the second chunk's data -- thus
            # overlapping -- that's a paddlin'
            if chunkAEnd > chunkBStart:
                raise Exception("Found overlapping chunk data at {:08X} and {:08X}".format(
                    chunks[next - 1].start,
                    chunks[next].start
                ))

            # If the data from the first chunk doesn't stop right at the second
            # chunk's start, then these can't be combined into a contiguous
            # range of flash, so don't do anything with this chunk
            if chunkAEnd != chunkBStart:
                next += 1
                continue

            # We'll combine these chunks, so remove the second one from the
            # chunk list
            chunkA = chunks[next - 1]
            chunkB = chunks.pop(next)

            # Concatinate the data, with the starting address being the first
            # chunk's
            chunkA.data.extend(chunkB.data)

            # We removed the chunk we were handling this time around, so don't
            # increment our index for next time

    @staticmethod
    def getPage(address):
        """Gets the page number from an address in flash

        :param address:
            The address whose page to get

        :return Integer:
            The page
        """

        return math.floor(address / Flash.PageSize)

    @staticmethod
    def _waitReady(ahb, ready):
        """Waits for the NVMC to be ready

        :param ahb:
            The AHB-AP to use
        :param ready:
            The ready register to use

        :return none:
        """

        while ahb.read(ready)[0] != 1:
            time.sleep(0.25)

    @staticmethod
    def erasePage(ahb, start):
        """Triggers a page erase

        :param ahb:
            The AHB-AP to use
        :param start:
            The starting address whose page to erase

        :return none:
        """

        if ahb.secure:
            config = Flash.SecureNvmc + Flash.Config
            ready = Flash.SecureNvmc + Flash.Ready
        else:
            config = Flash.NonSecureNvmc + Flash.ConfigNs
            ready = Flash.NonSecureNvmc + Flash.Ready

        # Enable erase
        ahb.write(config, [2])

        # Wait for the NVMC to be ready
        Flash._waitReady(ahb = ahb, ready = ready)

        # Make sure the starting address is page-aligned
        start = Flash.getPage(start) * Flash.PageSize

        # Trigger the erase
        ahb.write(start, [0xFFFFFFFF])

        # Wait for the NVMC to finish the erase
        Flash._waitReady(ahb = ahb, ready = ready)

    @staticmethod
    def writePage(ahb, start, data):
        """Writes data to a page of flash

        :param ahb:
            The AHB-AP to use
        :param start:
            The starting address to write data to
        :param data:
            The data to write

        :return none:
        """

        if (len(data) % 4) != 0:
            raise Exception("Data to be written not in 32-bits words!")

        if ahb.secure:
            config = Flash.SecureNvmc + Flash.Config
            ready = Flash.SecureNvmc + Flash.Ready
        else:
            config = Flash.NonSecureNvmc + Flash.ConfigNs
            ready = Flash.NonSecureNvmc + Flash.Ready

        # Wait for the NVMC to be ready
        Flash._waitReady(ahb = ahb, ready = ready)

        # Enable writing
        ahb.write(config, [1])

        # Wait again for the NVMC to be ready
        Flash._waitReady(ahb = ahb, ready = ready)

        # Convert the byte contents to words for AHB-AP
        values = []

        for i in range(int(len(data) / 4)):
            wordStart = i * 4

            values.append(int.from_bytes(data[wordStart:wordStart + 4], byteorder = "little"))

        # Dump the data out to flash
        ahb.write(start, values)

    @staticmethod
    def writeChunks(ahb, chunks, erase = True, passthrough = True):
        """Writes chunks to flash

        :param ahb:
            The AHB-AP to use
        :param chunks:
            The chunks to write
        :param erase:
            Whether or not to erase pages as we go
        :param passthrough:
            Whether or not to allow this to be passed on to nrfjprog

        :return none:
        """

        # If we still have Secure permissions, don't bother chunking the data;
        # just pass it directly on to pynrfjprog, which will handle the NVMC
        # stuff on its own
        if passthrough and ahb.secure:
            for chunk in chunks:
                print("Writing {} to flash @ {:08X}".format(len(chunk.data), chunk.start))

                ahb.dap.api.write(chunk.start, chunk.data, True)

            return

        # Further chunk the file data so we can properly flash its contents
        pageChunks = []

        for chunk in chunks:
            pageChunks.extend(Flash.paginateChunk(chunk = chunk))

        # Organize the flash contents and optimize them
        Flash.sortChunks(chunks = pageChunks)

        lastPage = -1

        # For each chunk, write out the contents
        for chunk in pageChunks:
            # Get the page this applies to
            page = Flash.getPage(address = chunk.start)

            # If we are erasing, we didn't do an initial mass erase, and this
            # page isn't the one we erased last time around, erase this page
            #
            # We ordered our chunks by their address, so we can do a simple
            # tracking of the previous page and not bother with tracking each
            # individual page we've erased.
            if erase and (page != lastPage):
                print("Erasing page @ {:08X}".format(chunk.start))

                Flash.erasePage(
                    ahb = ahb,
                    start = chunk.start
                )

                lastPage = page

            print("Writing {} to page @ {:08X}".format(len(chunk.data), chunk.start))

            # Write out the chunk's contents
            Flash.writePage(
                ahb = ahb,
                start = chunk.start,
                data = chunk.data
            )
