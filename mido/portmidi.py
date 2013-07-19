"""
Input and Output ports for PortMidi.

There is no need to use this module directly. All you need is
available in the toplevel module.

PortMidi documentation:
http://portmedia.sourceforge.net/portmidi/doxygen/
"""
import time

from .parser import Parser
from .messages import Message
from .ports import BaseInput, BaseOutput, IOPort

class PortMidiInitializer:
    """
    This class is responsible for loading PortMidi on demand. It
    camouflages in the global name space as a module, and forwards all
    attribute access to the real module.

    For testing, this mock module can be replaced with another mock
    module.
    """
    def __init__(self):
        self.pm = None

    def __getattr__(self, attr):
        # print('initializer was asked for', attr)
        if self.pm is None:
            # print('Initializing PortMidi...')
            from . import portmidi_init as pm
            self.pm = pm
            self.pm.lib.Pm_Initialize()

        return getattr(self.pm, attr)

    def __del__(self):
        if self.pm is not None:
            # print('Terminating PortMidi...')
            self.pm.lib.Pm_Terminate()
            self.pm = None

pm = PortMidiInitializer()

def _check_error(return_value):
    """Raise IOError if return_value < 0.

    The exception will be raised with the error message from PortMidi.
    """
    if return_value < 0:
        raise IOError(pm.lib.Pm_GetErrorText(return_value))


class DeviceInfo(object):
    """
    Info about a PortMidi device.

        device_id   an integer
        interface   interface name (for example 'ALSA')
        name        device name (the same as port name)
        is_input    boolean, True if this is an input device
        is_output   boolean, True if this is an output device
    """

    def __init__(self, device_id):
        """Create a new DeviceInfo object."""
        info_pointer = pm.lib.Pm_GetDeviceInfo(device_id)
        if not info_pointer:
            raise IOError('PortMidi device with id={} not found'.format(
                          device_id))
        info = info_pointer.contents
        
        self.device_id = device_id
        self.interface = info.interface.decode('utf-8')
        self.name = info.name.decode('utf-8')
        self.is_input = info.is_input
        self.is_output = info.is_output
        self.opened = bool(info.opened)
 
    def __repr__(self):
        if self.opened:
            state = 'open'
        else:
            state = 'closed'

        if self.is_input:
            device_type = 'input'
        else:
            device_type = 'output'

        return "<{state} {device_type} device '{self.name}'" \
            " '{self.interface}'>" \
            "".format(**locals())


def get_devices():
    """Return a list of DeviceInfo objects, one for each PortMidi device."""
    devices = []
    for device_id in range(pm.lib.Pm_CountDevices()):
        devices.append(DeviceInfo(device_id))

    return devices


def get_input_names():
    """Return a sorted list of all input port names.

    These names can be passed to Input().
    """
    names = [device.name for device in get_devices() if device.is_input]
    return list(sorted(names))


def get_output_names():
    """Return a sorted list of all input port names.

    These names can be passed to Output().
    """
    names = [device.name for device in get_devices() if device.is_output]
    return list(sorted(names))


def get_ioport_names():
    """Return the names of all ports that allow input and output."""
    return sorted(set(get_input_names()) & set(get_output_names()))


def open_input(name=None):
    """Open an input port."""
    return Input(name)


def open_output(name=None):
    """Open an output port."""
    return Output(name)


def open_ioport(name=None):
    """Open a port for input and output."""
    return IOPort(Input(name), Output(name))


class PortCommon(object):
    """
    Mixin with common things for input and output ports.
    """
    def _open(self, **kwargs):
        self._stream = pm.PortMidiStreamPtr()
        self.device = None

        opening_input = (self.__class__ is Input)

        if self.name is None:
            self.device = self._get_default_device(opening_input)
            self.name = self.device.name
        else:
            self.device = self._get_named_device(self.name, opening_input)

        if self.device.opened:
            if opening_input:
                devtype = 'input'
            else:
                devtype = 'output'
            raise IOError('{} port {!r} is already open'.format(devtype,
                                                                self.name))
        
        # Make a shortcut, since this is so long
        device_id = self.device.device_id

        if opening_input:
            _check_error(pm.lib.Pm_OpenInput(
                         pm.byref(self._stream),
                         device_id,  # Input device
                         pm.null,    # Input driver info
                         1000,       # Buffer size
                         pm.NullTimeProcPtr,  # Time callback
                         pm.null))    # Time info
        else:
            _check_error(pm.lib.Pm_OpenOutput(
                         pm.byref(self._stream),
                         device_id,  # Output device
                         pm.null,    # Output diver info
                         0,          # Buffer size
                                     # (ignored when latency == 0?)
                         pm.NullTimeProcPtr,  # Default to internal clock
                         pm.null,    # Time info
                         0))         # Latency

    def _get_device_type(self):
        return self.device.interface

    def _get_default_device(self, get_input):
        if get_input:
            device_id = pm.lib.Pm_GetDefaultInputDeviceID()
        else:
            device_id = pm.lib.Pm_GetDefaultOutputDeviceID()

        if device_id < 0:
            raise IOError('no default port found')
        
        return DeviceInfo(device_id)

    def _get_named_device(self, name, get_input):
        # Look for the device by name and type (input / output)
        for device in get_devices():
            if device.name != name:
                continue

            # Skip if device is the wrong type
            if get_input:
                if device.is_output:
                    continue
            else:
                if device.is_input:
                    continue

            if device.opened:
                raise IOError('port already opened: {!r}'.format(name))

            return device
        else:
            raise IOError('unknown port: {!r}'.format(name))

    def _close(self):
        _check_error(pm.lib.Pm_Close(self._stream))
        self.device.opened = False

class Input(PortCommon, BaseInput):
    """
    PortMidi Input port
    """

    def _pending(self):
        # I get hanging notes if MAX_EVENTS > 1, so I'll have to
        # resort to calling Pm_Read() in a loop until there are no
        # more pending events.

        max_events = 1
        # Todo: this should be allocated once
        BufferType = pm.PmEvent * max_events
        read_buffer = BufferType()

        while pm.lib.Pm_Poll(self._stream):

            # Read one message. Should return 1.
            # If num_events < 0, an error occured.
            length = 1  # Buffer length
            num_events = pm.lib.Pm_Read(self._stream, read_buffer, length)
            _check_error(num_events)

            # Get the event
            event = read_buffer[0]
            # print('Received: {:x}'.format(event.message))

            # The bytes of the message are stored like this:
            #    0x00201090 -> (0x90, 0x10, 0x10)
            # (Todo: not sure if this is correct.)
            packed_message = event.message & 0xffffffff

            for i in range(4):
                byte = packed_message & 0xff
                self._parser.feed_byte(byte)
                packed_message >>= 8

        return self._parser.pending()


class Output(PortCommon, BaseOutput):
    """
    PortMidi output port
    """

    def _send(self, message):
        if message.type == 'sysex':
            # Sysex messages are written as a string.
            string = pm.c_char_p(bytes(message.bin()))
            timestamp = 0  # Ignored when latency = 0
            _check_error(pm.lib.Pm_WriteSysEx(self._stream, timestamp, string))
        else:
            # The bytes of a message as packed into a 32 bit integer.
            packed_message = 0
            for byte in reversed(message.bytes()):
                packed_message <<= 8
                packed_message |= byte

            timestamp = 0  # Ignored when latency = 0
            _check_error(pm.lib.Pm_WriteShort(self._stream,
                                              timestamp,
                                              packed_message))
