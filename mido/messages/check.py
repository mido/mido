import sys
from .specs import VALID_DATA_BYTES, MIN_SONGPOS, MAX_SONGPOS
from .specs import MIN_PITCHWHEEL, MAX_PITCHWHEEL
from .specs import SPEC_BY_TYPE, VALID_DATA_BYTES

PY2 = (sys.version_info.major == 2)


def check_type(type_):
    if type_ not in SPEC_BY_TYPE:
        raise ValueError('invalid message type {!r}'.format(type_))


def check_channel(channel):
    if not isinstance(channel, int):
        raise TypeError('channel must be an integer')
    elif not 0 <= channel <= 15:
        raise ValueError('channel must be in range 0..15')


def check_pos(pos):
    if not isinstance(pos, int):
        raise TypeError('song pos must be and integer')
    elif not MIN_SONGPOS <= pos <= MAX_SONGPOS:
        raise ValueError('song pos must be in range {}..{}'.format(
                         MIN_SONGPOS, MAX_SONGPOS))


def check_pitch(pitch):
    if not isinstance(pitch, int):
        raise TypeError('pichwheel value must be an integer')
    elif not MIN_PITCHWHEEL <= pitch <= MAX_PITCHWHEEL:
        raise ValueError('pitchwheel value must be in range {}..{}'.format(
                         MIN_PITCHWHEEL, MAX_PITCHWHEEL))


def check_data(data_bytes):
    if PY2 and isinstance(data_bytes, bytes):
        data_bytes = bytearray(data_bytes)

    for byte in data_bytes:
        check_data_byte(byte)


def check_frame_type(value):
    if not isinstance(value, int):
        raise TypeError('frame_type must be an integer')
    elif not 0 <= value <= 7:
        raise ValueError('frame_type must be in range 0..7')


def check_frame_value(value):
    if not isinstance(value, int):
        raise TypeError('frame_value must be an integer')
    elif not 0 <= value <= 15:
        raise ValueError('frame_value must be in range 0..15')


def check_data_byte(value):
    if not isinstance(value, int):
        raise TypeError('data byte must be an integer')
    elif not value in VALID_DATA_BYTES:
        raise ValueError('data byte must be in range 0..127')


def check_time(time):
    if not (isinstance(time, int) or isinstance(time, float)):
        raise TypeError('time must be an integer or float')


_CHECKS = {
    'type': check_type,
    'data': check_data,
    'channel': check_channel,
    'control': check_data_byte,
    'data': check_data,
    'frame_type': check_frame_type,
    'frame_value': check_frame_value,
    'note': check_data_byte,
    'pitch': check_pitch,
    'pos': check_pos,
    'program': check_data_byte,
    'song': check_data_byte,
    'value': check_data_byte,
    'velocity': check_data_byte,
    'time': check_time,
}


def check_value(name, value, ignore_unknown=False):
    if name in _CHECKS:
        _CHECKS[name](value)
    elif ignore_unknown:
        pass
    else:
        # Todo: "attribute"?
        raise ValueError('unknown message attribute {!r}'.format(name))


def check_msgdict(msgdict, ignore_unknown=False):
    # Todo: also check type
    # Todo: type must be included?
    # Todo: this must not allow 'control' in 'note_on' message for example
    for name, value in msgdict.items():
        check_value(name, value)
