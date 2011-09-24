"""
This is a very thin wrapper aournd PortAudio.

Since this is written specifically for ProtoMIDI, we don't use:

  - timers
  - latency
  - filters
  - channel masks

It is better to implement these generally further up.

The API still needs a lot of work. I want to get rid of get_defoutput() and count_devices()
and replace them with something else.

http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py
http://portmedia.sourceforge.net/portmidi/doxygen/main.html
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
from .msg import opcode2msg

from . import portmidi_init as pm

debug = False

def dbg(*args):
    if debug:
        print('DBG:', *args)

initialized = False

def initialize():
    global initialized

    dbg('initialize()')

    if initialized:
        dbg('  (already initialized)')
        pass
    else:        
        pm.lib.Pm_Initialize()        

        # Start timer
        pm.lib.Pt_Start(1, pm.NullTimeProcPtr, pm.null)
        initialized = True
        atexit.register(terminate)

def terminate():
    global initialized

    dbg('terminate()')
    if initialized:
        pm.lib.Pm_Terminate()
        initialized = False
    else:
        dbg('  (already terminated)')

class Device(dict):
    """
    General device class.
    A dict with attributes will have to do for now.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except IndexError:
            raise AttributeError(name)        

def get_devices(**query):
    """
    Somewhat experimental function to get device info
    as a list of Device objects.
    """

    # Todo: raise exception on illegal query arguments
    # Todo: explain query in docstring

    devices = []

    for id in range(pm.lib.Pm_CountDevices()):
        info_ptr = pm.lib.Pm_GetDeviceInfo(id)
        if info_ptr:
            devinfo = info_ptr.contents

            skip = False
            for (name, value) in query.items():
                dev_value = getattr(devinfo, name)
                if value != dev_value:
                    skip = True
                    break

            if not skip:
                dev = Device(
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

class Port:
    pass

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

        initialize()

        self._parser = Parser()
 
        if name == None:
            self._devid = pm.lib.Pm_GetDefaultInputDeviceID()
            if self._devid < 0:
                raise Error('No default input found')
        else:
            devices = get_devices(name=name, input=1)
            if len(devices) >= 1:
                self._devid = devices[0].id
            else:
                raise Error('Unknown input device %r' % name)

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

    def __dealloc__(self):
        err = pm.lib.Pm_Abort(self.stream)
        _check_err(err)
        err = pm.lib.Pm_Close(self.stream)
        _check_err(err)

    def _parse(self):
        """
        Read and parse whatever events have arrived since the last time we were called.
        
        Returns the number of messages ready to be received.
        """

        MAX_EVENTS = 1000
        BufferType = pm.PmEvent * MAX_EVENTS  # Todo: this should be allocated once
        buffer = BufferType()

        # Third argument is length (number of messages)
        num_events = pm.lib.Pm_Read(self.stream, buffer, MAX_EVENTS)
        _check_err(num_events)

        for i in range(num_events):
            event = buffer[i]

            # The bytes are stored in the lower 16 bit of the message,
            # starting with lsb and ending with msb. Just shift and pop
            # them into the parser.
            value = event.message & 0xffffffff
            if debug:
                dbg_bytes = []
                for i in range(4):
                    byte = value & 0xff
                    dbg_bytes.append(byte)
                    value >>= 8
                print('%032x' % event.message)
                print('  ' + ' '.join('%02x' % b for b in dbg_bytes))

            for i in range(4):
                byte = value & 0xff
                self._parser.put_byte(byte)
                value >>= 8

        # Todo: the parser needs another method
        return len(self._parser._messages)
    
    def poll(self):
        """
        Return the number of messages ready to be received.
        """

        return self._parse()

    def recv(self):
        """
        Return the next pending message, or None if there are no messages.
        """

        self._parse()
        return self._parser.get_msg()

    def __iter__(self):
        """
        Iterate through pending messages.
        """

        self._parse()
        for msg in self._parser:
            yield msg

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

        initialize()
        
        if name == None:
            self._devid = pm.lib.Pm_GetDefaultOutputDeviceID()
            if self._devid < 0:
                raise Error('No default output found')
        else:
            devices = get_devices(name=name, output=1)
            if len(devices) >= 1:
                self._devid = devices[0].id
            else:
                raise Error('Unknown output device %r' % name)

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

    def __dealloc__(self):
        if 0:
            err = pm.lib.Pm_Abort(self._devid)
            _check_err(err)
            
            err = pm.lib.Pm_Close(self._devid)
            _check_err(err)

    def send(self, msg):
        """Send a message on the output port"""
        
        if msg.type == 'sysex':
            chars = pm.c_char_p(bytes(serialize(msg)))
            err = pm.lib.Pm_WriteSysEx(self.stream, 0, chars)
            _check_err(err)
        else:
            value = 0
            for byte in reversed(serialize(msg)):
                value <<= 8
                value |= byte

            # Todo: timestamp is ignored if latency=0,
            # which means we don't need this.
            now = pm.lib.Pt_Time()

            err = pm.lib.Pm_WriteShort(self.stream, now, value)
            _check_err(err)
