def isint(val):
    """Check if a value is an integer"""
    # Todo: is there a better way to check this?
    return isinstance(val, int)

def isnum(val):
    """Check if a value is a number"""
    # Todo: is there a better way to check this?
    return isinstance(val, int) or isinstance(val, float) or isinstance(val, long)




def isopcode(val):
    """Returns True if the byte is an opcode"""
    return isint(val) and (128 <= val <= 255)

def isdata(val):
    """Returns True if the byte is a data byte"""
    return isint(val) and (0 <= val <= 127)


#
# Basic MIDI bytes
#
# Bytes with the high bit set are opcodes, and start a new message.
# That's why MIDI data bytes are only 7 bits.
#
#    opcode bytes are >= 128
#    data bytes are < 128
#

def assert_opcode(val):
    if not isopcode(val):
        raise ValueError('MIDI opcode must be int in range [128 .. 255] (was %s)' % repr(val))

def assert_data(val):
    if not isdata(val):
        raise ValueError('MIDI data byte must an in range [0 .. 127] (was %s)' % repr(val))


#
# Data values
#

def assert_time(time):
    if not isnum(time):
        raise ValueError('MIDI time value must be number (was %s)' % repr(time))

def assert_chan(val):
    if not isint(val) or not (0 <= val <= 15):
        raise ValueError('MIDI channel must be int in range [0 .. 15] (was %s)' % repr(val))

# Todo: fix range (should be 14 bit unsigned)
def assert_songpos(val):
    if not isint(val) or not (0 <= val <= 127):
        raise ValueError('MIDI data byte must be int in range [0 .. 127] (was %s)' % repr(val))

def assert_pitchwheel(val):
    if not isnum(val) or not (-1 <= val <= 1):
        raise ValueError('MIDI pitch wheel must be number in range [-1 .. 1] (was %s)' % repr(val))
