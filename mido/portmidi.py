"""
PortMidi I/O.
"""

from __future__ import print_function
import time

from .parser import Parser
from . import portmidi_wrapper as pm

debug = False

def dbg(*args):
    """
    Print a debugging message.
    """
    if debug:
        print('DBG:', *args)

_initialized = False

def _initialize():
    """
    Initialize PortMidi. If PortMidi is already initialized,
    it will do nothing.
    """

    global _initialized

    dbg('initialize()')

    if _initialized:
        dbg('  (already initialized)')
    else:        
        pm.lib.Pm_Initialize()        

        _initialized = True
        # Todo: This screws up __del__() for ports
        # atexit.register(_terminate)

def _terminate():
    """
    Terminate PortMidi. This will be called by an atexit() handler.
    If you call it after it has already terminated, it will do nothing.
    """

    global _initialized

    dbg('terminate()')
    if _initialized:
        pm.lib.Pm_Terminate()
        _initialized = False
    else:
        dbg('  (already terminated)')


def _get_device(devid):
    """
    Return a device based on ID. Raises IOError
    if the device is not found.
    """
    info_ptr = pm.lib.Pm_GetDeviceInfo(devid)
    if not info_ptr:
        raise IOError('PortMIDI device with id={} not found'.format(devid))

    return info_ptr.contents

def _get_devices():
    """
    Return all PortMidi devices as a dictionary with
    device ID as key.
    """

    _initialize()

    devices = {}

    for devid in range(pm.lib.Pm_CountDevices()):
        devices[devid] = _get_device(devid)

    return devices

def get_input_names():
    """
    Return a list of all input port names.
    These can be passed to Input().
    """

    names = [dev.name for dev in
             _get_devices().values() if dev.input]
    return list(sorted(names))

def get_output_names():
    """
    Return a list of all input port names.
    These can be passed to Output().
    """

    names = [dev.name for dev in
             _get_devices().values() if dev.output]
    return list(sorted(names))

def _check_err(err):
    """
    Raise IOError if err < 0.
    """
    if err < 0:
        raise IOError(pm.lib.Pm_GetErrorText(err))

def _print_event(event):
    """
    Print a PortMIDI event. (For debugging.)
    """

    value = event.message & 0xffffffff
    dbg_bytes = []
    for _ in range(4):
        byte = value & 0xff
        dbg_bytes.append(byte)
        value >>= 8
    print(' '.join('{:02x}'.format(b) for b in dbg_bytes))

class Port(object):
    """
    Abstract base class for Input and Output ports
    """

    def __init__(self, name=None):
        self.name = name
        self.closed = True
        self.stream = None

    def close(self):
        """
        Close the port. If the port is already closed, nothing will
        happen.
        """

        dbg('closing port')

        if not self.closed:
            # Todo: Abort is not implemented for ALSA, so we get a warning here.
            # But is this really needed?
            # err = pm.lib.Pm_Abort(self.stream)
            # _check_err(err)
            
            err = pm.lib.Pm_Close(self.stream)
            _check_err(err)

            self.closed = True

    def __del__(self):
        self.close()

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}({!r})'.format(class_name, self.name)

class Input(Port):
    """
    PortMidi Input
    """

    def __init__(self, name=None):
        """
        Create an input port.

        The argument 'name' is the name of the device to use. If not passed,
        the default device is used instead (which may not exists on all systems).
        """
        
        Port.__init__(self, name)

        _initialize()

        self._parser = Parser()

        if self.name is None:
            devid = pm.lib.Pm_GetDefaultInputDeviceID()
            if devid < 0:
                raise IOError('No default input found')
            self.name = _get_device(devid).name
        else:
            for devid, dev in _get_devices().items():
                if dev.name == self.name and dev.input:
                    if dev.opened:
                        fmt = 'Input already opened: {!r}'
                        raise IOError(fmt.format(self.name))
                    else:
                        break
            else:
                raise IOError('unknown input: {!r}'.format(self.name))

        self.stream = pm.PortMidiStreamPtr()
        
        dbg('opening input')

        err = pm.lib.Pm_OpenInput(pm.byref(self.stream),
                                  devid,    # inputDevice
                                  pm.null,  # inputDriverInfo
                                  1000,     # bufferSize
                                  pm.NullTimeProcPtr,   # time_proc
                                  pm.null,  # time_info
                                  )
        _check_err(err)

        self.closed = False

    def poll(self):
        """
        Read and parse whatever events have arrived since the last time we were called.
        
        Returns the number of messages ready to be received.
        """

        if self.closed:
            return

        # I get hanging notes if MAX_EVENTS > 1, so I'll have to resort
        # to calling Pm_Read() in a loop until there are no more pending events.

        max_events = 1
        # Todo: this should be allocated once
        BufferType = pm.PmEvent * max_events
        buf = BufferType()

        while pm.lib.Pm_Poll(self.stream):

            num_events = pm.lib.Pm_Read(self.stream, buf, 1)
            _check_err(num_events)

            #
            # Read the event
            #

            event = buf[0]

            #if debug:
            #    _print_event(event)

            # The bytes are stored in the lower 16 bit of the message,
            # starting with LSB and ending with MSB, for example:
            #    0x007f4090 
            # is a note_on message. The code below pops each byte from the
            # right and puts them into the parser. The stray data byte 0x00
            # will be ignored by the parser, so we can safely put all 4 bytes
            # in no matter how short the message is.
            value = event.message & 0xffffffff

            for i in range(4):
                byte = value & 0xff
                self._parser.put_byte(byte)
                value >>= 8

        # Todo: the parser needs another method
        return len(self._parser.messages)

    def recv(self):
        """
        Return the next pending message. Blocks until a message
        is available.

        Use .poll() to see how many messages you can safely read
        without blocking.
        
        NOTE: Blocking is currently implemented with polling and
        time.sleep(). This is inefficient, but the proper way doesn't
        work yet, so it's better than nothing.
        """

        # If there is a message pending, return it right away
        msg = self._parser.get_msg()
        if msg:
            return msg

        # Wait for a message to arrive
        while 1:
            time.sleep(0.001)
            if self.poll():
                return self._parser.get_msg()

    #
    # There is not __iter__() yet.
    # 
    # It is unclear how  __iter__() should
    # behave. Should __iter__() iterate through
    # all messages that will arrive on the port?
    # That is:
    #
    #     for i in range(port.poll()):
    #         yield port.recv()
    #
    # or:
    #
    #     while 1
    #         while port.poll():
    #             yield port.recv()
    #

class Output(Port):
    """
    PortMidi Output
    """
    def __init__(self, name=None):
        """
        Create an output port.

        The argument 'name' is the name of the device to use. If not passed,
        the default device is used instead (which may not exists on all systems).
        """

        Port.__init__(self, name)

        if self.name is None:
            devid = pm.lib.Pm_GetDefaultOutputDeviceID()
            if devid < 0:
                raise IOError('no default output found')
            self.name = _get_device(devid).name
        else:
            # Find devid from name
            for devid, dev in _get_devices().items():
                if dev.name == self.name and dev.output:
                    if dev.opened:
                        fmt = 'output already in use: {!r}'
                        raise IOError(fmt.format(dev.name))
                    else:
                        break
            else:
                raise IOError('unknown output {!r}'.format(self.name))

        self.stream = pm.PortMidiStreamPtr()
        
        err = pm.lib.Pm_OpenOutput(
            pm.byref(self.stream),
            devid,    # outputDevice
            pm.null,  # outputDriverInfo
            0,        # bufferSize (ignored when latency=0?)
            pm.NullTimeProcPtr,  # default to internal clock
            pm.null,  # time_info
            0)        # latency
        _check_err(err)

        self.closed = False

    def send(self, msg):
        """
        Send a message on the output port
        """

        if self.closed:
            raise ValueError('send() called on closed port')

        if msg.type == 'sysex':
            chars = pm.c_char_p(bytes(msg.bin()))
            err = pm.lib.Pm_WriteSysEx(self.stream, 0, chars)
            _check_err(err)
        else:
            value = 0
            for byte in reversed(msg.bin()):
                value <<= 8
                value |= byte

            timestamp = 0  # Ignored when latency=0

            err = pm.lib.Pm_WriteShort(self.stream, timestamp, value)
            _check_err(err)
