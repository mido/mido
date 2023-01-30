# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT
"""
Standard MIDI Files

Wherever applicable, naming conventions follows the official specifications
published by the MIDI Association:
- RP-001: Standard MIDI File format v1.0
- RP-017: SMF Lyric
- RP-019: SMD Device
- RP-026: SMF Language
- RP-032: XMF Patch
"""
import ctypes
import struct
from dataclasses import dataclass
from enum import IntEnum

# StrEnum is only available natively from Python 3.11
try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


class MidiFileFormat(IntEnum):
    """
    Defined Standard MIDI File formats.

    Sometimes incorrectly referred to as types.
    """
    ZERO = 0
    ONE = 1
    TWO = 2


class MidiFileChunkType(StrEnum):
    HEADER = 'MThd'
    TRACK = 'MTrk'


class MidiFileDivisionFormat(IntEnum):
    TICKS_PER_QUARTER_NOTE = 0
    SMPTE_TICKS_PER_FRAME = 1


class MidiFileNegativeSMPTEFormat(IntEnum):
    TWENTY_FOUR_FPS = -24
    TWENTY_FIVE_FPS = -25
    THIRTY_FPS = -30
    THIRTY_DROP_FPS = -29


class MidiFileTicksPerFrameResolution(IntEnum):
    """Typical Midi File Division Format Ticks per Frame resolutions.

    8, 10 & 100 are also cited in the specification but aren't given a name.
    """
    MIDI_TIME_CODE = 4
    BIT = 80


class MidiFileDivision:
    _SIZE = 2  # Bytes aka 16-bits
    format: MidiFileDivisionFormat  # First bit
    # Only in format 0
    ticks_per_quarter_note: int  # 15 bits
    # Only in format 1
    negative_smpte_format = int  # 7 bits
    ticks_per_frame = int  # 8 bits

    def __init__(
            self,
            word: bytes,
    ):
        if len(word) != self._SIZE:
            raise ValueError("MidiFileDivision expects a 16-bit word")

        # Bit 15 indicates the format
        self.format = MidiFileDivisionFormat(word[0] >> 7)

        # Remaining bits
        if self.format is MidiFileDivisionFormat.TICKS_PER_QUARTER_NOTE:
            self.ticks_per_quarter_note = \
                ((word[0] & 0b0111_1111) << 0xFF) + word[1]

        if self.format is MidiFileDivisionFormat.SMPTE_TICKS_PER_FRAME:
            # Converts two's complement byte to negative integer
            self.negative_smpte_format = int.from_bytes(
                word[0].to_bytes(1, byteorder='big'),
                byteorder='big',
                signed=True)
            self.ticks_per_frame = word[1]


class MidiTick(int):
    pass


class MidiEvent:
    """
    A MidiEvent is any MIDI channel message. Running status is used.
    """
    pass


class SysExEventType(IntEnum):
    NORMAL = 0xF0
    ESCAPE = 0xF7


class SysExEvent:
    """
    SysExEvent is used to specify a MIDI system exclusive message.
    Either as one unit or in packets or as an "escape" to specify
     any arbitrary bytes to be transmitted.
    """
    type: SysExEventType
    length: int  # VLQ
    pass


@dataclass
class MetaEvent:
    """
    Specifies non-MIDI information useful to the SMF format or to sequencers.
    """
    meta_event_type: int
    length: int  # VLQ
    data: bytes


class SequenceNumber(MetaEvent):
    meta_event_type = 0x00
    length = 0x02
    number: int  # 4 bytes / 32 bits


class TextEvent(MetaEvent):
    meta_event_type = 0x01
    text: bytes  # ASCII Characters or other.


class CopyrightNotice(TextEvent):
    meta_event_type = 0x02


class SequenceOrTrackName(TextEvent):
    meta_event_type = 0x03


class InstrumentName(TextEvent):
    meta_event_type = 0x04


class Lyric(TextEvent):
    meta_event_type = 0x05


class Marker(TextEvent):
    meta_event_type = 0x06


class CuePoint(TextEvent):
    meta_event_type = 0x07


class ProgramName(TextEvent):
    meta_event_type = 0x08


class DeviceName(TextEvent):
    meta_event_type = 0x09


class ReservedTextEvent(TextEvent):
    META_EVENT_TYPES = range(0x0A, 0x0F + 1)


class MidiChannelPrefix(MetaEvent):
    meta_event_type = 0x20
    length = 0x01
    channel: int


class EndOfTrack(MetaEvent):
    meta_event_type = 0x2F
    length = 0x00


class SetTempo(MetaEvent):
    meta_event_type = 0x51
    length = 0x03


class SMPTEOffset(MetaEvent):
    meta_event_type = 0x54
    length = 0x05
    hours: int
    minutes: int
    seconds: int
    frames: int
    fractional_frames: int


class TimeSignature(MetaEvent):
    meta_event_type = 0x58
    length = 0x04
    numerator: int  # As notated
    denominator: int  # in negative power of 2. Ex. 3 for 6/8 since 2^-3 = 1/8
    midi_clocks: int  # in a metronome click
    number_of_notated_32nd: int  # in what MIDI thinks of as a quarter-note (24 MIDI Clocks)


class Scale(IntEnum):
    MAJOR = 0
    MINOR = 1


class KeySignature(MetaEvent):
    meta_event_type = 0x59
    length = 0x02
    # Once converted to signed int: Negative are flats, positive sharps
    sharps_or_flats: int
    scale: Scale


class SequencerSpecificMetaEvent(MetaEvent):
    meta_event_type = 0x7F
    data: bytes


class MtrkEvent:
    delta_time: MidiTick  # VLQ
    event: MidiEvent | SysExEvent | MetaEvent


class Chunk:
    """Class to read Standard MIDI Files Chunks.

    Inspired from the deprecated Python Chunk module
    since MIDI file chunks are somewhat similar to IFF chunks.

    A chunk has the following structure:

    +----------------+
    | type (4 bytes) |
    +----------------+
    | size (4 bytes) |
    +----------------+
    | data           |
    | ...            |
    +----------------+

    The ID is a 4-byte ASCII string which identifies the type of chunk.

    The size field (a 32-bit value, encoded using big-endian byte order)
    gives the size of the data excluding the 8 pytes of type and length.

    Usually a Standard MIDI File consists of two or more chunks.  The proposed
    usage of the Chunk class defined here is to instantiate an instance at
    the start of each chunk and read from the instance until it reaches
    the end, after which a new instance can be instantiated.  At the end
    of the file, creating a new instance will fail with an EOFError
    exception.

    Usage:
    while True:
        try:
            chunk = Chunk(file)
        except EOFError:
            break
        chunktype = chunk.getname()
        while True:
            data = chunk.read(nbytes)
            if not data:
                pass
            # do something with data

    The interface is file-like.  The implemented methods are:
    read, close, seek, tell, isatty.

    The __init__ method has one required argument, a file-like object
    (including a chunk instance).
    """
    TYPE_LEN = 4
    LENGTH_LEN = 4
    LENGTH_FORMAT = '>L'  # 32 bits big-endian
    type: MidiFileChunkType | str  # 4 chars (32 bits)
    data_length: int  # 32-bits
    data: bytes

    def __init__(self, file):
        self.closed = False

        self.file = file

        self.type = file.read(Chunk.TYPE_LEN)
        if len(self.type) < Chunk.TYPE_LEN:
            raise EOFError

        try:
            self.data_length = struct.unpack_from(
                self.LENGTH_FORMAT,
                file.read(self.LENGTH_LEN)
            )[0]
        except struct.error:
            raise EOFError from None

        self.size_read = self.TYPE_LEN + self.LENGTH_LEN

        try:
            self.offset = self.file.tell()
        except (AttributeError, OSError):
            self.seekable = False
        else:
            self.seekable = True

    def close(self):
        if not self.closed:
            try:
                self.skip()
            finally:
                self.closed = True

    def isatty(self):
        if self.closed:
            raise ValueError("I/O operation on closed file")
        return False

    def seek(self, pos, whence=0):
        """Seek to specified position into the chunk.
        Default position is 8 (start of the data).
        If the file is not seekable, this will result in an error.
        """

        if self.closed:
            raise ValueError("I/O operation on closed file")
        if not self.seekable:
            raise OSError("cannot seek")
        if whence == 1:
            pos = pos + self.size_read
        elif whence == 2:
            pos = pos + self.data_length
        if pos < 0 or pos > self.data_length:
            raise RuntimeError
        self.file.seek(self.offset + pos, 0)
        self.size_read = pos

    def tell(self):
        if self.closed:
            raise ValueError("I/O operation on closed file")
        return self.size_read

    def read(self, size=-1):
        """Read at most size bytes from the chunk.
        If size is omitted or negative, read until the end
        of the chunk.
        """

        if self.closed:
            raise ValueError("I/O operation on closed file")
        if self.size_read >= self.data_length:
            return b''
        if size < 0:
            size = self.data_length - self.size_read
        if size > self.data_length - self.size_read:
            size = self.data_length - self.size_read
        data = self.file.read(size)
        self.size_read = self.size_read + len(data)
        return data

    def skip(self):
        """Skip the rest of the chunk.
        If you are not interested in the contents of the chunk,
        this method should be called so that the file points to
        the start of the next chunk.
        """

        if self.closed:
            raise ValueError("I/O operation on closed file")
        if self.seekable:
            try:
                n = self.data_length - self.size_read
                return
            except OSError:
                pass
        while self.size_read < self.data_length:
            n = min(8192, self.data_length - self.size_read)
            dummy = self.read(n)
            if not dummy:
                raise


class HeaderChunk(Chunk):
    TYPE = MidiFileChunkType.HEADER
    DATA_FORMAT = '>3H'
    data_length = 6
    format: MidiFileFormat | int  # 16-bit word
    ntrks: int  # 16-bit word. Number of tracks
    division: MidiFileDivision  # 16-bit word

    def __init__(self, data):
        provided_length = len(data)
        if provided_length != self.data_length:
            raise IOError(
                f"expected {self.data_length} bytes, got {provided_length}")

        fields = struct.unpack_from(self.DATA_FORMAT, data)
        try:
            self.format = MidiFileFormat(fields[0])
        except ValueError:
            # TODO: filter according to spec & config
            raise
        self.ntrks = fields[1]
        try:
            self.division = MidiFileDivision(data[4:6])
        except:  # FIXME: be precise
            # TODO: filter according to spec & config
            raise


class TrackChunk(Chunk):
    TYPE = MidiFileChunkType.TRACK
    events = [MtrkEvent]


class SMF:
    header: HeaderChunk
    tracks = []

    # TODO: implement modes:
    # - strict: specification compliant. Raises errors.
    # - lenient: issues warnings instead of errors. Parses in best effort mode.
    # - silent: silences errors and warnings
    #   (not recommended if not user controlled).

    def __init__(self, file):
        while True:
            try:
                chunk = Chunk(file)
            except EOFError:
                break

            if chunk.type not in MidiFileChunkType:
                # Alien chunk
                # TODO: issue a silenceable warning
                pass

            # TODO: replace by bespoke objects
            # TODO: make sure first chunk is a header chunk
            while True:
                if chunk.type == TrackChunk.TYPE:
                    self.tracks.append(
                        TrackChunk(chunk.read(chunk.data_length)))
                elif chunk.type == HeaderChunk.TYPE:
                    if not self.header:
                        self.header = HeaderChunk(chunk.read(chunk.data_length))
                    else:
                        raise IOError("Multiple header chunks found!")
                else:
                    # Alien chunk data
                    # TODO: issue a warning
                    # DEBUG
                    data = chunk.read(chunk.data_length)
                    if not data:
                        pass
                    # do something with data

            if self.header.format == MidiFileFormat.ZERO:
                # TODO: make sure we only have one track
                pass

