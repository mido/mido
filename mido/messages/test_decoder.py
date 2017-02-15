from .decode import Decoder

NOTE_ON = dict(type='note_on', note=1, velocity=2, channel=0, time=0)
SYSEX = dict(type='sysex', data=(1, 2, 3), time=0)
EMPTY_SYSEX = dict(type='sysex', data=(), time=0)
CLOCK = dict(type='clock', time=0)


def decode(data):
    """Decode data and return as a list of message dict."""
    return list(Decoder(bytearray.fromhex(data)))


def test_channel_message():
    assert decode('90 01 02') == [NOTE_ON]


def test_sysex():
    assert decode('f0 01 02 03 f7') == [SYSEX]


def test_empty_sysex():
    assert decode('f0 01 02 03 f7') == [SYSEX]


def test_realtime():
    assert decode('f8') == [CLOCK]


def test_double_realtime():
    assert decode('f8 f8') == [CLOCK, CLOCK]


def test_realtime_inside_message():
    """Realtime message inside message should reset the parser."""
    assert decode('90 01 f8 02') == [CLOCK]


def test_realtime_inside_sysex():
    """Realtime messages are allowed inside sysex.

    The sysex messages should be delivered first.

    This is the only case where a message is allowed inside another message.
    """
    assert decode('f0 01 02 f8 03 f7') == [CLOCK, SYSEX]
    assert decode('f0 f8 f7') == [CLOCK, EMPTY_SYSEX]


def test_message_inside_sysex():
    """Non-realtime message inside sysex should reset the parser."""
    assert decode('f0 90 01 02 f7') == [NOTE_ON]


def test_sysex_inside_sysex():
    """Sysex inside sysex should reset the parser."""
    assert decode('f0 20 30 f0 01 02 03 f7') == [SYSEX]


def test_stray_data_bytes():
    """Data bytes outside messages should be ignored."""
    assert decode('00 01 90 01 02 00 02 f8 01') == [NOTE_ON, CLOCK]
