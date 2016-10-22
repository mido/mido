from .specs import VALID_DATA_BYTES, MIN_SONGPOS, MAX_SONGPOS
from .specs import MIN_PITCHWHEEL, MAX_PITCHWHEEL

def check_channel(channel):
    """Check type and value of channel.

    Raises TypeError if the value is not an integer, and ValueError if
    it is outside range 0..15.
    """
    if not isinstance(channel, int):
        raise TypeError('channel must be an integer')
    elif not 0 <= channel <= 15:
        raise ValueError('channel must be in range 0..15')


def check_pos(pos):
    """Check type and value of song position.

    Raise TypeError if the value is not an integer, and ValueError if
    it is outside range MIN_SONGPOS..MAX_SONGPOS.
    """
    if not isinstance(pos, int):
        raise TypeError('song pos must be and integer')
    elif not MIN_SONGPOS <= pos <= MAX_SONGPOS:
        raise ValueError('song pos must be in range {}..{}'.format(
                         MIN_SONGPOS, MAX_SONGPOS))


def check_pitch(pitch):
    """Raise TypeError if the value is not an integer, and ValueError
    if it is outside range MIN_PITCHWHEEL..MAX_PITCHWHEEL.
    """
    if not isinstance(pitch, int):
        raise TypeError('pichwheel value must be an integer')
    elif not MIN_PITCHWHEEL <= pitch <= MAX_PITCHWHEEL:
        raise ValueError('pitchwheel value must be in range {}..{}'.format(
                         MIN_PITCHWHEEL, MAX_PITCHWHEEL))


# Todo: it's a bit messy for this to return something.
def check_data(data_bytes):
    """Check type of data_byte and type and range of each data byte.

    Returns the data bytes as a SysexData object.

    Raises TypeError if value is not iterable.
    Raises TypeError if one of the bytes is not an integer.
    Raises ValueError if one of the bytes is out of range 0..127.
    """
    # Make the sequence immutable.
    data_bytes = bytes(data_bytes)

    for byte in data_bytes:
        check_data_byte(byte)

    return data_bytes


def check_frame_type(value):
    """Check type and value SMPTE quarter frame type.

    Raises TypeError if the value is not an integer.
    Raises ValueError if the value is out of range.
    """
    if not isinstance(value, int):
        raise TypeError('frame_type must be an integer')
    elif not 0 <= value <= 7:
        raise ValueError('frame_type must be in range 0..7')


def check_frame_value(value):
    """Check type and value of SMPTE quarter frame value.

    Raises TypeError if the value is not an integer.
    Raises ValueError if the value is out of range.
    """
    if not isinstance(value, int):
        raise TypeError('frame_value must be an integer')
    elif not 0 <= value <= 15:
        raise ValueError('frame_value must be in range 0..15')


def check_data_byte(value):
    """Raise exception of byte has wrong type or is out of range

    Raises TypeError if the byte is not an integer, and ValueError if
    it is out of range. Data bytes are 7 bit, so the valid range is
    0..127.
    """
    if not isinstance(value, int):
        raise TypeError('data byte must be an integer')
    elif not 0 <= value <= 127:
        raise ValueError('data byte must be in range 0..127')


def check_time(time):
    """Check type and value of time.
    
    Raises TypeError if value is not an integer or a float
    """
    if not (isinstance(time, int) or isinstance(time, float)):
        raise TypeError('time must be an integer or float')


_CHECKS = {
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
    if name == 'data':
        return check_data(value)
    elif name == 'type':
        # Todo: add proper check here.
        return value
    elif name in _CHECKS:
        # Check value.
        _CHECKS[name](value)
        return value
    elif ignore_unknown:
        return value
    else:
        # Todo: "attribute"?
        raise ValueError('unknown message attribute {!r}'.format(name))


def check_msgdict(msgdict, ignore_unknown=False):
    # Todo: also check type
    # Todo: type must be included?
    # Todo: this must not allow 'control' in 'note_on' message for example
    for name, value in msgdict.items():
        check_value(name, value)
