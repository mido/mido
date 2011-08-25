from __future__ import print_function
import sys
import array
from ctypes import *
from contextlib import contextmanager
# import midi

"""
Mock implementation of PortMidi wrapper. I will fill in the implementation later.

http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py
http://portmedia.sourceforge.net/portmidi/doxygen/portmidi_8h-source.html
"""

debug = False

def dbg(*args):
    print('DBG:', *args)

#
# Initialize library
#
# This part is copied straight from Grant Yoshida's
# portmidizero:
#
# http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py
#

from ctypes import *
import array
import sys

dll_name = ''
if sys.platform == 'darwin':
    dll_name = 'libportmidi.dylib'
elif sys.platform in ('win32', 'cygwin'):
    dll_name = 'portmidi.dll'
else:
    dll_name = 'libportmidi.so'

lib = CDLL(dll_name)

null = None
false = 0
true = 1

# portmidi.h

PmError = c_int
# PmError enum
pmNoError = 0
pmHostError = -10000
pmInvalidDeviceId = -9999
pmInsufficientMemory = -9989
pmBufferTooSmall = -9979
pmBufferOverflow = -9969
pmBadPtr = -9959
pmBadData = -9994
pmInternalError = -9993
pmBufferMaxSize = -9992

lib.Pm_Initialize.restype = PmError
lib.Pm_Terminate.restype = PmError

PmDeviceID = c_int

PortMidiStreamPtr = c_void_p
PmStreamPtr = PortMidiStreamPtr
PortMidiStreamPtrPtr = POINTER(PortMidiStreamPtr)

lib.Pm_HasHostError.restype = c_int
lib.Pm_HasHostError.argtypes = [PortMidiStreamPtr]

lib.Pm_GetErrorText.restype = c_char_p
lib.Pm_GetErrorText.argtypes = [PmError]

lib.Pm_GetHostErrorText.argtypes = [c_char_p, c_uint]

pmNoDevice = -1

class PmDeviceInfo(Structure):
    _fields_ = [("structVersion", c_int),
                ("interf", c_char_p),
                ("name", c_char_p),
                ("input", c_int),
                ("output", c_int),
                ("opened", c_int)]

PmDeviceInfoPtr = POINTER(PmDeviceInfo)

lib.Pm_CountDevices.restype = c_int
lib.Pm_GetDefaultOutputDeviceID.restype = PmDeviceID
lib.Pm_GetDefaultInputDeviceID.restype = PmDeviceID

PmTimestamp = c_long
PmTimeProcPtr = CFUNCTYPE(PmTimestamp, c_void_p)
NullTimeProcPtr = cast(null, PmTimeProcPtr)

# PmBefore is not defined

lib.Pm_GetDeviceInfo.argtypes = [PmDeviceID]
lib.Pm_GetDeviceInfo.restype = PmDeviceInfoPtr

lib.Pm_OpenInput.restype = PmError
lib.Pm_OpenInput.argtypes = [PortMidiStreamPtrPtr,
                             PmDeviceID,
                             c_void_p,
                             c_long,
                             PmTimeProcPtr,
                             c_void_p]

lib.Pm_OpenOutput.restype = PmError
lib.Pm_OpenOutput.argtypes = [PortMidiStreamPtrPtr,
                             PmDeviceID,
                             c_void_p,
                             c_long,
                             PmTimeProcPtr,
                             c_void_p,
                             c_long]

lib.Pm_SetFilter.restype = PmError
lib.Pm_SetFilter.argtypes = [PortMidiStreamPtr, c_long]

lib.Pm_SetChannelMask.restype = PmError
lib.Pm_SetChannelMask.argtypes = [PortMidiStreamPtr, c_int]

lib.Pm_Abort.restype = PmError
lib.Pm_Abort.argtypes = [PortMidiStreamPtr]

lib.Pm_Close.restype = PmError
lib.Pm_Close.argtypes = [PortMidiStreamPtr]

PmMessage = c_long

class PmEvent(Structure):
    _fields_ = [("message", PmMessage),
                ("timestamp", PmTimestamp)]

PmEventPtr = POINTER(PmEvent)

lib.Pm_Read.restype = PmError
lib.Pm_Read.argtypes = [PortMidiStreamPtr, PmEventPtr, c_long]

lib.Pm_Poll.restype = PmError
lib.Pm_Poll.argtypes = [PortMidiStreamPtr]

lib.Pm_Write.restype = PmError
lib.Pm_Write.argtypes = [PortMidiStreamPtr, PmEventPtr, c_long]

lib.Pm_WriteShort.restype = PmError
lib.Pm_WriteShort.argtypes = [PortMidiStreamPtr, PmTimestamp, c_long]

lib.Pm_WriteSysEx.restype = PmError
lib.Pm_WriteSysEx.argtypes = [PortMidiStreamPtr, PmTimestamp, c_char_p]

# porttime.h

# PtError enum
PtError = c_int
ptNoError = 0
ptHostError = -10000
ptAlreadyStarted = -9999
ptAlreadyStopped = -9998
ptInsufficientMemory = -9997

PtTimestamp = c_long
PtCallback = CFUNCTYPE(PmTimestamp, c_void_p)

lib.Pt_Start.restype = PtError
lib.Pt_Start.argtypes = [c_int, PtCallback, c_void_p]

lib.Pt_Stop.restype = PtError
lib.Pt_Started.restype = c_int
lib.Pt_Time.restype = PtTimestamp


########################################################################3
# API starts here
#

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

def get_time():
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
            time_proc = PmTimeProcPtr(get_time)
        else:
            # This doesn't work. NullTimeProcPtr() requires
            # one argument.
            time_proc = NullTimeProcPtr()

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
