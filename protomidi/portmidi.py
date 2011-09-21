"""
Wrapper for PortAudio

The API still needs a lot of work. I want to get rid of get_defoutput() and count_devices()
and replace them with something else.

http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py
http://portmedia.sourceforge.net/portmidi/doxygen/portmidi_8h-source.html

Todo:

  - clean up API
"""

from __future__ import print_function
import sys
from contextlib import contextmanager
from collections import OrderedDict
import atexit
# import midi

from .serializer import serialize
from .parser import Parser

from . import portmidi_init as pm

debug = False

def dbg(*args):
    if debug:
        print('DBG:', *args)

def get_definput():
    return pm.lib.Pm_GetDefaultInputDeviceID()

def get_defoutput():
    return pm.lib.Pm_GetDefaultOutputDeviceID()

def count_devices():
    return pm.lib.Pm_CountDevices()

def get_devinfo():
    devices = []

    for id in range(count_devices()):
        info_ptr = pm.lib.Pm_GetDeviceInfo(id)
        if info_ptr:
            devinfo = info_ptr.contents

            dev = dict(
                id=id,
                name=devinfo.name,
                interf=devinfo.interf,
                input=devinfo.input,
                output=devinfo.output,
                opened=devinfo.opened,
                )
            devices.append(dev)

    return devices

class Error(Exception):
    pass

def _check_err(err):
    # Todo: err?
    if err < 0:
        raise Error(pm.lib.Pm_GetErrorText(err))

initialized = False

def initialize():
    global initialized

    dbg('initialize()')

    if initialized:
        dbg('(already initialized)')
        pass
    else:        
        pm.lib.Pm_Initialize()        

        dbg('starting timer')
        # Start timer
        pm.lib.Pt_Start(1, pm.NullTimeProcPtr, pm.null)
        initialized = True
        dbg('atexit.register()')
        atexit.register(terminate)
        dbg('initialized')

def terminate():
    global initialized

    dbg('terminate()')
    if initialized:
        pm.lib.Pm_Terminate()
        initialized = False
    else:
        dbg('(already terminated)')


class Port:
    pass

class Input(Port):
    """
    PortMidi Input
    """

    def __init__(self,
                 dev=None,
                 latency=0,
                 channel_mask=None,
                 filters=None):
        """
        Create an input port. If 'dev' is not passed, the default
        device is used. 'dev' is an integer >= 0.
        """
        # Todo: add channel_mask, filters etc. to docstring

        initialize()

        if dev == None:
            dev = get_definput()
            if dev < 0:
                raise Error('No default input found')
        self.dev = dev
        self.stream = pm.PortMidiStreamPtr()
        
        time_proc = pm.PmTimeProcPtr(pm.lib.Pt_Time())

        dbg('opening input')
        err = pm.lib.Pm_OpenInput(pm.byref(self.stream),
                               self.dev, pm.null, 100,
                               time_proc, pm.null)
        _check_err(err)

        if channel_mask != None:
            self.set_channel_mask(channel_mask)

        if filters != None:
            self.set_filter(filters)

    def __dealloc__(self):
        err = pm.lib.Pm_Abort(self.stream)
        _check_err(err)
        err = pm.lib.Pm_Close(self.stream)
        _check_err(err)

    def set_filter(self, filters):
        """
        """
        # Todo: write docstring
        # Todo: do this? set_filter(['active', 'sysex'])

        buffer = pm.PmEvent()
        err = pm.lib.Pm_SetFilter(self.stream, filters)
        _check_err(err)

        while pm.lib.Pm_Poll(self.stream) != 0:
            err = pm.lib.Pm_Read(self.stream, buffer, 1)
            _check_err(err)

    def set_channel_mask(self, mask):
        """
        16-bit bitfield.
        """
        # Todo: improve docstring

        err = pm.lib.Pm_SetChannelMask(self.stream, mask)
        _check_err(err)

    def poll(self):
        """
        Returns True if there are one or more pending messages to
        read.
        """
        ret = pm.lib.Pm_Poll(self.stream)
        _check_err(ret)
        return ret

    def recv(self):
        """
        Return the next pending message, or None if there are no messages.
        """

        BufferType = pm.PmEvent * 1
        buffer = BufferType()

        # Third argument is length (number of messages)
        num_events = pm.lib.Pm_Read(self.stream, buffer, 1)
        _check_err(num_events)

        # event.message is an integer, where the lowest bytes are the MIDI
        # message.
        
        if num_events == 1:
            event = buffer[0]

            # Todo: What happens to sysex messages?

            value = event.message
            # Todo: keep the parser around, so we don't have to
            # allocate it every time.
            p = Parser()

            while value:
                # Pop the lowest byte
                byte = value & 0xff
                value = value >> 8
                
                # 
                if p.feed(chr(byte)):  # Todo: wrong type?
                    # Todo: This looks weird. The parser should perhaps
                    # have a fetchone() or similar after all.
                    for msg in p:
                        return msg

        # Todo: what should happen here?

    def __iter__(self):
        """
        Iterate through pending messages.
        """
        while 1:
            msg = self.recv()
            if msg:
                yield msg
            else:
                break

class Output(Port):
    """
    PortMidi Output
    """
    def __init__(self, dev=None, latency=1):
        initialize()
        
        if dev == None:
            dev = get_defoutput()
            if dev < 0:
                raise Error('No default output found')
        self.dev = dev

        self.stream = pm.PortMidiStreamPtr()
        
        if latency > 0:
            time_proc = pm.PmTimeProcPtr(pm.lib.Pt_Time())
        else:
            # Todo: This doesn't work. NullTimeProcPtr() requires
            # one argument.
            time_proc = pm.NullTimeProcPtr(pm.lib.Pt_Time())

        err = pm.lib.Pm_OpenOutput(pm.byref(self.stream),
                                self.dev, pm.null, 0,
                                time_proc, pm.null, latency)
        _check_err(err)

    def __dealloc__(self):
        if 0:
            err = pm.lib.Pm_Abort(self.dev)
            _check_err(err)
            
            err = pm.lib.Pm_Close(self.dev)
            _check_err(err)

    def send(self, msg):
        """Send a message on the output port"""

        bytes = [b for b in serialize(msg)]
        bytes += [0, 0, 0, 0]  # Padding

        event = pm.PmEvent()
        event.timestamp = pm.lib.Pt_Time()
        event.message = (bytes[2] << 16) | (bytes[1] << 8) | (bytes[0])

        err = pm.lib.Pm_Write(self.stream, event, 1)
        _check_err(err)

#
# Message filters for Input
#
# Todo: The names here should correspond with those in MIDI messages names (msg.py)
#
FILT_ACTIVE = (1 << 0x0E)  # filter active sensing messages (0xFE)
FILT_SYSEX  = (1 << 0x00)  # filter system exclusive messages (0xF0)
FILT_CLOCK  = (1 << 0x08)  # filter MIDI clock message (0xF8)
FILT_PLAY   = ((1 << 0x0A) | (1 << 0x0C) | (1 << 0x0B))  # filter play messages (start 0xFA, stop 0xFC, continue 0xFB) 
FILT_TICK   = (1 << 0x09)  # filter tick messages (0xF9) 
FILT_FD     = (1 << 0x0D)  # ilter undefined FD messages
FILT_UNDEFINED = FILT_FD  # filter undefined real-time messages 
FILT_RESET  = (1 << 0x0F)  # filter reset messages (0xFF) 

FILT_REALTIME = (FILT_ACTIVE | FILT_SYSEX | FILT_CLOCK | FILT_PLAY | FILT_UNDEFINED | FILT_RESET | FILT_TICK)  #filter all real-time messages 

FILT_NOTE   = ((1 << 0x19) | (1 << 0x18))  # filter note-on and note-off (0x90-0x9F and 0x80-0x8F

FILT_CHANNEL_AFTERTOUCH = (1 << 0x1D)  # filter channel aftertouch (most midi controllers use this) (0xD0-0xDF)
FILT_POLY_AFTERTOUCH = (1 << 0x1A)  # per-note aftertouch (0xA0-0xAF) 
FILT_AFTERTOUCH = (FILT_CHANNEL_AFTERTOUCH | FILT_POLY_AFTERTOUCH)  # filter both channel and poly aftertouch 

FILT_PROGRAM = (1 << 0x1C)  # Program changes (0xC0-0xCF)
FILT_CONTROL = (1 << 0x1B)  # Control Changes (CC's) (0xB0-0xBF)
FILT_PITCHBEND = (1 << 0x1E)  # Pitch Bender (0xE0-0xEF) 

FILT_MTC = (1 << 0x01)  # MIDI Time Code (0xF1)
FILT_SONG_POSITION = (1 << 0x02)  # Song Position (0xF2)
FILT_SONG_SELECT = (1 << 0x03)  # Song Select (0xF3). 
FILT_TUNE = (1 << 0x06)  # Tuning request (0xF6) 
FILT_SYSTEMCOMMON = (FILT_MTC | FILT_SONG_POSITION | FILT_SONG_SELECT | FILT_TUNE)  # All System Common messages (mtc, song position, song select, tune request). 
