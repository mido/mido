from mido.tokenizer import Tokenizer

def tokenize(midi_bytes):
    return list(Tokenizer(midi_bytes))


def test_channel_message():
    assert tokenize([0x90, 1, 2]) == [[0x90, 1, 2]]


def test_sysex():
    assert tokenize([0xf0, 1, 2, 3, 0xf7]) == [[0xf0, 1, 2, 3, 0xf7]]


def test_empty_sysex():
    assert tokenize([0xf0, 0xf7]) == [[0xf0, 0xf7]]


def test_realtime():
    assert tokenize([0xf8]) == [[0xf8]]


def test_double_realtime():
    assert tokenize([0xf8, 0xf8]) == [[0xf8], [0xf8]]


def test_realtime_inside_message():
    """Realtime message inside message should reset the parser."""
    assert tokenize([0x90, 1, 0xf8, 2]) == [[0xf8]]


def test_realtime_inside_sysex():
    """Realtime messages are allowed inside sysex.

    The sysex messages should be delivered first.

    This is the only case where a message is allowed inside another message.
    """ 
    assert tokenize([0xf0, 1, 0xf8, 2, 0xf7]) == [[0xf8], [0xf0, 1, 2, 0xf7]]
    assert tokenize([0xf0, 0xf8, 0xf7]) == [[0xf8], [0xf0, 0xf7]]


def test_message_inside_sysex():
    """Non-realtime message inside sysex should reset the parser."""
    assert tokenize([0xf0, 0x90, 1, 2, 0xf7]) == [[0x90, 1, 2]]


def test_sysex_inside_sysex():
    """Sysex inside sysex should reset the parser."""
    assert tokenize([0xf0, 1, 0xf0, 2, 0xf7]) == [[0xf0, 2, 0xf7]]


def test_stray_data_bytes():
    """Data bytes outside messages should be ignored."""
    assert tokenize([0, 1, 0x90, 2, 3, 4, 5, 0xf8, 6]) == [[0x90, 2, 3], [0xf8]]
