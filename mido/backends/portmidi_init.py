"""
Low-level wrapper for PortMidi library

Copied straight from Grant Yoshida's portmidizero, with slight
modifications.
"""
import sys
from ctypes import (CDLL, CFUNCTYPE, POINTER, Structure, c_char_p,
                    c_int, c_long, c_uint, c_void_p, cast,
                    create_string_buffer, byref)
import ctypes.util

dll_name = ''
if sys.platform == 'darwin':
    dll_name = ctypes.util.find_library('libportmidi.dylib')
elif sys.platform in ('win32', 'cygwin'):
    dll_name = 'portmidi.dll'
else:
    dll_name = 'libportmidi.so'

lib = CDLL(dll_name)

null = None
false = 0
true = 1

# portmidi.h

# From portmidi.h
PM_HOST_ERROR_MSG_LEN = 256


def get_host_error_message():
    """Return host error message."""
    buf = create_string_buffer(PM_HOST_ERROR_MSG_LEN)
    lib.Pm_GetHostErrorText(buf, PM_HOST_ERROR_MSG_LEN)
    return buf.raw.decode().rstrip('\0')


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
                ("interface", c_char_p),
                ("name", c_char_p),
                ("is_input", c_int),
                ("is_output", c_int),
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
