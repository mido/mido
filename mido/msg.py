"""
msg.py - MIDI messages

http://www.midi.org/techspecs/midimessages.php

New messages are created with mido.new() or mido.Message(),
which both return a message object.
"""

from __future__ import print_function
from collections import namedtuple


# Pitchwheel is a 14 bit signed integer
PITCHWHEEL_MIN = -8192
PITCHWHEEL_MAX = 8191


Spec = namedtuple('Spec', ('status_byte', 'type', 'args', 'size'))

msg_specs = [
    #
    # MIDI message specifications
    #
    # This is the authorative definition of message types.
    #
    
    #
    # Channel messages
    # 
    # pitchwheel value is a signed integer in the range -8192 - 8191
    #
    Spec(0x80, 'note_off',        ('channel', 'note',    'velocity'), 3),
    Spec(0x90, 'note_on',         ('channel', 'note',    'velocity'), 3),
    Spec(0xa0, 'polytouch',       ('channel', 'note',    'value'),    3),
    Spec(0xb0, 'control_change',  ('channel', 'control', 'value'),    3),
    Spec(0xc0, 'program_change',  ('channel', 'program',),   3),
    Spec(0xd0, 'aftertouch',      ('channel', 'value',),    3),
    Spec(0xe0, 'pitchwheel',      ('channel', 'value',),    3),

    #
    # System common messages
    #
    # songpos.pos is 14 bit unsigned int,
    # seralized as lsb msb
    #
    # Todo: rename song to song_select?
    #
    # Sysex messages have a potentially infinite size.
    #
    Spec(0xf0, 'sysex',         ('data',),          float('inf')),
    Spec(0xf1, 'undefined_f1',  (),                 1), 
    Spec(0xf2, 'songpos',       ('pos',),           3),  
    Spec(0xf3, 'song',          ('song',),          2),
    Spec(0xf4, 'undefined_f4',  (), 1),
    Spec(0xf5, 'undefined_f5',  (), 1),
    Spec(0xf6, 'tune_request',  (), 1),
    Spec(0xf7, 'sysex_end',     (), 1),

    #
    # System realtime messages These can interleave other messages but
    # they have no data bytes, so that's OK
    #
    Spec(0xf8, 'clock',          (), 1),
    Spec(0xf9, 'undefined_f9',   (), 1),
    Spec(0xfa, 'start',          (), 1),
    # Note: 'continue' is a keyword in python, so is
    # is bound to protomidi.msg.continue_
    Spec(0xfb, 'continue',       (), 1),
    Spec(0xfc, 'stop',           (), 1),
    Spec(0xfd, 'undefined_fd',   (), 1),
    Spec(0xfe, 'active_sensing', (), 1),
    Spec(0xff, 'reset',          (), 1),
    ]

#
# Lookup tables for quick access
# You can look up by status_byte or type.
#
spec_lookup = {}
for spec in msg_specs:
    if spec.status_byte < 0xf0:
        # Channel message.
        # The upper 4 bits are message type, and
        # the lower 4 are MIDI channel.
        # We need lookup for all 16 MIDI channels.
        for channel in range(16):
            spec_lookup[spec.status_byte | channel] = spec
    else:
        spec_lookup[spec.status_byte] = spec

    spec_lookup[spec.type] = spec

del spec, channel

def assert_databyte(val):
    if not isinstance(val, int) or not (0 <= val < 128):
        raise ValueError('data byte must be and int in range(0, 128)')

class Message(object):
    """
    MIDI message class.

    New messages are created with mido.new() or mido.Message().
    Valid arguments are:

    mido.new('note_off', channel=0, note=0, velocity=0, time=0)
    mido.new('note_on', channel=0, note=0, velocity=0, time=0)
    mido.new('polytouch', channel=0, note=0, value=0, time=0)
    mido.new('control_change', channel=0, control=0, value=0, time=0)
    mido.new('program_change', channel=0, program=0, time=0)
    mido.new('aftertouch', channel=0, value=0, time=0)
    mido.new('pitchwheel', channel=0, value=0, time=0)
    mido.new('sysex', data=(), time=0)
    mido.new('undefined_f1', time=0)
    mido.new('songpos', pos=0, time=0)
    mido.new('song', song=0, time=0)
    mido.new('undefined_f4', time=0)
    mido.new('undefined_f5', time=0)
    mido.new('tune_request', time=0)
    mido.new('sysex_end', time=0)
    mido.new('clock', time=0)
    mido.new('undefined_f9', time=0)
    mido.new('start', time=0)
    mido.new('continue', time=0)
    mido.new('stop', time=0)
    mido.new('undefined_fd', time=0)
    mido.new('active_sensing', time=0)
    mido.new('reset', time=0)
    """
    
    def __init__(self, type_or_status_byte, **kw):

        try:
            spec = spec_lookup[type_or_status_byte]
        except KeyError:
            fmt = '{!r} is an invalid type name or status byte'
            raise ValueError(fmt.format(type_or_status_byte))

        status_byte = spec.status_byte

        # Get channel. Can be overrided with keyword argument.
        if status_byte < 0xf0:
            # Channel message. Split out channel from status_byte.
            default_channel = status_byte & 0x0f
            status_byte &= 0xf0
        else:
            channel = 0

        self._set('spec', spec)
        self._set('type', self.spec.type)

        # Set default values
        for name in self.spec.args:
            if name == 'data':
                self._set('data', ())
            elif name == 'channel':
                self._set('channel', default_channel)
            else:
                self._set(name, 0)
        self._set('time', 0)

        # Override attibutes with keyword arguments
        for name, value in kw.items():
            try:
                setattr(self, name, value)
            except AttributeError:
                fmt = '{!r} is an invalid keyword argument for this message type'
                raise ValueError(fmt.format(name))

        # self._set('is_chanmsg', (self.status_byte < 0xf0))

    def copy(self, **override):
        """
        Return a copy of the message. Attributes can
        be overriden by passing keyword arguments.

        msg = Message('note_on', note=20, velocity=64)  # Create a note_on
        msg2 = msg.copy(velocity=32)  # New note_on with softer velocity
        """

        # Get values from this object
        kw = {'time' : self.time}
        for name in self.spec.args:
            kw[name] = getattr(self, name)

        # Override
        kw.update(override)

        return Message(self.type, **kw)

    def _set(self, name, value):
        """
        Set an attribute, bypassing all name and type checks.
        """
        self.__dict__[name] = value

    def __setattr__(self, name, value):
        # Todo: validation

        if name in self.spec.args or name == 'time':
            if name == 'time':
                if not (isinstance(value, int) or isinstance(value, float)):
                    raise ValueError('time must be a number')

            elif name == 'channel':
                if not isinstance(value, int) or not (0 <= value < 16):
                    raise ValueError('channel must be an int in range(0, 16)')

            elif name == 'pos':
                if not isinstance(value, int) or not (0 <= value < 32768):
                    raise ValueError('song position must be an int in range(0, 32768)')

            elif name == 'pitchwheel':
                if not isinstance(value, int) or not (PITCHWHEEL_MIN <= value <= PITCHWHEEL_MAX):
                    fmt = 'pitchwheel value must be an int in range({}, {})'
                    raise ValueError(fmt.format(
                            PITCHWHEEL_MIN,
                            PITCHWHEEL_MAX))

            elif name == 'data':
                value = tuple(value)  # Make the data bytes immutable
                for byte in value:
                    assert_databyte(byte)
            else:
                assert_databyte(value)

            self.__dict__[name] = value
        else:
            fmt = '{} message has no {!r} attribute'
            raise AttributeError(fmt.format(self.type, name)) 

    def __delattr__(self, name):
        raise AttributeError('Message attributes can\'t be deleted')

    def _get_status_byte(self):
        # Add channel to status byte.
        sb = self.spec.status_byte
        if sb <= 0xf0:
            sb |= self.channel
        return sb

    status_byte = property(fget=_get_status_byte)
    del _get_status_byte

    def bytes(self):
        """
        Encode message and return as a list of bytes.
        """

        b = [self.status_byte]

        for name in self.spec.args:
            if name == 'channel':
                continue  # We already have this

            elif name == 'data':
                b.extend(self.data)

            elif self.type == 'pitchwheel' and name == 'value':
                value = self.value + (2**13)
                lsb = value & 0x7f
                msb = value >> 7
                b.append(lsb)
                b.append(msb)

            elif self.type == 'songpos' and name == 'pos':
                # Convert 14 bit value to two 7-bit values
                # Todo: check if this is correct
                lsb = msg.pos & 0x7f
                b.append(lsb)

                msb = msg.pos >> 7
                b.append(msb)
            else:
                # Ordinary data byte
                b.append(getattr(self, name))

        if self.type == 'sysex':
            # Append a sysex_end
            b.append(0xf7)

        return b

    def bin(self):
        """
        Encode message and return as a bytearray().
        """
        
        # Todo: bytearray() or bytes()
        return bytearray(self.bytes())

    def hex(self, sep=' '):
        """
        Encode message and return as a string of hex numbers,
        separated by the string sep. The default separator is
        a single space.
        """

        return sep.join(['{:02X}'.format(byte) for byte in self.bytes()])

    def __repr__(self):
        args = [repr(self.type)] 
        args += ['{}={!r}'.format(name, getattr(self, name))
                 for name in list(self.spec.args) + ['time']]
        args = ', '.join(args)
        return 'mido.Message({})'.format(args)

    def __eq__(self, other):
        """
        Compares message type and message specific attributes. (For
        example ('note_on', channel, note, velocity) The time, spec
        and status_byte attributes are not compared.
        """

        def key(msg):
            k = tuple([msg.type] + [getattr(msg, a) for a in msg.spec.args])
            return k
            
        return key(self) == key(other)

def build_signature(spec, include_type=True):
    """
    Builds a contructor signature for a message.

    This is used to create documentation.
    """

    if include_type:
        parts = [repr(spec.type)]
    else:
        parts = []

    for name in spec.args + ('time',):
        if name == 'data':
            parts.append('data=()')
        else:
            parts.append(name + '=0')

    sig = '(' + ', '.join(parts) + ')'

    return sig

def _print_signatures():
    """
    Print arguments for mido.new() for all supported message types.

    This will be used to generate documentation.
    """
    
    for spec in msg_specs:
        sig = build_signature(spec)
        print('mido.new' + sig)
