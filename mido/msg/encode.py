from collections import ChainMap
from .defs import SYSEX_START, SYSEX_END, CHANNEL_MESSAGES, VALID_DATA_BYTES
# Todo: there should be a function instead.
from .defs import _MSG_DEFS_BY_TYPE, DEFAULT_VALUES

def _encode_pitchwheel_data(msg):
    pitch = msg['pitch'] - MIN_PITCHWHEEL
    return bytes([pitch & 0x7f, pitch >> 7])


def _encode_sysex_data(msg):
    return bytes(msg['bytes']) + SYSEX_END


def _encode_quarter_frame_data(msg):
    return bytes([msg['frame_type'] << 4 | msg['frame_value']])


def _encode_songpos_data(data):
    pos = data['pos']
    return bytes([pos & 0x7f, pos >> 7])


_SPECIAL_CASES = {
    0xe0: _encode_pitchwheel_data,
    0x70: _encode_sysex_data,
    0xf1: _encode_quarter_frame_data,
    0xf2: _encode_songpos_data,
}


def encode_msg(msg):
    """Encode msg dict as bytes.

    Todo: Add type and value checking.
          (Can be turned off with keyword argument.)
    """
    msgdef = _MSG_DEFS_BY_TYPE[msg['type']]
    status_byte = msgdef['status_byte']

    msg = ChainMap(msg, DEFAULT_VALUES)

    if status_byte in CHANNEL_MESSAGES:
        status_byte |= msg['channel']

    if status_byte in _SPECIAL_CASES:
        data = _SPECIAL_CASES[status_byte](msg)
    else:
        data = bytes(msg[name] for name in msgdef['value_names']
                     if name != 'channel')
 
    return bytes([status_byte]) + data
