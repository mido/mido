"""
Virtual port
"""

from __future__ import absolute_import
from ..ports import BaseInput, BaseOutput
import ctypes
from ctypes import *

MAX_MSG_SIZE = 1024

vm = ctypes.CDLL("c:/windows/system32/teVirtualMIDI.dll")

PARSE_RX = (1)
PARSE_TX = (2)
INSTANTIATE_RX = (4)
INSTANTIATE_TX = (8)
INSTANTIATE_BOTH = (12)

get_version = vm.virtualMIDIGetVersion
get_version.restype=c_wchar_p
get_version.argtypes = [POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)]

create_port_ex2 = vm.virtualMIDICreatePortEx2
create_port_ex2.restype = c_void_p
create_port_ex2.argtypes = [c_wchar_p, c_void_p, POINTER(c_long), c_long, c_long]

close_port = vm.virtualMIDIClosePort
close_port.restype = c_void_p
close_port.argtypes = [c_void_p]

get_data = vm.virtualMIDIGetData
get_data.restype = c_bool
get_data.argtypes = [c_void_p, c_char_p, POINTER(c_int)]

send_data = vm.virtualMIDISendData
send_data.restype = c_bool
send_data.argtypes = [c_void_p, c_char_p, c_int]

class PortCommon(object):
    """
    Mixin with common things for input and output ports.
    """
    def _open(self, **kwargs):
        if not kwargs.get('virtual'):
            raise ValueError('physical ports are not supported by the teVirtualMidi backend')
        elif kwargs.get('callback'):
            raise ValueError('callbacks are not supported by the teVirtualMidi backend')


        if self.name is None:
            self.name = "Virtual Port"

        print("Opening port "+self.name)    
        
        flags = 0
        if self.is_input:
            flags += PARSE_RX + INSTANTIATE_RX
        if self.is_output:
            flags += PARSE_TX + INSTANTIATE_TX

        self._port = create_port_ex2(self.name, None, None, MAX_MSG_SIZE, flags)

        if not self._port:
            raise IOError("Could not open port: "+str(ctypes.WinError()))

        self._buffer = create_string_buffer(MAX_MSG_SIZE)

        self._device_type = "teVirtualMidi"

    def _close(self):
        close_port(self._port)


class Input(PortCommon, BaseInput):
    """
    Input port
    """
    _locking = False
    def _receive(self, block=True):
        if not block:
            raise IOError("Non-blocking virtual port read unimplemented")

        size = c_int(MAX_MSG_SIZE)
        result = get_data(self._port, self._buffer, byref(size))
        if not result:
            raise IOError("Buffer %d not large enough to hold message of size %d" % (MAX_MSG_SIZE, size.value))

        self._parser.feed(self._buffer.raw[0:size.value])


class Output(PortCommon, BaseOutput):
    """
    output port
    """
    _locking = False
    def _send(self, message):
        data = bytes(message.bytes())
        result = send_data(self._port, data, len(data))
        if not result:
            raise IOError("Error sending message: "+str(ctypes.WinError()))

class IOPort(Input, Output):
    def __init__(self, name='', **kwargs):
        """Create an IO port.

        name is the port name, as returned by ioport_names().
        """
        Input.__init__(self, name, **kwargs)
        Output.__init__(self, name, **kwargs)
