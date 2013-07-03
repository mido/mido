"""
Input and Output ports for PortMidi.

There is no need to use this module directly. All you need is
available in the toplevel module.
"""
import time

from .parser import Parser
from . import portmidi_init as pm

_initialized = False


def _check_error(return_value):
    """Raise IOError if return_value < 0.

    The exception will be raised with the error message from PortMidi.
    """
    if return_value < 0:
        raise IOError(pm.lib.Pm_GetErrorText(return_value))


def _initialize():
    """Initialize PortMidi.

    This is called by constructors and functions in this module as
    needed.

    If PortMidi is already initialized, it will do nothing.
    """
    global _initialized

    if _initialized:
        pm.lib.Pm_Initialize()

        _initialized = True

        # This screws up __del__() for ports,
        # so it's left out for now:
        # atexit.register(_terminate)


def _terminate():
    """Terminate PortMidi.

    Note: This function is never called.

    It was meant to be used as an atexit handler, but it ended up
    being called before the port object constructors, resulting in a
    PortMidi reporting "invalid stream ID", so it's just never called
    until a solution is found.
    """
    global _initialized

    if _initialized:
        pm.lib.Pm_Terminate()
        _initialized = False


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


def input_names():
    """Return a sorted list of all input port names.

    These names can be passed to Input().
    """
    names = [device.name for device in get_devices() if device.is_input]
    return list(sorted(names))


def output_names():
    """Return a sorted list of all input port names.

    These names can be passed to Output().
    """
    names = [device.name for device in get_devices() if device.is_output]
    return list(sorted(names))


class Port(object):
    """
    Abstract base class for PortMidi Input and Output ports.
    """

    def __init__(self, name=None):
        self.closed = True
        self._stream = pm.PortMidiStreamPtr()
        self.device = None

        _initialize()

        opening_input = (self.__class__ is Input)

        if name is None:
            self.device = self._get_default_device(opening_input)
        else:
            self.device = self._get_named_device(name, opening_input)
        self.name = self.device.name

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

        self.closed = False
        self.device.opened = True

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

    def close(self):
        """Close the port.

        If the port is already closed, nothing will happen.
        The port is automatically closed when the object goes
        out of scope or is garbage collected.
        """

        if not self.closed:
            # Todo: Abort is not implemented for ALSA,
            # so we get a warning here.
            # But is it really needed?
            # _check_error(pm.lib.Pm_Abort(self._stream))

            _check_error(pm.lib.Pm_Close(self._stream))

            self.closed = True
            self.device.opened = False

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False

    def __repr__(self):
        if self.closed:
            state = 'closed'
        else:
            state = 'open'

        if self.__class__ is Input:
            port_type = 'input'
        else:
            port_type = 'output'

        return "<{state} {port_type} port '{self.name}'" \
               " ({self.device.interface})>".format(**locals())


class Input(Port):
    """
    PortMidi Input port
    """

    def __init__(self, name=None):
        """Create an input port.

        name is the port name, as returned by input_names(). If
        name is not passed, the default input is used instead.
        """
        Port.__init__(self, name)
        self._parser = Parser()

    def pending(self):
        """Return how many messages are ready to be received.

        This can be used for non-blocking receive(), for example:

             for _ in range(port.pending()):
                 message = port.receive()

        Todo: return 0 or raise exception if the port is closed?
        """
        if self.closed:
            return self._parser.pending()

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

    def iter_pending(self):
        """Iterate through pending messages."""
        for _ in range(self.pending()):
            yield self.receive()

    def receive(self):
        """Return the next message.

        This will block until a message arrives. For non-blocking
        behavior, you can use pending() to see how many messages can
        safely be received without blocking:

            for _ in range(port.pending()):
                message = port.receive()

        NOTE: Blocking is currently implemented with polling and
        time.sleep(). This is inefficient, but the proper way doesn't
        work yet, so it's better than nothing.

        Todo: What should happen when the port is closed?
        - raise exception?
        - return pending messages until we run out, then
          raise exception?
        """

        # If there is a message pending, return it right away.
        message = self._parser.get_message()
        if message:
            return message

        if self.closed:
            raise ValueError('receive() called on closed port')

        # Wait for a message to arrive.
        while 1:
            time.sleep(0.001)
            if self.pending():
                # pending() has read at least one message from the
                # device. Return the first message.
                return self._parser.get_message()

    def __iter__(self):
        """Iterate through messages as they arrive on the port."""
        while 1:
            yield self.receive()


class Output(Port):
    """
    PortMidi output port
    """

    def __init__(self, name=None):
        """Create an output port
        
        name is the port name, as returned by output_names(). If
        name is not passed, the default output is used instead.
        """
        Port.__init__(self, name)

    def send(self, message):
        """Send a message."""
        print('****', message)

        if self.closed:
            raise ValueError('send() called on closed port')

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
