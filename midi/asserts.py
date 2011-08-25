def isint(val):
    """Check if a value is an integer"""
    # Todo: is there a better way to check this?
    return isinstance(val, int)

def isnum(val):
    """Check if a value is a number"""
    # Todo: is there a better way to check this?
    return isinstance(val, int) or isinstance(val, float) 

def is_chanmsg(msg):
    """Returns True if message is a channel message."""
    return msg.opcode < 0xf0

def assert_time(time):
    if not isnum(time) or time < 0:
        raise ValueError('MIDI time value must be a number >= 0 (was %s)' % repr(time))

def assert_opcode(*values):
    if not isint(val) or not (0 <= val <= 255):
        raise ValueError('MIDI opcode byte must an int in the range [0 .. 255] (was %s)' % repr(val))

def assert_chan(val):
    if not isint(val) or not (0 <= val <= 15):
        raise ValueError('MIDI channel must be an int in the range [0 .. 15] (was %s)' % repr(val))

def assert_data(val):
    if not isint(val) or not (0 <= val <= 127):
        raise ValueError('MIDI data byte must an int in the range [0 .. 127] (was %s)' % repr(val))
