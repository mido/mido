from collections import deque
from .defs import SYSEX_START, SYSEX_END
from .defs import _MSG_DEFS_BY_STATUS_BYTE
from .defs import CHANNEL_MESSAGES, REALTIME_MESSAGES
from .defs import VALID_BYTES, VALID_DATA_BYTES
from .defs import MIN_PITCHWHEEL, MAX_PITCHWHEEL


def check_data_byte(byte):
    if byte not in VALID_DATA_BYTES:
        raise ValueError('invalid data byte')


def check_data(data):
    for byte in data:
        check_data_byte(byte)


def _decode_sysex_data(data):
    return {'data': bytes(data)}


def _decode_quarter_frame_data(data):
    return {'frame_type': data[0] >> 4,
            'frame_value' : data[0] & 15}


def _decode_songpos_data(data):
    return {'pos': data[0] | (data[1] << 7)}


def _decode_pitchwheel_data(data):
    # Todo: implement.
    return {'pitch': data[0] | ((data[1] << 7) + MIN_PITCHWHEEL)}


_SPECIAL_CASES = {
    0xe0: _decode_pitchwheel_data,
    0xf0: _decode_sysex_data,
    0xf1: _decode_quarter_frame_data,
    0xf2: _decode_songpos_data,
    # + pitchwheel
}


def _decode_data_bytes(status_byte, data, msgdef):
    # Subtract 1 for status byte.
    if len(data) != (msgdef['length'] - 1):
        raise ValueError(
            'wrong number of bytes for {} message'.format(msgdef['type']))

    # Todo: better name than args?
    names = [name for name in msgdef['value_names'] if name != 'channel']
    args = {name: value for name, value in zip(names, data)}

    if status_byte in CHANNEL_MESSAGES:
        # Channel is stored in the lower nibble of the status byte.
        args['channel'] = status_byte & 0x0f

    return args


def decode_msg(midi_bytes, *, time=0, data_bytes_checked=False):
    """Decode message bytes and return messages as a dictionary.

    Raises ValueError if the bytes are out of range or the message is
    invalid.
    """
    # Todo: this function is getting long.

    if len(midi_bytes) == 0:
        raise ValueError('message is 0 bytes long')

    status_byte, *data = midi_bytes

    try:
        msgdef = _MSG_DEFS_BY_STATUS_BYTE[status_byte]
    except KeyError:
        raise ValueError('invalid status byte {!r}'.format(status_byte))

    msg = {
        'type': msgdef['type'],
        'time': time,
    }

    # Sysex.
    if status_byte == SYSEX_START:
        *data, end = data
        if end != SYSEX_END:
            raise ValueError('invalid sysex end byte {!r}'.format(end))

    if not data_bytes_checked:
        check_data(data)

    if status_byte in _SPECIAL_CASES:
        msg.update(_SPECIAL_CASES[status_byte](data))
    else:
        msg.update(_decode_data_bytes(status_byte, data, msgdef))

    return msg


class Decoder:
    """
    Encodes MIDI message bytes to dictionaries.
    """
    def __init__(self, data=None):
        """Create a new decoder."""
        self.messages = deque()
        self._reset()
        if data is not None:
            self.feed(data)

    def _reset(self):
        self._bytes = []
        self._len = -1
        self._in_msg = False
        self._in_sysex = False

    def _deliver(self, msg=None):
        if msg is None:
            msg = decode_msg(self._bytes, data_bytes_checked=True)
        self.messages.append(msg)


    def _handle_status_byte(self, byte):
        msgdef = _MSG_DEFS_BY_STATUS_BYTE.get(byte)

        if self._in_sysex and byte in REALTIME_MESSAGES:
            if msgdef:
                self._deliver(decode_msg([byte]))
        elif byte == SYSEX_END:
            if self._in_sysex:
                self._bytes.append(SYSEX_END)
                self._deliver()
                self._reset()
            else:
                self._reset()
        elif msgdef:
            # Start new message.
            self._in_msg = True
            self._in_sysex = (byte == SYSEX_START)
            self._len = msgdef['length']
            self._bytes = [byte]
        else:
            # Ignore message.
            self._reset()

    def _handle_data_byte(self, byte):
        if self._in_msg:
            self._bytes.append(byte)

    def feed_byte(self, byte):
        """Feed MIDI byte to the decoder.

        Takes an int in range [0..255].
        """

        if byte in VALID_DATA_BYTES:
            self._handle_data_byte(byte)
        elif byte in VALID_BYTES:
            self._handle_status_byte(byte)
        else:
            raise ValueError('invalid byte value {!r}'.format(byte))

        if len(self._bytes) == self._len:
            self._deliver()
            self._reset()

    def feed(self, data):
        """Feed MIDI bytes to the decoder.

        Takes an iterable of ints in in range [0..255].
        """
        for byte in data:
            self.feed_byte(byte)

    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        """Yield messages that have been parsed so far."""
        while len(self.messages):
            yield self.messages.popleft()
