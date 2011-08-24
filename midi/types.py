def isint(val):
    """Check if a value is an integer"""
    # Todo: is there a better way to check this?
    return isinstance(val, int)

def isnum(val):
    """Check if a value is a number"""
    # Todo: is there a better way to check this?
    return isinstance(val, int) or isinstance(val, float) 

def assert_4bit(*values):
    for val in values:
        if not isint(val) or not (0 <= val <= 15):
            raise ValueError('MIDI data byte must an integer >= 0 and <= 127 (was %r)' % val)

def assert_7bit(*values):
    for val in values:
        if not isint(val) or not (0 <= val <= 127):
            raise ValueError('MIDI data byte must an integer >= 0 and <= 127 (was %r)' % val)

def assert_8bit(*values):
    for val in values:
        if not isint(val) or not (0 <= val <= 255):
            raise ValueError('MIDI data byte must an integer >= 0 and <= 127 (was %r)' % val)

def assert_time(time):
    """Check if time value is a number >= 0"""
    
    if not isnum(time) or time < 0:
        raise ValueError('MIDI time value must be a number >= 0 (was %r)' % time)

def is_chanmsg(msg):
    """Returns True if message is a channel message."""
    return msg.opcode < 0xf0
