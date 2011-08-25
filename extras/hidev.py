"""
HID event parser.
"""

import struct

event_names = {
    0x00 : 'EV_SYN',
    0x01 : 'EV_KEY',
    0x02 : 'EV_REL',
    0x03 : 'EV_ABS',
    0x04 : 'EV_MSC',
    0x05 : 'EV_SW',
    0x11 : 'EV_LED',
    0x12 : 'EV_SND',
    0x14 : 'EV_REP',
    0x15 : 'EV_FF',
    0x16 : 'EV_PWR',
    0x17 : 'EV_FF_STATUS',
    0x1f : 'EV_MAX',
    }

class Event:
    def __init__(self, time, type, code, value):
        self.time = time
        self.type = type
        self.code = code
        self.value = value

    def __repr__(self):
        name = event_names.get(self.type, 'EV_UNKNOWN')
        return '<Event: %s %s (%s) %s %s>' % (self.time, name,
                                              hex(self.type), hex(self.code), hex(self.value).strip('L'))

EVENT_SIZE = 16

def parse_event(data):
    """
    struct input_event {
      struct timeval time;
      unsigned short type;
      unsigned short code;
      unsigned int value;
    };
    """
    sec, usec, type, code, value = struct.unpack('<LLHHL', data)
    tm = sec + (0.000001 * usec)
    return Event(tm, type, code, value)    

def read_event(file):
    return parse_event(file.read(EVENT_SIZE))

#
# Constants from linux/input.h
#

#
# Event types
#
EV_SYN       = 0x00
EV_KEY       = 0x01
EV_REL       = 0x02
EV_ABS       = 0x03
EV_MSC       = 0x04
EV_SW        = 0x05
EV_LED       = 0x11
EV_SND       = 0x12
EV_REP       = 0x14
EV_FF        = 0x15
EV_PWR       = 0x16
EV_FF_STATUS = 0x17
EV_MAX       = 0x1f

#
# Syncronization events
#
SYN_REPORT = 0
SYN_CONFIG = 1


#
# Relative axes
#
REL_X                   = 0x00
REL_Y                   = 0x01
REL_Z                   = 0x02
REL_RX                  = 0x03
REL_RY                  = 0x04
REL_RZ                  = 0x05
REL_HWHEEL              = 0x06
REL_DIAL                = 0x07
REL_WHEEL               = 0x08
REL_MISC                = 0x09
REL_MAX                 = 0x0f

#
# Absolute axes
#
ABS_X                   = 0x00
ABS_Y                   = 0x01
ABS_Z                   = 0x02
ABS_RX                  = 0x03
ABS_RY                  = 0x04
ABS_RZ                  = 0x05
ABS_THROTTLE            = 0x06
ABS_RUDDER              = 0x07
ABS_WHEEL               = 0x08
ABS_GAS                 = 0x09
ABS_BRAKE               = 0x0a
ABS_HAT0X               = 0x10
ABS_HAT0Y               = 0x11
ABS_HAT1X               = 0x12
ABS_HAT1Y               = 0x13
ABS_HAT2X               = 0x14
ABS_HAT2Y               = 0x15
ABS_HAT3X               = 0x16
ABS_HAT3Y               = 0x17
ABS_PRESSURE            = 0x18
ABS_DISTANCE            = 0x19
ABS_TILT_X              = 0x1a
ABS_TILT_Y              = 0x1b
ABS_TOOL_WIDTH          = 0x1c
ABS_VOLUME              = 0x20
ABS_MISC                = 0x28
ABS_MAX                 = 0x3f


BTN_DIGI                = 0x140
BTN_TOOL_PEN            = 0x140
BTN_TOOL_RUBBER         = 0x141
BTN_TOOL_BRUSH          = 0x142
BTN_TOOL_PENCIL         = 0x143
BTN_TOOL_AIRBRUSH       = 0x144
BTN_TOOL_FINGER         = 0x145
BTN_TOOL_MOUSE          = 0x146
BTN_TOOL_LENS           = 0x147
BTN_TOUCH               = 0x14a
BTN_STYLUS              = 0x14b
BTN_STYLUS2             = 0x14c
BTN_TOOL_DOUBLETAP      = 0x14d
BTN_TOOL_TRIPLETAP      = 0x14e

"""
Wacom:

BTN_TOOL_PEN
BTN_TOOL_RUBBER

BTN_TOUCH
BTN_STYLUS
BTN_STYLUS2

ABS_X
ABS_Y
ABS_PRESSURE
ABS_DISTANCE
ABS_TILT_X
ABS_TILT_Y
ABS_MISC            0x85a, 0x852, 0 (Tool ID?)

"""

if __name__ == '__main__':
    import sys
    import midi

    X_MAX = 20320
    Y_MAX = 16240
    PRESSURE_MAX = 1023
    
    #dev = open('/dev/input/wacom')
    #dev = open('/dev/input/js0')
    dev = open(sys.argv[1])

    out = midi.MidiOut('/dev/midi1')

    while 1:
        e = read_event(dev)
        print e
