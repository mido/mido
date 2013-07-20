import struct
import select


"""
Init:

                  8 = init?
Time stamp        |
(ms since boot)   |
--+--+--+--       |  -- Button number
f0 fb 37 09 00 00 81 00
f0 fb 37 09 00 00 81 01
f0 fb 37 09 00 00 81 02
f0 fb 37 09 00 00 81 03
f0 fb 37 09 00 00 81 04
f0 fb 37 09 00 00 81 05
f0 fb 37 09 00 00 81 06
f0 fb 37 09 00 00 81 07
f0 fb 37 09 00 00 81 08
f0 fb 37 09 00 00 81 09
f0 fb 37 09 00 00 81 0a
f0 fb 37 09 00 00 81 0b
f0 fb 37 09 00 00 82 00
f0 fb 37 09 00 00 82 01
f0 fb 37 09 00 00 82 02
f0 fb 37 09 00 00 82 03
f0 fb 37 09 00 00 82 04
f0 fb 37 09 00 00 82 05
            --+--  |
              |    1 = button, 2 = 
              |
            value (little endian unsigned)

        button down
             |
98 f0 2f 09 01 00 01 00   1 down
08 fa 2f 09 00 00 01 00   1 up

2c 6a 31 09 01 00 01 01   2 down
04 73 31 09 00 00 01 01   2 up

48 bf 32 09 01 00 01 02   3 down
f8 c4 32 09 00 00 01 02   3 up


Logitech PS2-style gamepad:

   axis 0 == left stick   -left / right   (left is negative)
   axis 1 == left stick   -up / down      (up is negative)
   axis 2 == right stick  -left / right
   axis 3 == right stick  -up / down
   axis 4 == plus stick   -left / right   (when mode is off), values min/0/max
   axis 5 == plus stick   -up / down      (when mode is off, values min/0/max

The + stick has two modes. When the mode light is off, it sends axis
4/5. When mode is on, it sends axis 0/1. The values are -32767, 0, and 32767.

Other axis have values from -32767 to 32767 as well.

"""

JS_EVENT_BUTTON = 0x1
JS_EVENT_AXIS = 0x2
JS_EVENT_INIT = 0x80

def read_event(device):
    data = device.read(8)

    event = {}

    (event['time'],
     event['value'],
     event['type'],
     event['number']) = struct.unpack('IhBB', data)

    event['init'] = bool(event['type'] & JS_EVENT_INIT)
    event['type'] &= 0x7f  # Strip away the flag bits (JS_EVENT_INIT etc.)
    if event['type'] != JS_EVENT_BUTTON:
        
        event['normalized_value'] = \
            float(event['value']) / 0x7fff  # Normalize to -1..1

    event['type'] = {1: 'button', 2: 'axis'}[event['type']]
    
    return event

def read_events(device_name):
    with open(device_name, 'rb') as device:
        while 1:
            yield read_event(device)

if __name__ == '__main__':
    import sys
    import mido

    scale = range(20)
    scale = [0, 2, 5, 7, 9, 12, 14, 17, 19, 21, 24, 26, 29]
    scale = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19]

    with open('/dev/input/js0') as dev:
        with mido.open_output('SH-201 MIDI 1') as out:
            out.send(mido.Message('program_change', program=16))

        while 1:
            event = read_event(dev)
            if event['type'] == 'button':
                note = 62 + 12 + scale[event['number']]
                if event['value']:
                    out.send(mido.Message('note_on', note=note, velocity=64))
                else:
                    out.send(mido.Message('note_off', note=note, velocity=64))

            if event['type'] == 'axis':
                if event['number'] == 0:
                    pitch_scale = mido.messages.MAX_PITCHWHEEL
                    pitch = int(event['normalized_value'] * pitch_scale)
                    out.send(mido.Message('pitchwheel', pitch=pitch))
