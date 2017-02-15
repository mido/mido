from pytest import raises
from .specs import MIN_PITCHWHEEL, MAX_PITCHWHEEL, MIN_SONGPOS, MAX_SONGPOS
from .messages import Message, SysexData

def test_msg_time_equality():
    # Since 1.1.18 time is included in comparison.
    assert Message('clock', time=0) == Message('clock', time=0)
    assert Message('clock', time=0) != Message('clock', time=1)


def test_set_type():
    """Can't change the type of a message."""
    with raises(AttributeError):
        Message('note_on').type = 'note_off'


def test_encode_pitchwheel():
    assert 'E0 00 00' == Message('pitchwheel', pitch=MIN_PITCHWHEEL).hex()
    assert 'E0 00 40' == Message('pitchwheel', pitch=0).hex()
    assert 'E0 7F 7F' == Message('pitchwheel', pitch=MAX_PITCHWHEEL).hex()


def test_decode_pitchwheel():
    assert Message.from_hex('E0 00 00').pitch == MIN_PITCHWHEEL
    assert Message.from_hex('E0 00 40').pitch == 0
    assert Message.from_hex('E0 7F 7F').pitch == MAX_PITCHWHEEL


def test_encode_songpos():
    assert 'F2 00 00' == Message('songpos', pos=MIN_SONGPOS).hex()
    assert 'F2 7F 7F' == Message('songpos', pos=MAX_SONGPOS).hex()


def test_decode_songpos():
    assert Message.from_hex('F2 00 00').pos == MIN_SONGPOS
    assert Message.from_hex('F2 7F 7F').pos == MAX_SONGPOS


def test_sysex_data_is_sysexdata_object():
    assert isinstance(Message.from_hex('F0 00 F7').data, SysexData)


def test_sysex_data_accepts_different_types():
    assert Message('sysex', data=(0, 1, 2)).data == (0, 1, 2)
    assert Message('sysex', data=[0, 1, 2]).data == (0, 1, 2)
    assert Message('sysex', data=range(3)).data == (0, 1, 2)
    assert Message('sysex', data=bytearray([0, 1, 2])).data == (0, 1, 2)
    assert Message('sysex', data=b'\x00\x01\x02').data == (0, 1, 2)


def test_copy():
    assert Message('start').copy(time=1) == Message('start', time=1)


def test_init_invalid_argument():
    with raises(ValueError):
        Message('note_on', zzzzzzzzzzzz=2)

    with raises(ValueError):
        # note_on doesn't take program.
        Message('note_on', program=2)


def test_copy_invalid_argument():
    with raises(ValueError):
        Message('note_on').copy(zzzzzzzzzzzz=2)

    with raises(ValueError):
        # note_on doesn't take program.
        Message('note_on').copy(program=2)


def test_copy_cant_change_type():
    with raises(ValueError):
        Message('start').copy(type='stop')


def test_copy_can_have_same_type():
    Message('start').copy(type='start')


def test_compare_with_nonmessage():
    with raises(TypeError):
        Message('clock') == 'not a message'


def test_from_dict_default_values():
    msg = Message('note_on', channel=0, note=0, time=0)
    data = {'type': 'note_on'}
    assert Message.from_dict(data) == msg


def test_dict_sysex_data():
    msg = Message('sysex', data=(1, 2, 3))
    data = msg.dict()
    assert data == {'type': 'sysex', 'data': [1, 2, 3], 'time': 0}
    assert type(data['data']) == type([])

