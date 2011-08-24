"""
A simple MIDI library

Ole Martin Bjorndalen
ombdalen@gmail.com
http://nerdly.info/ole/
"""

# Channel messages
NOTE_OFF         = 0x80
NOTE_ON          = 0x90
POLY_PRESSURE    = 0xa0
CONTROL_CHANGE   = 0xb0
PROGRAM_CHANGE   = 0xc0
CHANNEL_PRESSURE = 0xd0
PITCH_WHEEL      = 0xe0

# System common messages
# (Underfined messages (0xf1, ...) are not listed)
SYSEX            = 0xf0
SONG_POSITION    = 0xf2
SONG_SELECT      = 0xf3
TUNE_REQUEST     = 0xf6
END_OF_SYSEX     = 0xf7

TIMING_CLOCK     = 0xf8
START            = 0xfa
CONTINUE         = 0xfb
STOP             = 0xfc
ACTIVE_SENSING   = 0xfe
RESET            = 0xff


# Types not listed here take no arguments
type_args = {
    NOTE_OFF         : ['note', 'velocity'],
    NOTE_ON          : ['note', 'velocity'],
    POLY_PRESSURE    : ['note', 'velocity'],
    CONTROL_CHANGE   : ['control', 'value'],
    PROGRAM_CHANGE   : ['program'],
    CHANNEL_PRESSURE : ['pressure'],
    PITCH_WHEEL      : ['lo', 'hi'],

    # 0xf0 : ['device'],  # + data until 0xf7
    0xf2 : ['lo', 'hi'],
    0xf3 : ['song'],
    }

type_name = {
    0x80 : 'note_off',
    0x90 : 'note_on',
    0xa0 : 'poly_pressure',
    0xb0 : 'control_change',
    0xc0 : 'program_change',
    0xd0 : 'channel_pressure',
    0xe0 : 'pitch_wheel',

    0xf0 : 'sysex',
    0xf1 : '*undefined',
    0xf2 : 'song_position',
    0xf3 : 'song_select',
    0xf4 : '*undefined',
    0xf5 : '*undefined',
    0xf6 : 'tune_request',
    0xf7 : 'end_of_sysex',

    0xf8 : 'timing_clock',
    0xf9 : '*undefined',
    0xfa : 'start',
    0xfb : 'continue',
    0xfc : 'stop',
    0xfd : '*undefined',
    0xfe : 'active_sensing',
    0xff : 'reset',
    }

# System messages have a the channel set to -1
# to you can tell them apart.
CHANNEL_SYSTEM = -1

class MidiMsg:
    """A MIDI message"""
    def __init__(self, type, channel, **kw):
        self.type = type
        self.channel = channel

        if self.type == SYSEX:
            self.data = []

        self.__dict__.update(kw)

    def __repr__(self):
        name = type_name[self.type]
        d = repr(self.__dict__)
        return '<MidiMsg %s %s>' % (name, d)

    def copy(self, **kw):
        """Make a copy of the message. Also copies the sysex data (if any)."""
        msg = MidiMsg(**self.__dict__)
        if hasattr(self, 'data'):
            msg.data = self.data[:]

        # Overrides some attributes
        msg.__dict__.update(kw)

        return msg

class MidiParser:
    """
    Put bytes in and get messages out.

    add_byte(b)   adds a byte to the parser

    If a callback function is given, it is called for every message
    completed.

    If no callback is given, the message is put on in a queue,
    and you can get it with get_msg().

    Todo: make sure we don't overflow.

    Todo: decide if sysex messages should be delivered when everything has arrived
          (or let it be an option)
    """
    
    def __init__(self, callback=None):
        self._reset()
        self.messages = []  # Result

        self.callback = callback or self.put_msg
        self.sysex = None

    def _reset(self):
        self.opcode = 0    # Last opcode seen
        self.numargs = 0   # Number of arguments it needs
        self.data = []     # Data bytes collected

        self.type = 0
        self.channel = 0

    def put_msg(self, msg):
        self.messages.append(msg)

    def get_msg(self):
        """
        Get the next message. Returns None if
        there are no messages.
        """
        if self.messages:
            return self.messages.pop(0)
        else:
            return None

    def get_all(self):
        """Returns all pending messages"""
        ret = self.messages
        self.messages = []
        return ret

    def add_byte(self, b):
        """
        Add a byte to the parser. Returns the
        number of messages available for reading.
        """

        if b < 0x80:
            # print 'Data byte', b, self.sysex
            if self.opcode:
                self.data.append(b)
            elif self.sysex:
                self.sysex.data.append(b)
            else:
                # *warn?*
                pass
            
        elif b >= 0xf8:
            # Realtime message, send right away

            if self.opcode:
                if self.opcode == 0xf0:
                    # Send interleaved realtime message
                    self.callback(MidiMsg(b, -1))
                else:
                    # Not in sysex, cancel current message
                    # and send this instead
                    # *warn?*
                    self._reset()
            else:
                self.opcode = b
                self.type = b
                self.channel = -1
                self.numargs = 0

        elif b & 0xf0 == 0xf0:
            # System message
            self.opcode = b
            self.type = b
            self.channel = -1
            self.numargs = len(type_args.get(self.type, []))

        else:
            # Channel message
            self.opcode = b
            self.type = b & 0xf0
            self.channel = b & 0x0f
            self.numargs = len(type_args.get(self.type, []))

        # Have we read a whole message?
        if self.opcode:
            if len(self.data) == self.numargs:

                kw = {}

                if self.opcode == 0xf7:
                    if self.data:
                        # Todo: this assumes that we have the whole sysex
                        # How do we know?
                        # End of sysex. Send the sysex message now
                        self.type = 0xf0
                        kw['data'] = self.data
                    
                elif self.type in type_args:
                    # Add arguments
                    for name, value in zip(type_args[self.type], self.data):
                        kw[name] = value

                msg = MidiMsg(self.type, self.channel, **kw)
        
                if msg.type == SYSEX:
                    self.sysex = msg
                elif msg.type == END_OF_SYSEX:
                    # Todo: what if there's no start?
                    # msg.start = self.sysex
                    if self.sysex:
                        self.callback(self.sysex)
                        self.callback(msg)
                        self.sysex = None
                else:
                    self.callback(msg)

                self._reset()

        return len(self.messages)

    def feed(self, string):
        for c in string:
            self.add_byte(ord(c))
        return len(self.messages)

def get_bytes(msg):
    def truncate(b):
        return int(b) & 0x7f  # truncate value

    bytes = []

    if msg.channel > -1:
        channel = msg.channel % 0x0f
        opcode = msg.type | channel
    else:
        opcode = msg.type

    bytes.append(opcode)

    if msg.type == 0xf0:
        # Add data bytes and end_of_sysex
        bytes.extend([truncate(b) for b in msg.data])
        bytes.append(0xf7)

    else:
        if msg.type in type_args:
            # Add arguments
            for name in type_args[msg.type]:
                b = getattr(msg, name)
                b = truncate(b)
                bytes.append(b)

    return bytes

def serialize(msg):
    """Converts a MIDIMsg object into a byte string ready to write to the MIDI device"""
    string = ''
    for c in get_bytes(msg):
        string += chr(c)
    return string

def callback(msg):
    """A test callback"""
    print 'Got message!', msg
    print get_bytes(msg)
    print repr(serialize(msg))

class MidiIn:
    def __init__(self, file):
        self.file = file
        self.parser = MidiParser()

    def recv(self):
        """Block until a message is available and return it"""
        while 1:
            c = self.file.read(1)
            if self.parser.feed(c):
                return self.parser.get_msg()

    def __iter__(self):
        while 1:
            yield self.recv()

class MidiOut:
    def __init__(self, file):
        self.file = file

    def send(self, msg):
        """Send a message"""
        self.file.write(serialize(msg))
        self.file.flush()




#
# Message constructors
#

def note_off(channel, note, velocity):
    return MidiMsg(NOTE_OFF, channel, note=note, velocity=velocity)

def note_on(channel, note, velocity):
    return MidiMsg(NOTE_ON, channel, note=note, velocity=velocity)

def poly_pressure(channel, note, pressure):
    return MidiMsg(POLY_PRESSURE, channel, note=note, pressure=pressure)

def program_change(channel, program):
    return MidiMsg(PROGRAM_CHANGE, channel, program=program)

def control_change(channel, control, value):
    return MidiMsg(CONTROL_CHANGE, channel, control=control, value=value)

def channel_pressure(channel, pressure):
    return MidiMsg(CHANNEL_PRESSURE, channel, pressure=pressure)

def pitch_wheel(channel, lo, hi):
    return MidiMsg(PITCH_WHEEL, channel, lo=lo, hi=hi)


def sysex(bytes):
    return MidiMsg(SYSEX, -1, data=bytes)

def song_position(pos, lo, hi):
    return MidiMsg(SONG_POSITION, -1, lo=lo, hi=hi)

def song_select(pos, song):
    return MidiMsg(SONG_SELECT, -1, song=song)

def tune_request(pos):
    return MidiMsg(TUNE_REQUEST, -1)

def timing_clock(pos):
    return MidiMsg(TIMING_CLOCK, -1)

def start(pos):
    return MidiMsg(START, -1)

def stop(pos):
    return MidiMsg(STOP, -1)

def active_sensing(pos):
    return MidiMsg(ACTIVE_SENSING, -1)

def reset(pos):
    return MidiMsg(RESET, -1)
