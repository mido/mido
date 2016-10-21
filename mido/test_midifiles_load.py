import io
from pytest import raises
from .messages import Message
from .midifiles import MidiFile

HEADER_ONE_TRACK = """
4d 54 68 64  # MThd
00 00 00 06  # Chunk size
      00 01  # Type 1
      00 01  # 1 track
      00 78  # 120 ticks per beat
"""    


def parse_hexdump(hexdump):
    data = bytearray()
    for line in hexdump.splitlines():
        data += bytearray.fromhex(line.split('#')[0])
    return data


def read_file(hexdump):
    return MidiFile(file=io.BytesIO(parse_hexdump(hexdump)))


def test_no_tracks():
    assert read_file("""
    4d 54 68 64  # MThd
    00 00 00 06  # Chunk size
    00 01  # Type 1
    00 00  # 0 tracks
    00 78  # 120 ticks per beat
    """).tracks == []


def test_single_message():
    assert read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b  # MTrk
    00 00 00 04
    00 90 40 40  # note_on
    """).tracks[0] == [Message('note_on', note=64, velocity=64)]


def test_empty_file():
    with raises(EOFError):
        read_file("")
   

def test_eof_in_track():
    with raises(EOFError):
        read_file(HEADER_ONE_TRACK + """
        4d 54 72 6b  # MTrk
        00 00 00 01  # Chunk size
        # Oops, no data here.
        """)
