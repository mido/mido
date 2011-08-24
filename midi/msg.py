# -*- coding: utf-8 -*-

"""
Implements the following MIDI messages:


  Channel messages

  80 note_off    chan note vel
  90 note_on     chan note vel
  a0 polytouch   chan note value
  b0 control     chan number value
  c0 program     chan program
  d0 aftertouch  chan value
  c0 pitchwheel  chan lsb msb


  System common messages

  f0 sysex          vendor data
  f2 songpos        lsb msb
  f3 song           song
  f6 tune_request
  f7 sysex_end


  System realtime messages

  f8 clock
  fa start
  fb continue        # This clashes with 
  fc stop
  fe active_sensing
  ff reset

"""

import sys
from .types import assert_time, assert_chan, assert_data, is_chanmsg


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


class system_common_msg(system_msg):
    """
    System common message (abstract base class)
    """
    pass


class system_realtime_msg(system_msg):
    """
    System realtime message (abstract base class)
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
        self.bytes = (self.opcode | self.chan, self.note, self.vel)
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
        return '%s(time=%s, chan=%s, note=%s, vel=%s)' % (self.type, self.time, self.chan, self.note, self.vel)


class note_off(note_msg):
    opcode = 0x80
    type = 'note_off'


class note_on(note_msg):
    opcode = 0x90
    type = 'note_on'


class aftertouch(channel_msg):
    opcode = 0x90
    type = 'aftertouch'

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
        self.bytes = (self.opcode | self.chan, self.note, self.value)
        self.bin = bytes(self.bytes)

    def copy(self, time=0, chan=0, note=0, value=0):
        return self.__class__(time=time, chan=chan, note=note, value=value)
    
    def __repr__(self):
        return '%s(time=%s, chan=%s, note=%s, value=%s)' % (self.type, self.time, self.chan, self.note, self.value)


class sysex(system_common_msg):
    
    type = 'sysex'
    opcode = 0xf0

    def __init__(self, time=0, vendor=0, data=()):

        assert_time(time)
        assert_data(vendor)
        for byte in data:
            assert_data(data)

        self.time = time
        self.vendor = vendor
        self.data = tuple(data)

        # Serialize
        self.bytes = (self.opcode, self.vendor) + self.data
        self.bin = bytes(self.bytes)

    def copy(self, time=0, vendor=0, data=()):
        return self.__class__(time=time, vendor=vendor, data=data)

    def __repr__(self):
        return '%s(time=%s, vendor=%s, data=%s)' % (self.type, self.time, self.vendor, self.data)
