from mido.tokenizer import Tokenizer


def tokenize(midi_bytes):
    return list(Tokenizer(midi_bytes))


def test_channel_message():
    assert tokenize([0x90, 1, 2]) == [[0x90, 1, 2]]


def test_running_status():
    """The last known status byte should be reused if omitted in a message."""
    assert tokenize([0x9a, 3, 127, 3, 64, 3, 0, 0xb0, 2, 3, 4, 5]) == [
        [0x9a, 3, 127], [0x9a, 3, 64], [0x9a, 3, 0],
        [0xb0, 2, 3], [0xb0, 4, 5]
    ]


def test_running_status_interruption():
    """Running status shall be reset by system common messages and invalid data bytes ignored."""
    assert tokenize([0x9a, 3, 127, 3, 64, 0xf6, 3, 0, 0xb0, 2, 3, 4, 5]) == [
        [0x9a, 3, 127], [0x9a, 3, 64], [0xf6],
        [0xb0, 2, 3], [0xb0, 4, 5]
    ]


def test_running_status_common():
    """The last known status byte should not be reused with common or exclusive message"""
    assert tokenize([0xf3, 1, 2]) != [
        [0xf3, 1], [0xf3, 2]
    ]


def test_sysex():
    assert tokenize([0xf0, 1, 2, 3, 0xf7]) == [[0xf0, 1, 2, 3], [0xf7]]


def test_empty_sysex():
    assert tokenize([0xf0, 0xf7]) == [[0xf0], [0xf7]]


def test_realtime():
    assert tokenize([0xf8]) == [[0xf8]]


def test_double_realtime():
    assert tokenize([0xf8, 0xf8]) == [[0xf8], [0xf8]]


def test_realtime_inside_message():
    """Realtime message inside message should not interrupt running status."""
    assert tokenize([0x90, 1, 0xf8, 2]) == [[0xf8], [0x90, 1, 2]]


def test_realtime_inside_sysex():
    """Realtime messages are allowed inside sysex.

    The realtime messages should be delivered first since it has the highest priority, hence its name.
    """
    assert tokenize([0xf0, 1, 0xf8, 2, 0xf7]) == [[0xf8], [0xf0, 1, 2], [0xf7]]
    assert tokenize([0xf0, 0xf8, 0xf7]) == [[0xf8], [0xf0], [0xf7]]


def test_message_inside_sysex():
    """Non-realtime message inside sysex should end the sysex message."""
    assert tokenize([0xf0, 0x90, 1, 2, 0xf7]) == [[0xf0], [0x90, 1, 2], [0xf7]]


def test_sysex_inside_sysex():
    """Sysex inside sysex should end the first sysex message and start a new one."""
    assert tokenize([0xf0, 1, 0xf0, 2, 0xf7]) == [[0xf0, 1], [0xf0, 2], [0xf7]]


def test_stray_data_bytes():
    """Data bytes outside messages should be ignored."""
    assert tokenize([0, 1, 0x90, 2, 3, 0xf8]) == [[0x90, 2, 3], [0xf8]]
