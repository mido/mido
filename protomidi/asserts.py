def isint(val):
    """Check if a value is an integer"""
    # Todo: is there a better way to check this?
    return isinstance(val, int)

def isnum(val):
    """Check if a value is a number"""
    # Todo: is there a better way to check this?
    return isinstance(val, int) or isinstance(val, float) or isinstance(val, long)


#
# Assert that data values as of correct type and size
#
def assert_time(time):
    if not isnum(time):
        raise ValueError('time must be a number')

def assert_channel(val):
    if not isint(val) or not (0 <= val < 16):
        raise ValueError('channel must be integer in range(0, 16)')

# Todo: fix range (should be 14 bit unsigned)
def assert_songpos(val):
    if not isint(val) or not (0 <= val < 32768):
        raise ValueError('song position must be integer in range(0, 32768)')

def assert_pitchwheel(val):
    if not isnum(val) or not (-1 <= val <= 1):
        raise ValueError('pitchwheel value must be number in range(-1, 1)')

def assert_databyte(val):
    if not isint(val) or not (0 <= val <= 128):
        raise ValueError('data byte must by in range range(0, 128)')
