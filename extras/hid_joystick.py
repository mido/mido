"""Read from /dev/input/js0 and return as dictionaries.

If you have pygame it is easier and more portable to do something
like::

    import pygame.joystick
    from pygame.event import event_name

    pygame.init()
    pygame.joystick.init()

    js = pygame.joystick.Joystick(0)
    js.init()

    while True:
        for event in pygame.event.get():
            if event.axis == 0:
                print(event)


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
import struct
import select

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
        while True:
            yield read_event(device)

def panic(port):
    """
    Send "All Notes Off" and "Reset All Controllers" on
    all channels.
    """
    for channel in range(16):
        for control in [121, 123]:
            message = mido.Message('control_change',
                                   channel=channel,
                                   control=control, value=0)
            print(message)
            port.send(message)

class Monophonic(object):
    # Todo: this assumes everything is on channel 0!

    def __init__(self, output, channel=0):
        self.output = output
        self.notes = set()
        self.current_note = None
        self.channel = channel

    def send(self, message):
        if message.type not in ['note_on', 'note_off'] or \
                message.channel != self.channel:
            self.output.send(message)
            return

        if message.type == 'note_on':
            self.notes.add(message.note)
        elif message.type == 'note_off':
            if message.note in self.notes:
                self.notes.remove(message.note)

        print(self.notes)

        try:
            note = min(self.notes)
        except ValueError:
            note = None

        if note == self.current_note:
            return  # Same note as before, no change.

        if self.current_note is not None:
            off = mido.Message('note_off',
                               note=self.current_note,
                               velocity=message.velocity)
            print(off)
            self.output.send(off)
            self.current_note = None

        if note is not None:
            on = mido.Message('note_on',
                              note=note,
                              velocity=message.velocity)
            print(on)
            self.output.send(on)
            self.current_note = note


def play_scale(dev, out):
    # out = Monophonic(out, channel=0)

    # Major scale.
    scale = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19]

    # program = 16  # Organ
    program = 74
    out.send(mido.Message('program_change', program=program))

    while True:
        event = read_event(dev)

        if event['init']:
            continue  # Skip init events.

        if event['type'] == 'button':
            # Convert to D-major scale starting at middle D.
            note = 62 + 12 + scale[event['number']]
            if event['value']:
                type_ = 'note_on'
            else:
                type_ = 'note_off'

            message = mido.Message(type_, note=note, velocity=64)
            out.send(message)

        # elif event['type'] == 'axis':
        #     if event['number'] == 0:
        #         pitch_scale = mido.messages.MAX_PITCHWHEEL
        #         pitch = int(event['normalized_value'] * pitch_scale)
        #         out.send(mido.Message('pitchwheel', pitch=pitch))

def play_drums(dev, out):
    # http://www.midi.org/techspecs/gm1sound.php
    note_mapping = {
        2: 35,  # Acoustic Bass Drum
        6: 38,  # Acoustic Snare
        1: 41,  # Low Floor Tom
        4: 47,  # Low Mid Tom
        3: 50,  # High Tom
        8: 51,  # Ride Cymbal

        5: 42,  # Closed Hi Hat
        7: 46,  # Open Hi Hat

        9: 52,  # Chinese Cymbal
        10: 55,  # Splash Cymbal
        }

    while True:
        event = read_event(dev)
        if event['init']:
            continue

        if event['type'] == 'button':
            print(event)

            button = event['number'] + 1  # Number buttons starting with 1.
            if button not in note_mapping:
                continue

            if event['value']:
                type_ = 'note_on'
            else:
                type_ = 'note_off'
            
            note = note_mapping[button]

            message = mido.Message(type_, channel=9, note=note, velocity=64)
            print(message)
            out.send(message)


if __name__ == '__main__':
    import sys
    import mido

    with open('/dev/input/js0') as dev:
        with mido.open_output('SD-20 Part A') as out:
            try:
                # play_drums(dev, out)
                play_scale(dev, out)
            finally:
                panic(out)
