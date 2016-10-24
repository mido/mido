from .specs import SYSEX_START, SYSEX_END, CHANNEL_MESSAGES, VALID_DATA_BYTES
from .specs import SPEC_BY_TYPE, DEFAULT_VALUES
from .specs import MIN_PITCHWHEEL

def _encode_pitchwheel_data(msg):
    pitch = msg['pitch'] - MIN_PITCHWHEEL
    return [pitch & 0x7f, pitch >> 7]


def _encode_sysex_data(msg):
    return list(msg['data']) + [0xf7]


def _encode_quarter_frame_data(msg):
    return [msg['frame_type'] << 4 | msg['frame_value']]


def _encode_songpos_data(data):
    pos = data['pos']
    return [pos & 0x7f, pos >> 7]


_SPECIAL_CASES = {
    0xe0: _encode_pitchwheel_data,
    0xf0: _encode_sysex_data,
    0xf1: _encode_quarter_frame_data,
    0xf2: _encode_songpos_data,
}


def encode_msg(msg):
    """Encode msg dict as a list of bytes.

    Todo: Add type and value checking.
          (Can be turned off with keyword argument.)
    """
    spec = SPEC_BY_TYPE[msg['type']]
    status_byte = spec['status_byte']

    if status_byte in CHANNEL_MESSAGES:
        status_byte |= msg['channel']

    if status_byte in _SPECIAL_CASES:
        data = _SPECIAL_CASES[status_byte](msg)
    else:
        data = [msg[name] for name in spec['value_names'] if name != 'channel']
 
    return [status_byte] + data
