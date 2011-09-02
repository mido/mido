"""
Wrapper for PortAudio

The API still needs a lot of work. I want to get rid of get_defoutput() and count_devices()
and replace them with something else.

http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py
http://portmedia.sourceforge.net/portmidi/doxygen/portmidi_8h-source.html
"""

from __future__ import print_function
import sys
from contextlib import contextmanager
from collections import OrderedDict
# import midi

from .portmidi_init import *
from .serializer import serialize

debug = False

def dbg(*args):
    print('DBG:', *args)

def initialize():
    dbg('initialize()')

    lib.Pm_Initialize()

    # Start timer
    lib.Pt_Start(1, NullTimeProcPtr, null)

def terminate():
    dbg('terminate()')
    lib.Pm_Terminate()    


@contextmanager
def context():
    initialize()
    yield
    terminate()

def get_definput():
    return lib.Pm_GetDefaulInputDeviceID()

def get_defoutput():
    return lib.Pm_GetDefaultOutputDeviceID()

def count_devices():
    return lib.Pm_CountDevices()

def get_device_info(i):
    """
    GetDeviceInfo(<device number>): returns 5 parameters
    - underlying MIDI API
    - device name
    - TRUE iff input is available
    - TRUE iff output is available
    - TRUE iff device stream is already open
    """
    info_ptr = lib.Pm_GetDeviceInfo(i)
    if info_ptr:
        info = info_ptr.contents
        # return info.interf, info.name, info.input, info.output, info.opened
        return info
    else:
        return None

def get_devinfo_dicts():
    devices = []

    for i in range(count_devices()):
        devinfo = get_device_info(i)

        dev = dict(
            i=i,
            input=devinfo.input,
            interf=devinfo.interf,
            name=devinfo.name,
            opened=devinfo.opened,
            output=devinfo.output,
            structVersion=devinfo.structVersion,
            info=devinfo,
            )
        devices.append(dev)

    return devices

def _get_time(*args):
    # Pt_time() returns the current time in milliseconds,
    # so we ned to divide it a bit here to get seconds.
    return lib.Pt_Time()

def get_time(*args):
    """
    Returns the current value of the PortMidi timer in seconds.
    The timer is started when you initialize PortMidi.
    """

    # Pt_time() returns the current time in milliseconds,
    # so we ned to divide it a bit here to get seconds.
    return lib.Pt_Time() / 1000.0

def get_err():
    """Return error text"""

# Todo: what does this return?
def Channel(chan):
    return lib.Pm_Channel(chan-1)

class PortAudioError(Exception):
    pass

def _check_err(err):
    # Todo: err?
    if err < 0:
        raise Exception(lib.Pm_GetErrorText(err))

class Input:
    """
    PortMidi Input
    """

    def __init__(self, dev=None, latency=0):
        """
        Create an input port. If 'device' is not passed, the default
        device is used. Todo: What exactly is 'device'? An integer?
        """
        if device == None:
            device = get_definput()


    def set_filter(self, filters):
        """
        set_filter(['active', 'sysex'])
        """
        pass

    def set_channel_mask(self, mask):
        """
        16-bit bitfield.
        """
        pass

    def poll(self):
        """
        Returns True if there are one or more pending messages to
        read.
        """
        return False

    def read(self):
        """
        Return the next pending message, or None if there are no messages.
        """
        return None

    def __iter__(self):
        """
        Iterate through pending messages.
        """
        while 1:
            msg = self.read()
            if msg:
                yield msg
            else:
                return

class Output:
    """
    PortMidi Output
    """
    def __init__(self, dev=None, latency=1):
        if dev == None:
            dev = get_defoutput()
        self.dev = dev

        self.stream = PortMidiStreamPtr()
        
        if latency > 0:
            time_proc = PmTimeProcPtr(_get_time)
        else:
            # This doesn't work. NullTimeProcPtr() requires
            # one argument.
            time_proc = NullTimeProcPtr(_get_time)

        err = lib.Pm_OpenOutput(byref(self.stream),
                                self.dev, null, 0,
                                time_proc, null, latency)
        _check_err(err)

    def __dealloc__(self):
        err = lib.Pm_Abort(self.dev)
        _check_err(err)

        err = lib.Pm_Close(self.dev)
        _check_err(err)

    def _send(self, data):
        if len(data) > 1024: raise IndexError, 'maximum list length is 1024'

        BufferType = PmEvent * 1024
        buffer = BufferType()

        for i, message in enumerate(data):
            msg = message[0]

            if len(msg) > 4 or len(msg) < 1:
                raise IndexError, str(len(msg)) + ' arguments in event list'

            buffer[i].message = 0

            for j, data_part in enumerate(msg):
                buffer[i].message += ((data_part & 0xFF) << (8*j))

            buffer[i].timestamp = message[1]

        err = lib.Pm_Write(self.stream, buffer, len(data))

        check_err(err)

    def send(self, msg):
        """Send a message on the output port"""

        bytes = [b for b in serialize(msg)]
        bytes += [0, 0, 0, 0]  # Padding

        print(bytes)

        event = PmEvent()
        event.timestamp = _get_time()
        event.message = (bytes[2] << 16) | (bytes[1] << 8) | (bytes[0])

        err = lib.Pm_Write(self.stream, event, 1)
        _check_err(err)
