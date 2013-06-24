"""
PortMidi I/O.

Since this is written specifically for ProtoMIDI, we don't use:

  - timers
  - latency
  - filters
  - channel masks

It is better to implement these generally further up.

http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py
http://portmedia.sourceforge.net/portmidi/doxygen/main.html
http://portmedia.sourceforge.net/portmidi/doxygen/portmidi_8h-source.html
"""

from __future__ import print_function
import time

from .parser import Parser
from . import portmidi_wrapper as pm

debug = False

def dbg(*args):
    if debug:
        print('DBG:', *args)

initialized = False

def _initialize():
    """
    Initialize PortMidi. If PortMidi is already initialized,
    it will do nothing.
    """

    global initialized

    dbg('initialize()')

    if initialized:
        dbg('  (already initialized)')
        pass
    else:        
        pm.lib.Pm_Initialize()        

        initialized = True
        # Todo: This screws up __del__() for ports
        # atexit.register(_terminate)

def _terminate():
    """
    Terminate PortMidi. This will be called by an atexit() handler.
    If you call it after it has already terminated, it will do nothing.
    """

    global initialized

    dbg('terminate()')
    if initialized:
        pm.lib.Pm_Terminate()
        initialized = False
    else:
        dbg('  (already terminated)')


class _Device(dict):
    """
    PortMidi device.
    """
    def __init__(self, name, isinput, isoutput, **kw):
        self.name = name
        self.isinput = isinput
        self.isoutput = isoutput
        for (name, value) in kw.items():
            setattr(self, name, value)

    def __repr__(self):
        args = []
        for (name, value) in self.__dict__.items():
            if not name.startswith('_'):
                arg = '%s=%r' % (name, value)
                args.append(arg)

        args = ', '.join(args)

        return '_Device(%s)' % args

def _get_device(id):
    info_ptr = pm.lib.Pm_GetDeviceInfo(id)
    if info_ptr:
        devinfo = info_ptr.contents

        if repr(devinfo.name).startswith('b'):
            # Python 3
            name = devinfo.name.decode('ascii')
        else:
            name = devinfo.name

        dev = _Device(name=name,
                      isinput=devinfo.input != 0,
                      isoutput=devinfo.output != 0,
                      id=id,
                      interf=devinfo.interf,
                      opened=devinfo.opened != 0)

        return dev
    return None

def _get_devices():
    """
    Get all PortMidi devices.
    """

    _initialize()

    devices = []

    for id in range(pm.lib.Pm_CountDevices()):
        dev = _get_device(id)
        if dev is not None:
            devices.append(dev)

    return devices

def get_input_names():
    """
    Return a list of all input port names.
    These can be passed to Input().
    """

    return [dev.name for dev in _get_devices() if dev.isinput]

def get_output_names():
    """
    Return a list of all input port names.
    These can be passed to Output().
    """

    return [dev.name for dev in _get_devices() if dev.isoutput]

def _check_err(err):
    if err < 0:
        raise IOError(pm.lib.Pm_GetErrorText(err))

class Port:
    """
    Abstract base class for Input and Output ports
    """
    def __init__(self, name=None):
        self.name = name
        self._init()
        self.closed = False

    def close(self):
        dbg('closing port')

        if hasattr(self, 'closed') and not self.closed:
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
        cl = self.__class__.__name__
        return '%s(%r)' % (cl, self.name)

class Input(Port):
    """
    PortMidi Input
    """

    def _init(self):
        """
        Create an input port.

        The argument 'name' is the name of the device to use. If not passed,
        the default device is used instead (which may not exists on all systems).
        """

        _initialize()

        self._parser = Parser()

        if self.name is None:
            self._devid = pm.lib.Pm_GetDefaultInputDeviceID()
            if self._devid < 0:
                raise IOError('No default input found')
            self.name = _get_device(self._devid).name
        else:
            for dev in _get_devices():
                if dev.name == self.name and dev.isinput:
                    self._devid = dev.id
                    break
            else:
                raise IOError('Unknown input device %r' % name)

        self.stream = pm.PortMidiStreamPtr()
        
        dbg('opening input')

        err = pm.lib.Pm_OpenInput(pm.byref(self.stream),
                                  self._devid,  # inputDevice
                                  pm.null,   # inputDriverInfo
                                  1000,      # bufferSize
                                  pm.NullTimeProcPtr,   # time_proc
                                  pm.null,   # time_info
                                  )
        _check_err(err)

        self._open = True

    def _print_event(self, event):
        value = event.message & 0xffffffff
        dbg_bytes = []
        for i in range(4):
            byte = value & 0xff
            dbg_bytes.append(byte)
            value >>= 8
        print(' '.join('%02x' % b for b in dbg_bytes))

    def poll(self):
        """
        Read and parse whatever events have arrived since the last time we were called.
        
        Returns the number of messages ready to be received.
        """

        if self.closed:
            return

        # I get hanging notes if MAX_EVENTS > 1, so I'll have to resort
        # to calling Pm_Read() in a loop until there are no more pending events.

        MAX_EVENTS = 1
        BufferType = pm.PmEvent * MAX_EVENTS  # Todo: this should be allocated once
        buffer = BufferType()

        while pm.lib.Pm_Poll(self.stream):

            num_events = pm.lib.Pm_Read(self.stream, buffer, 1)
            _check_err(num_events)

            #
            # Read the event
            #

            event = buffer[0]

            #if debug:
            #    self._print_event(event)

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

    def __iter__(self):
        """
        Iterate through all available messages.
        """

        self.poll()
        while self._parser.messages:
            yield self._parser.get_msg()

class Output(Port):
    """
    PortMidi Output
    """
    def _init(self):
        """
        Create an output port.

        The argument 'name' is the name of the device to use. If not passed,
        the default device is used instead (which may not exists on all systems).
        """

        if self.name is None:
            self._devid = pm.lib.Pm_GetDefaultOutputDeviceID()
            if self._devid < 0:
                raise IOError('No default output found')
            self.name = _get_device(self._devid).name
        else:
            for dev in _get_devices():
                if dev.name == self.name and dev.isoutput:
                    self._devid = dev.id
                    break
            else:
                raise IOError('Unknown output %r' % name)

        self.stream = pm.PortMidiStreamPtr()
        
        err = pm.lib.Pm_OpenOutput(pm.byref(self.stream),
                                   self._devid,  # outputDevice
                                   pm.null,   # outputDriverInfo
                                   0,         # bufferSize (ignored when latency=0?)
                                   pm.NullTimeProcPtr,   # time_proc (default to internal clock)
                                   pm.null,   # time_info
                                   0,         # latency
                                   )
        _check_err(err)

        self._open = True

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
