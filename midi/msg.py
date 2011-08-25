# -*- coding: utf-8 -*-

"""
Implements the following MIDI messages:


  Channel messages

  80 note_off    chan    note vel
  90 note_on     chan    note vel
  a0 polytouch   chan    note value
  b0 control     chan    number value
  c0 program     chan    program
  d0 aftertouch  chan    value
  c0 pitchwheel  chan    lsb msb


  System common messages

  f0 sysex          vendor data
  f2 songpos        lsb msb
  f3 song           song
  f6 tune_request


  System realtime messages

  f8 clock
  fa start
  fb continue        # This clashes with 
  fc stop
  fe active_sensing
  ff reset

"""

import sys
from .asserts import assert_time, assert_chan, assert_data, is_chanmsg


# Todo: use abc? 
class midi_msg:
    """
    MIDI message (Abstract base class)
    """

    def __len__(self):
        """Returns number of bytes in the message"""
        return len(self.bytes)


class channel_msg(midi_msg):
    """
    Channel message (abstract base class)
    """
    pass


class system_msg(midi_msg):
    """
    System message (abstract base class)
    """
    pass


class note_msg(channel_msg):

    """
    Abstract base class for MIDI note messages.
    """

    def __init__(self, time=0, chan=0, note=0, vel=0):

        assert_time(time)
        assert_chan(chan)
        assert_data(note)
        assert_data(vel)

        self.time = time
        self.chan = chan
        self.note = note
        self.vel = vel

        # Serialize
        self.bytes = (self.opcode | chan, note, vel)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, chan=None, note=None, vel=None):

        if time is None:
            time = self.time
        if chan is None:
            chan = self.chan
        if note is None:
            note = self.note
        if vel is None:
            vel = self.vel

        return self.__class__(time=time, chan=chan, note=note, vel=vel)

    def __repr__(self):
        return '%s(time=%s, chan=%s, note=%s, vel=%s)' % (
            self.type, self.time, self.chan, self.note, self.vel)


class note_off(note_msg):

    opcode = 0x80
    type = 'note_off'


class note_on(note_msg):

    opcode = 0x90
    type = 'note_on'


class polytouch(channel_msg):

    opcode = 0xa0
    type = 'polytouch'

    def __init__(self, time=0, chan=0, note=0, value=0):
        
        assert_time(time)
        assert_chan(chan)
        assert_data(note)
        assert_data(value)

        self.time = time
        self.chan = chan
        self.note = note
        self.value = value

        # Serialize
        self.bytes = (self.opcode | chan, note, value)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, chan=None, note=None, value=None):

        if time is None:
            time = self.time
        if chan is None:
            chan = self.chan
        if note is None:
            note = self.note
        if value is None:
            value = self.value

        return self.__class__(time=time, chan=chan, note=note, value=value)
    
    def __repr__(self):
        return '%s(time=%s, chan=%s, note=%s, value=%s)' % (
            self.type, self.time, self.chan, self.note, self.value)


class control(channel_msg):
    """
    MIDI control change message
    """

    opcode = 0xb0
    type = 'aftertouch'

    def __init__(self, time=0, chan=0, number=0, value=0):
        
        assert_time(time)
        assert_chan(chan)
        assert_data(number)
        assert_data(value)

        self.time = time
        self.chan = chan
        self.number = number
        self.value = value

        # Serialize
        self.bytes = (self.opcode | chan, number, value)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, chan=None, number=None, value=None):

        if time is None:
            time = self.time
        if chan is None:
            chan = self.chan
        if note is None:
            note = self.note
        if value is None:
            value = self.value

        return self.__class__(time=time, chan=chan, number=number, value=value)
    
    def __repr__(self):
        return '%s(time=%s, chan=%s, number=%s, value=%s)' % (
            self.type, self.time, self.chan, self.number, self.value)


class program(channel_msg):
    """
    MIDI program change message
    """

    opcode = 0xc0
    type = 'program'

    def __init__(self, time=0, chan=0, program=0):
        
        assert_time(time)
        assert_chan(chan)
        assert_data(program)

        self.time = time
        self.chan = chan
        self.program = program

        # Serialize
        self.bytes = (self.opcode | chan, program)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, chan=None, program=None):

        if time is None:
            time = self.time
        if chan is None:
            chan = self.chan
        if program is None:
            program = self.program

        return self.__class__(time=time, chan=chan, program=program)
    
    def __repr__(self):
        return '%s(time=%s, chan=%s, program=%s)' % (
            self.type, self.time, self.chan, self.program)


class aftertouch(channel_msg):
    """
    MIDI aftertouch message
    """

    opcode = 0xd0
    type = 'aftertouch'

    def __init__(self, time=0, chan=0, value=0):
        
        assert_time(time)
        assert_chan(chan)
        assert_data(value)

        self.time = time
        self.chan = chan
        self.value = value

        # Serialize
        self.bytes = (self.opcode | chan, value)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, chan=None, value=None):

        if time is None:
            time = self.time
        if chan is None:
            chan = self.chan
        if value is None:
            value = self.value

        return self.__class__(time=time, chan=chan, value=value)
    
    def __repr__(self):
        return '%s(time=%s, chan=%s, value=%s)' % (
            self.type, self.time, self.chan, self.value)


class pitchwheel(channel_msg):
    """
    MIDI pitchwheel message
    """

    opcode = 0xe0
    type = 'pitchwheel'

    def __init__(self, time=0, chan=0, value=0):
        
        assert_time(time)
        assert_chan(chan)
        assert_data(value)

        self.time = time
        self.chan = chan
        self.value = value

        # Serialize
        self.bytes = (self.opcode | chan, value)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, chan=None, value=None):

        if time is None:
            time = self.time
        if chan is None:
            chan = self.chan
        if value is None:
            value = self.value

        return self.__class__(time=time, chan=chan, value=value)
    
    def __repr__(self):
        return '%s(time=%s, chan=%s, value=%s)' % (
            self.type, self.time, self.chan, self.value)


#########################################################
# System common messages
#

class system_common_msg(system_msg):
    """
    System common message (abstract base class)
    """
    pass

class sysex(system_common_msg):
    
    type = 'sysex'
    opcode = 0xf0

    def __init__(self, time=0, vendor=0, data=()):

        assert_time(time)
        assert_data(vendor)
        if not isinstance(data, tuple):
            raise ValueError('data argument to sysex must be a tuple')
        for byte in data:
            assert_data(byte)

        self.time = time
        self.vendor = vendor
        self.data = data

        # Serialize
        self.bytes = (self.opcode, vendor) + data
        self.bin = bytes(self.bytes)

    def copy(self, time=None, vendor=None, data=None):
        
        if time is None:
            time = self.time
        if vendor is None:
            vendor = self.vendor
        if data is None:
            data = self.data

        return self.__class__(time=time, vendor=vendor, data=data)

    def __repr__(self):
        return '%s(time=%s, vendor=%s, data=%s)' % (
            self.type, self.time, self.vendor, self.data)


class songpos(system_common_msg):
    
    type = 'songpos'
    opcode = 0xf2

    def __init__(self, time=0, lsb=0, msb=0):

        assert_time(time)
        assert_data(lsb)
        assert_data(msb)

        self.time = time
        self.lsb = lsb
        self.msb = msb

        # Serialize
        self.bytes = (self.opcode, lsb, msb)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, lsb=None, msb=None):

        if time is None:
            time = self.time
        if lsb is None:
            lsb = self.lsb
        if msb is None:
            msb = self.msb

        return self.__class__(time=time, lsb=lsb, msb=msb)

    def __repr__(self):
        return '%s(time=%s, lsb=%s, msb=%s)' % (
            self.type, self.time, self.lsb, self.msb)


class song_select(system_common_msg):
    
    type = 'song_select'
    opcode = 0xf3

    def __init__(self, time=0, song=0):

        assert_time(time)
        assert_data(song)

        self.time = time
        self.song = song

        # Serialize
        self.bytes = (self.opcode, song)
        self.bin = bytes(self.bytes)

    def copy(self, time=None, song=None):

        if time is None:
            time = self.time
        if song is None:
            song = self.song

        return self.__class__(time=0, song=0)

    def __repr__(self):
        return '%s(time=%s, song=%s)' % (
            self.type, self.time, self.song)


class tune_request(system_common_msg):
    
    type = 'tune_request'
    opcode = 0xf6

    def __init__(self, time=0, song=0):

        assert_time(time)

        self.time = time

        # Serialize
        self.bytes = (self.opcode, )
        self.bin = bytes(self.bytes)

    def copy(self, time=None):

        if time is None:
            time = self.time

        return self.__class__(time=0)

    def __repr__(self):
        return '%s(time=%s)' % (self.type, self.time)


############################################################################
# System realtime messages
#

class system_realtime_msg(system_msg):
    """
    System realtime message (abstract base class)
    """

    def __init__(self, time=0, song=0):

        assert_time(time)

        self.time = time

        # Serialize
        self.bytes = (self.opcode, )
        self.bin = bytes(self.bytes)

    def copy(self, time=None):

        if time is None:
            time = self.time

        return self.__class__(time=0)

    def __repr__(self):
        return '%s(time=%s)' % (self.type, self.time)


class clock(system_realtime_msg):

    opcode = 0xf8
    type = 'clock'


class start(system_realtime_msg):

    opcode = 0xfa
    type = 'start'


class continue_(system_realtime_msg):

    opcode = 0xfb
    type = 'continue'


class stop(system_realtime_msg):

    opcode = 0xfc
    type = 'stop'


class active_sensing(system_realtime_msg):

    opcode = 0xfe
    type = 'active_sensing'


class reset(system_realtime_msg):

    opcode = 0xff
    type = 'reset'
