from collections import deque
from numbers import Integral
from .specs import SYSEX_START, SYSEX_END
from .specs import SPEC_BY_STATUS
from .specs import CHANNEL_MESSAGES
from .specs import VALID_BYTES, VALID_DATA_BYTES
from .specs import MIN_PITCHWHEEL
from .checks import check_data
from ..py2 import convert_py2_bytes

def _decode_sysex_data(data):
    return {'data': tuple(data)}


def _decode_quarter_frame_data(data):
    return {'frame_type': data[0] >> 4,
            'frame_value' : data[0] & 15}


def _decode_songpos_data(data):
    return {'pos': data[0] | (data[1] << 7)}


def _decode_pitchwheel_data(data):
    return {'pitch': data[0] | ((data[1] << 7) + MIN_PITCHWHEEL)}


def _make_special_cases():
    cases = {
        0xe0: _decode_pitchwheel_data,
        0xf0: _decode_sysex_data,
        0xf1: _decode_quarter_frame_data,
        0xf2: _decode_songpos_data,
    }

    for i in range(16):
        cases[0xe0 | i] = _decode_pitchwheel_data

    return cases

_SPECIAL_CASES = _make_special_cases()


def _decode_data_bytes(status_byte, data, spec):
    # Subtract 1 for status byte.
    if len(data) != (spec['length'] - 1):
        raise ValueError(
            'wrong number of bytes for {} message'.format(spec['type']))

    # Todo: better name than args?
    names = [name for name in spec['value_names'] if name != 'channel']
    args = {name: value for name, value in zip(names, data)}

    if status_byte in CHANNEL_MESSAGES:
        # Channel is stored in the lower nibble of the status byte.
        args['channel'] = status_byte & 0x0f

    return args


def decode_message(msg_bytes, time=0, check=True):
    """Decode message bytes and return messages as a dictionary.

    Raises ValueError if the bytes are out of range or the message is
    invalid.

    This is not a part of the public API.
    """
    # Todo: this function is getting long.
    msg_bytes = convert_py2_bytes(msg_bytes)

    if len(msg_bytes) == 0:
        raise ValueError('message is 0 bytes long')

    status_byte = msg_bytes[0]
    data = msg_bytes[1:]

    try:
        spec = SPEC_BY_STATUS[status_byte]
    except KeyError:
        raise ValueError('invalid status byte {!r}'.format(status_byte))

    msg = {
        'type': spec['type'],
        'time': time,
    }

    # Sysex.
    if status_byte == SYSEX_START:
        if len(data) < 1:
            raise ValueError('sysex without end byte')

        end = data[-1]
        data = data[:-1]
        if end != SYSEX_END:
            raise ValueError('invalid sysex end byte {!r}'.format(end))

    if check:
        check_data(data)

    if status_byte in _SPECIAL_CASES:
        if status_byte in CHANNEL_MESSAGES:
            msg['channel'] = status_byte & 0x0f

        msg.update(_SPECIAL_CASES[status_byte](data))
    else:
        msg.update(_decode_data_bytes(status_byte, data, spec))

    return msg


class Decoder(object):
    """
    Encodes MIDI message bytes to dictionaries.

    This is not a part of the public API.
    """
    def __init__(self, data=None):
        """Create a new decoder."""

        self._status = 0
        self._bytes = []
        self._messages = deque()
        self._datalen = 0

        if data is not None:
            self.feed(data)

    def _decode_and_append(self, msg_bytes):
        self._messages.append(decode_message(msg_bytes, check=False))

    def _feed_status_byte(self, status):
        if status == SYSEX_END:
            if self._status == SYSEX_START:
                self._bytes.append(SYSEX_END)
                self._decode_and_append(self._bytes)

            self._status = 0

        elif 0xf8 <= status <= 0xff:
            if self._status != SYSEX_START:
                # Realtime messages are only allowed inside sysex
                # messages. Reset parser.
                self._status = 0

            if status in SPEC_BY_STATUS:
                self._decode_and_append([status])

        elif status in SPEC_BY_STATUS:
            # New message.
            spec = SPEC_BY_STATUS[status]

            if spec['length'] == 1:
                self._decode_and_append([status])
                self._status = 0
            else:
                self._status = status
                self._bytes = [status]
                self._len = spec['length']
        else:
            # Undefined message. Reset parser.
            # (Undefined realtime messages are handled above.)
            # self._status = 0
            pass

    def _feed_data_byte(self, byte):
        if self._status:
            self._bytes.append(byte)
            if len(self._bytes) == self._len:
                # Complete message.
                self._decode_and_append(self._bytes)
                self._status = 0
        else:
            # Ignore stray data byte.
            pass

    def feed_byte(self, byte):
        """Feed MIDI byte to the decoder.

        Takes an int in range [0..255].
        """
        if not isinstance(byte, Integral):
            raise TypeError('message byte must be integer')

        if byte in VALID_DATA_BYTES:
            self._feed_data_byte(byte)
        elif byte in VALID_BYTES:
            self._feed_status_byte(byte)
        else:
            raise ValueError('invalid byte value {!r}'.format(byte))

    def feed(self, data):
        """Feed MIDI bytes to the decoder.

        Takes an iterable of ints in in range [0..255].
        """
        for byte in convert_py2_bytes(data):
            self.feed_byte(byte)

    def __len__(self):
        return len(self._messages)

    def __iter__(self):
        """Yield messages that have been parsed so far."""
        while len(self._messages):
            yield self._messages.popleft()
