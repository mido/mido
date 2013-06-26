"""
Input and Output ports for PortMidi.

Module Content:

    Input(name=None)
        receive()     return a message, or block until there is one.
        poll()        return how many messages are pending
        close()       close the port

    Output(name=None)
        send(msg)     send a message
        close()       close the port

    get_input_names()   return a list of input names
    get_output_names()  return a list of output names
"""

from __future__ import print_function
import time

from .parser import Parser
from . import portmidi_wrapper as pm

_initialized = False


def _check_error(return_value):
    """Raise IOError if return_value < 0.

    The exception will be raised with the error message from PortMidi.
    """
    if return_value < 0:
        raise IOError(pm.lib.Pm_GetErrorText(return_value))


def _print_event(event):
    """Print a PortMidi event. (For debugging.)"""

    value = event.message & 0xffffffff
    message_bytes = []
    for _ in range(4):
        byte = value & 0xff
        message_bytes.append(byte)
        value >>= 8
    print(' '.join('{:02x}'.format(b) for b in message_bytes))


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

        # Todo: This screws up __del__() for ports,
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
        _initialized


def _get_device(device_id):
    """Return a PortMidi device based on ID.

    The return value is a PmDeviceInfo struct.

    Raises IOError if the device is not found.
    """
    info_pointer = pm.lib.Pm_GetDeviceInfo(device_id)
    if not info_pointer:
        raise IOError('PortMidi device with id={} not found'.format(device_id))

    return info_pointer.contents


def _get_devices():
    for device_id in range(pm.lib.Pm_CountDevices()):
        yield _get_device(device_id)

#
# Public functions and classes
#

def get_input_names():
    """Return a list of all input port names.

    These can be passed to Input().
    """
    names = [device.name for device in _get_devices() if device.is_input]
    return list(sorted(names))


def get_output_names():
    """Return a list of all input port names.

    These can be passed to Output().
    """
    names = [device.name for device in _get_devices() if device.is_output]
    return list(sorted(names))


class Port(object):
    """
    Abstract base class for PortMidi Input and Output ports.
    """

    def __init__(self, name=None):
        self.name = name
        self.closed = True
        self._stream = pm.PortMidiStreamPtr()

        _initialize()

        this_is_input = (self.__class__ == Input)

        if self.name is None:
            if this_is_input:
                device_id = pm.lib.Pm_GetDefaultInputDeviceID()
            else:
                device_id = pm.lib.Pm_GetDefaultOutputDeviceID()

            if device_id < 0:
                raise IOError('no default port found')

            self.name = _get_device(device_id).name
        else:
            #
            # Look for the device by name and type (input / output)
            #
            for device_id, device in enumerate(_get_devices()):
                if device.name != self.name:
                    continue
                
                # Check if device is correct type
                if this_is_input:
                    if device.is_output:
                        continue
                else:
                    if device.is_input:
                        continue

                if device.opened:
                    fmt = 'port already opened: {!r}'
                    raise IOError(fmt.format(self.name))

                # Nothing went wrong! We found a match!
                break
            else:
                # No match found.
                fmt = 'unknown port: {!r}'
                raise IOError(fmt.format(self.name))

        if this_is_input:
            _check_error(pm.lib.Pm_OpenInput(
                    pm.byref(self._stream),
                    device_id,  # inputDevice
                    pm.null,    # inputDriverInfo
                    1000,       # bufferSize
                    pm.NullTimeProcPtr,   # time_proc
                    pm.null))    # time_info
        else:
            _check_error(pm.lib.Pm_OpenOutput(
                    pm.byref(self._stream),
                    device_id,  # outputDevice
                    pm.null,    # outputDriverInfo
                    0,          # bufferSize (ignored when latency=0?)
                    pm.NullTimeProcPtr,  # default to internal clock
                    pm.null,    # time_info
                    0))         # latency

        self.closed = False

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

    def __del__(self):
        self.close()

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}({!r})'.format(class_name, self.name)


class Input(Port):
    """
    PortMidi Input port
    """

    def __init__(self, name=None):
        """Create an input port.

        The argument is the port name, as returned by
        get_input_names(). If name is not passed, the default input is
        used instead.
        """
        Port.__init__(self, name)
        self._parser = Parser()

    def poll(self):
        """Return how many messages are ready to be received.

        This can be used for non-blocking receive(), for example:

             while port.poll():
                 message = port.receive()
        """
        if self.closed:
            return

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

            # The bytes of the message are stored like this:
            #    0x00201090 -> (0x90, 0x10, 0x10)
            # (Todo: not sure if this is correct.)
            packed_message = event.message & 0xffffffff

            for i in range(4):
                byte = packed_message & 0xff
                self._parser.feed_byte(byte)
                packed_message >>= 8

        # Todo: the parser needs another method.
        return len(self._parser._parsed_messages)

    def receive(self):
        """Return the next message.

        This will block until a message arrives. For non-blocking
        behavior, you can use poll() to see how many messages can
        safely be received without blocking:

            while port.poll():
                message = port.receive()

        NOTE: Blocking is currently implemented with polling and
        time.sleep(). This is inefficient, but the proper way doesn't
        work yet, so it's better than nothing.
        """

        # If there is a message pending, return it right away.
        message = self._parser.get_message()
        if message:
            return message

        # Wait for a message to arrive.
        while 1:
            time.sleep(0.001)
            if self.poll():
                # poll() has read at least one
                # message from the device.
                # Return the first message.
                return self._parser.get_message()

    # It is unclear how  __iter__() should behave.
    # Like this?
    #
    #     for i in range(port.poll()):
    #         yield port.receive()
    #
    # Or like this?
    #
    #     while 1
    #         while port.poll():
    #             yield port.receive()


class Output(Port):
    """
    PortMidi output port
    """

    def send(self, message):
        """Send a message."""
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
