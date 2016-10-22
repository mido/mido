"""Definitions and lookup tables for MIDI messages.

Todo:

    * add lookup functions for messages definitions by type and status
      byte.
"""
CHANNEL_MESSAGES = set(range(0x80, 0xf0))
COMMON_MESSAGES = set(range(0xf0, 0xf8))
REALTIME_MESSAGES = set(range(0xf8, 0x100))

SYSEX_START = 0xf0
SYSEX_END = 0xf7

# Pitchwheel is a 14 bit signed integer
MIN_PITCHWHEEL = -8192
MAX_PITCHWHEEL = 8191

# Song pos is a 14 bit unsigned integer
MIN_SONGPOS = 0
MAX_SONGPOS = 16383


VALID_BYTES = set(range(0, 256))
VALID_DATA_BYTES = set(range(0, 128))


def _make_msgdef_lookups(msgdefs):
    by_status_byte = {}
    by_type = {}

    for msgdef in msgdefs:
        type_ = msgdef['type']
        status_byte = msgdef['status_byte']

        by_type[type_] = msgdef

        if status_byte in CHANNEL_MESSAGES:
            for channel in range(16):
                by_status_byte[status_byte | channel] = msgdef
        else:
            by_status_byte[status_byte] = msgdef
                
    return by_status_byte, by_type


def _defmsg(status_byte, type_, value_names, length):
    return {
        'status_byte': status_byte,
        'type': type_,
        'value_names': value_names,
        'length': length,
    }


_MSG_DEFS = [
    _defmsg(0x80, 'note_off', ('channel', 'note', 'velocity'), 3),
    _defmsg(0x90, 'note_on', ('channel', 'note', 'velocity'), 3),
    _defmsg(0xa0, 'polytouch', ('channel', 'note', 'value'), 3),
    _defmsg(0xb0, 'control_change', ('channel', 'control', 'value'), 3),
    _defmsg(0xc0, 'program_change', ('channel', 'program',), 2),
    _defmsg(0xd0, 'aftertouch', ('channel', 'value',), 2),
    _defmsg(0xe0, 'pitchwheel', ('channel', 'pitch',), 3),
    
    # System common messages.
    # 0xf4 and 0xf5 are undefined.
    _defmsg(0xf0, 'sysex', ('data',), float('inf')),
    _defmsg(0xf1, 'quarter_frame', ('frame_type', 'frame_value'), 2),
    _defmsg(0xf2, 'songpos', ('pos',), 3),
    _defmsg(0xf3, 'song_select', ('song',), 2),
    _defmsg(0xf6, 'tune_request', (), 1),
    
    # System real time messages.
    # 0xf9 and 0xfd are undefined.
    _defmsg(0xf8, 'clock', (), 1),
    _defmsg(0xfa, 'start', (), 1),
    _defmsg(0xfb, 'continue', (), 1),
    _defmsg(0xfc, 'stop', (), 1),
    _defmsg(0xfe, 'active_sensing', (), 1),
    _defmsg(0xff, 'reset', (), 1),
]

# These must be separate tables to prevent Message(0x90) from being legal.
_MSG_DEFS_BY_STATUS_BYTE, _MSG_DEFS_BY_TYPE = _make_msgdef_lookups(_MSG_DEFS)


DEFAULT_VALUES = {
    'channel': 0,
    'control': 0,
    'data': b'',
    'frame_type': 0,
    'frame_value': 0,
    'note': 0,
    'pitch': 0,
    'pos': 0,
    'program': 0,
    'song': 0,
    'value': 0,
    'velocity': 64,

    'time': 0,
}


# Todo: why is this not in decode.py?

def make_msgdict(type_, **args):
    """Return a new message.

    Returns a dictionary representing a message.

    Message values can be overriden.

    Todo: add 'strict' option that will check types and values
    of arguments.
    """
    if type_ in _MSG_DEFS_BY_TYPE:
        msgdef = _MSG_DEFS_BY_TYPE[type_]
    else:
        raise LookupError('Unknown message type {!r}'.format(type_))

    msg = {'type': type_}

    # Add default values.
    for name in msgdef['value_names']:
        msg[name] = DEFAULT_VALUES[name]
    msg['time'] = DEFAULT_VALUES['time']

    # for name in args:
    #     if name not in msgdef['value_names']:
    #         raise ValueError('

    msg.update(args)

    return msg


def test_make_msgdict():
    assert make_msgdict('clock') == dict(type=clock, time=0)
