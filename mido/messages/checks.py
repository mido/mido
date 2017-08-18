from numbers import Integral, Real
from .specs import (SPEC_BY_TYPE, MIN_SONGPOS, MAX_SONGPOS,
                    MIN_PITCHWHEEL, MAX_PITCHWHEEL,
                    MIN_PITCHWHEEL_LARGE, MAX_PITCHWHEEL_LARGE)
from ..py2 import convert_py2_bytes


# If set to False, data bytes must be in the range 0..127.
# If set to True, data bytes must by in the range 0..255.
ALLOW_DATA_LARGE_BYTES = False

# If set to to False, pitch wheel range must be between MIN_PITCHWHEEL and
# MAX_PITCHWHEEL
# If set to to True, pitch wheel range must be between MIN_PITCHWHEEL_LARGE and
# MAX_PITCHWHEEL_LARGE
ALLOW_LARGE_PITCHWHEEL_RANGE = False

def check_type(type_):
    if type_ not in SPEC_BY_TYPE:
        raise ValueError('invalid message type {!r}'.format(type_))


def check_channel(channel):
    if not isinstance(channel, Integral):
        raise TypeError('channel must be int')
    elif not 0 <= channel <= 15:
        raise ValueError('channel must be in range 0..15')


def check_pos(pos):
    if not isinstance(pos, Integral):
        raise TypeError('song pos must be int')
    elif not MIN_SONGPOS <= pos <= MAX_SONGPOS:
        raise ValueError('song pos must be in range {}..{}'.format(
                         MIN_SONGPOS, MAX_SONGPOS))


def check_pitch(pitch):
    if not isinstance(pitch, Integral):
        raise TypeError('pitchwheel value must be int')
    elif ALLOW_LARGE_PITCHWHEEL_RANGE and (
        not MIN_PITCHWHEEL_LARGE <= pitch <= MAX_PITCHWHEEL_LARGE):
        raise ValueError('pitchwheel value must be in range {}..{}'.format(
                         MIN_PITCHWHEEL_LARGE, MAX_PITCHWHEEL_LARGE))
    elif not ALLOW_LARGE_PITCHWHEEL_RANGE and (
        not MIN_PITCHWHEEL <= pitch <= MAX_PITCHWHEEL):
        raise ValueError(
            'pitchwheel value must be in range {}..{}. Other values violate '
            'the MIDI spec. However, if this is intentional, you may override '
            'this check by setting '
            'mido.messages.checks.ALLOW_LARGE_PITCHWHEEL_RANGE to True.'.format(
                         MIN_PITCHWHEEL, MAX_PITCHWHEEL))


def check_data(data_bytes):
    for byte in convert_py2_bytes(data_bytes):
        check_data_byte(byte)


def check_frame_type(value):
    if not isinstance(value, Integral):
        raise TypeError('frame_type must be int')
    elif not 0 <= value <= 7:
        raise ValueError('frame_type must be in range 0..7')


def check_frame_value(value):
    if not isinstance(value, Integral):
        raise TypeError('frame_value must be int')
    elif not 0 <= value <= 15:
        raise ValueError('frame_value must be in range 0..15')


def check_data_byte(value):
    if not isinstance(value, Integral):
        raise TypeError('data byte must be int')
    elif ALLOW_DATA_LARGE_BYTES and not 0 <= value <= 255:
        raise ValueError('data byte must be in range 0..255')
    elif not ALLOW_DATA_LARGE_BYTES and not 0 <= value <= 127:
        raise ValueError(
            'data byte must be in range 0..127. Values > 127 violate the MIDI '
            'spec. However, if this is intentional, you may override this '
            'check by setting mido.messages.checks.ALLOW_DATA_LARGE_BYTES to '
            'True.')


def check_time(time):
    if not isinstance(time, Real):
        raise TypeError('time must be int or float')


_CHECKS = {
    'type': check_type,
    'data': check_data,
    'channel': check_channel,
    'control': check_data_byte,
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


def check_value(name, value):
    _CHECKS[name](value)


def check_msgdict(msgdict):
    spec = SPEC_BY_TYPE.get(msgdict['type'])
    if spec is None:
        raise ValueError('unknown message type {!r}'.format(msgdict['type']))

    for name, value in msgdict.items():
        if name not in spec['attribute_names']:
            raise ValueError(
                '{} message has no attribute {}'.format(spec['type'], name))

        check_value(name, value)
