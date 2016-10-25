from __future__ import print_function
import random
from pytest import raises

from .messages import Message
from .parser import Parser, parse, parse_all


def test_parse():
    """Parse a note_on msg and compare it to one created with Message()."""
    parsed = parse(b'\x90\x4c\x20')
    other = Message('note_on', channel=0, note=0x4c, velocity=0x20)
    assert parsed == other


def test_parse_stray_data():
    """The parser should ignore stray data bytes."""
    assert parse_all(b'\x20\x30') == []


def test_parse_stray_status_bytes():
    """The parser should ignore stray status bytes."""
    assert parse_all(b'\x90\x90\xf0') == []


def test_encode_and_parse():
    """Encode a message and then parse it.

    Should return the same message.
    """
    note_on = Message('note_on')
    assert note_on == parse(note_on.bytes())


def test_feed_byte():
    """Put various things into feed_byte()."""
    parser = Parser()

    parser.feed_byte(0)
    parser.feed_byte(255)

    with raises(TypeError):
        parser.feed_byte([1, 2, 3])
    
    with raises(ValueError):
        parser.feed_byte(-1)

    with raises(ValueError):
        parser.feed_byte(256)


def test_feed():
    """Put various things into feed()."""
    parser = Parser()

    parser.feed([])
    parser.feed([1, 2, 3])
    # Todo: add more valid types.

    with raises(TypeError):
        parser.feed(1)

    with raises(TypeError):
        parser.feed(None)

    with raises(TypeError):
        parser.feed()


def test_parse_random_bytes():
    """Parser should not crash when parsing random data."""
    randrange = random.Random('a_random_seed').randrange
    parser = Parser()
    for _ in range(10000):
        byte = randrange(256)
        parser.feed_byte(byte)


def test_parse_channel():
    """Parser should not discard the channel in channel messages."""
    assert parse([0x90, 0x00, 0x00]).channel == 0
    assert parse([0x92, 0x00, 0x00]).channel == 2


def test_one_byte_message():
    """Messages that are one byte long should not wait for data bytes."""
    messages = parse_all([0xf6])  # Tune request.
    assert len(messages) == 1
    assert messages[0].type == 'tune_request'


def test_undefined_messages():
    """The parser should ignore undefined status bytes and sysex_end."""
    messages = parse_all([0xf4, 0xf5, 0xf7, 0xf9, 0xfd])
    assert messages == []


def test_realtime_inside_sysex():
    """Realtime message inside sysex should be delivered first."""
    messages = parse_all([0xf0, 0, 0xfb, 0, 0xf7])
    assert len(messages) == 2
    assert messages[0].type == 'continue'
    assert messages[1].type == 'sysex'


def test_undefined_realtime_inside_sysex():
    """Undefined realtime message inside sysex should ignored."""
    messages = parse_all([0xf0, 0, 0xf9, 0xfd, 0, 0xf7])
    assert len(messages) == 1
    assert messages[0].type == 'sysex'


def test_encode_and_parse_all():
    """Encode and then parse all message types.

    This checks mostly for errors in the parser.
    """
    from .messages import specs

    parser = Parser()
    for type_ in sorted(specs.SPEC_BY_TYPE.keys()):
        msg = Message(type_)
        parser.feed(msg.bytes())
        parser.get_message() == msg

    assert parser.get_message() is None


def test_parser_ascii_text():
    assert parse_all(b'7 bit ASCII should not produce any messages') == []

