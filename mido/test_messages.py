import sys
from pytest import raises

from .messages import Message, check_time, get_spec
from .messages import MIN_PITCHWHEEL, MAX_PITCHWHEEL
from .parser import Parser, parse, parse_all

PY2 = (sys.version_info.major == 2)

def test_msg_equality():
    args = dict(type='note_on', channel=1, note=2, velocity=3)
    assert Message(**args) == Message(**args)
    assert Message(time=1, **args) != Message(time=2, **args)

def test_set_type():
    with raises(AttributeError):
        Message('note_on').type = 'note_off'

def test_pitchwheel():
    """Check if pitchwheel type check and encoding is working."""
    msg = Message('pitchwheel', pitch=MIN_PITCHWHEEL)
    bytes = msg.bytes()
    assert bytes[1] == bytes[2]

    msg = Message('pitchwheel', pitch=MAX_PITCHWHEEL)
    bytes = msg.bytes()
    assert bytes[1] == bytes[2] == 127

def test_pitchwheel_encode_parse():
    """Encode and parse pitchwheel with value=0."""
    wheel = Message('pitchwheel', pitch=0)
    assert wheel == parse(wheel.bytes())

def test_quarter_frame_encode_parse():
    """Encode and parse quarter_frame."""
    frame = Message('quarter_frame', frame_type=1, frame_value=2)
    assert frame == parse(frame.bytes())

def test_sysex():
    sysex = Message('sysex', data=(1, 2, 3, 4, 5))
    assert sysex == parse(sysex.bytes())

def test_check_time():
    check_time(1)
    check_time(1.5)

    if PY2:
        # long should be allowed. (It doesn't exist in Python3,
        # so there's no need to check for it here.)
        check_time(long('9829389283L'))

    with raises(TypeError): check_time(None)
    with raises(TypeError): check_time('abc')

    with raises(TypeError): check_time(None)
    with raises(TypeError): check_time('abc')

def test_check_channel():
    from .messages import check_channel

    check_channel(0)
    check_channel(15)
    with raises(TypeError): check_channel(None)
    with raises(TypeError): check_channel('abc')
    with raises(TypeError): check_channel(0.5)
    with raises(ValueError): check_channel(-1)
    with raises(ValueError): check_channel(16)

def test_check_pos():
    from .messages import check_pos, MIN_SONGPOS, MAX_SONGPOS

    check_pos(0)
    check_pos(MIN_SONGPOS)
    check_pos(MAX_SONGPOS)
    with raises(TypeError): check_pos(None)
    with raises(TypeError): check_pos('abc')
    with raises(ValueError): check_pos(MIN_SONGPOS - 1)
    with raises(ValueError): check_pos(MAX_SONGPOS + 1)

def test_check_pitch():
    from .messages import check_pitch, MIN_PITCHWHEEL, MAX_PITCHWHEEL

    # Pitchwheel pitch
    check_pitch(MIN_PITCHWHEEL)
    check_pitch(MAX_PITCHWHEEL)
    with raises(TypeError): check_pitch(None)
    with raises(TypeError): check_pitch(0.5)
    with raises(TypeError): check_pitch('abc')
    with raises(ValueError): check_pitch(MIN_PITCHWHEEL - 1)
    with raises(ValueError): check_pitch(MAX_PITCHWHEEL + 1)

def test_check_data():
    from .messages import check_data

    # check_data() should return the data as a tuple.
    assert type(check_data([0, 1, 2]) == tuple)
    assert check_data([0, 1, 2]) == (0, 1, 2)
    assert check_data(i for i in [1, 2, 3]) == (1, 2, 3)

    with raises(TypeError): check_data(1)
    with raises(TypeError): check_data(('a', 'b', 'c'))
    with raises(ValueError): check_data((-1, -2, -3))

def test_check_frame_type():
    from .messages import check_frame_type

    # Qarter frame type
    check_frame_type(0)
    check_frame_type(7)
    with raises(TypeError): check_frame_type(None)
    with raises(TypeError): check_frame_type(0.5)
    with raises(ValueError): check_frame_type(-1)
    with raises(ValueError): check_frame_type(8)

def test_check_databyte():
    from .messages import check_databyte

    # Data byte
    check_databyte(0)
    check_databyte(15)
    with raises(TypeError): check_databyte(None)
    with raises(TypeError): check_databyte(0.5)
    with raises(ValueError): check_databyte(-1)
    with raises(ValueError): check_databyte(128)

def test_encode_channel():
    from .messages import encode_channel

    # Channel should be ignored, and an empty list returned.
    # Thus, there is no reason to check for TypeError
    # and ValueError.
    assert encode_channel(channel=0) == []

def test_encode_data():
    from .messages import encode_data

    # Note: encode_data() includes the sysex end byte (0xf7) to avoid a
    # special case in bytes().
    assert encode_data([1, 2, 3]) == [1, 2, 3, 0xf7]

def test_encode_():
    from .messages import encode_pitch, MIN_PITCHWHEEL, MAX_PITCHWHEEL

    # Pitchwheel pitch
    assert encode_pitch(MIN_PITCHWHEEL) == [0, 0]
    assert encode_pitch(MAX_PITCHWHEEL) == [127, 127]
    assert encode_pitch(0) == [0, 64]

def test_encode_pos():
    from .messages import encode_pos, MIN_SONGPOS, MAX_SONGPOS

    assert encode_pos(MIN_SONGPOS) == [0, 0]
    assert encode_pos(MAX_SONGPOS) == [127, 127]
    # Check endian
    assert [16, 78] == encode_pos(10000)

def test_get_spec():
    from .messages import get_spec

    assert get_spec('note_on').type == 'note_on'
    assert get_spec(0x80).type == 'note_off'
    assert get_spec(0x82).type == 'note_off'

    with raises(LookupError): get_spec(-1)
    with raises(LookupError): get_spec(0)
    with raises(LookupError): get_spec('banana')

def test_sysex_data_type():
    """Is messages.data turned into a tuple?"""
    data = range(1)

    message = Message('sysex')
    message.data = data
    assert isinstance(message.data, tuple)

    message = Message('sysex', data=data)
    assert isinstance(message.data, tuple)

    a = Message('sysex', data=(1, 2))
    b = parse(a.bytes())
    assert isinstance(b.data, tuple)

def test_copy():
    orig = Message('note_on', note=22, time=123)
    copy = orig.copy()

    assert orig == copy
    assert orig.time == copy.time
    assert vars(orig) == vars(copy)

    copy = orig.copy(velocity=1)
    orig.velocity = 1

    assert orig == copy

def test_copy_invalid_attribute():
    orig = Message('note_on')
    valid_spec = get_spec('note_on')

    # Pass arguments with invalid names.
    with raises(ValueError): orig.copy(_spec=valid_spec)
    with raises(ValueError): orig.copy(type='continue')
    with raises(ValueError): orig.copy(banana=1)

    # Valid arguments should pass.
    orig.copy(note=0, velocity=0, time=0)

def test_set_invalid_attribute():
    """Set an attribute that is not settable."""
    valid_spec = get_spec('note_on')
    msg = Message('note_on')

    with raises(AttributeError): msg._spec = valid_spec
    with raises(AttributeError): msg.type = 'continue'
    with raises(AttributeError): msg.invalid = 'banana'
