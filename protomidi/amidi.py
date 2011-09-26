"""
MIDI I/O using amidi (ALSA raw MIDI).

This is probably inefficient, since it uses an external program. Also,
amidi is started for each message you send.

It can still be useful for sysex dumps.
"""

from __future__ import print_function
import subprocess
import select

from .serializer import serialize
from .parser import Parser
from . import io

def _get_all_devices():
    """
    Return a list of all MIDI devices.
    """

    devices = []

    p = subprocess.Popen(['amidi', '-l'], stdout=subprocess.PIPE)
    for line in p.stdout:

        line = line.strip()
        dirs, port, name = line.split(None, 2)
        if dirs == 'Dir':
            continue  # Skip heading line

        for d in dirs:
            dev = iobase.Device(name=name,
                                input=(d == 'I'),
                                output=(d == 'O'),
                                port=port)
            devices.append(dev)
        
    return devices

get_devices = iobase.make_device_query(_get_all_devices)

class Error(Exception):
    pass

class Port:
    pass

hexchars = '0123456789ABCDEFabcdef'

class Input(iobase.Input):
    """
    PortMidi Input
    """

    # Todo: default device

    def __init__(self, name=None):
        devices = get_devices(name=name)
        if devices:
            dev = devices[0]
        else:
            raise ValueError('Unknown input device %r' % name)

        self._parser = Parser()
        self._proc = subprocess.Popen(['amidi', '-p', dev.port, '-d'],
                                      stdout=subprocess.PIPE)

    def _parse(self):
        # Todo:
        #   - make it read more than one byte at a time
        #   - make sure this doesn't block

        while 1:
            (rfds, wfds, efds) = select.select([self._proc.stdout.fileno()], [], [], 0)
            if rfds:
                a = self._proc.stdout.read(1)
                if a in hexchars:
                    b = self._proc.stdout.read(1)
                    if b in hexchars:
                        byte = int(a+b, base=16)
                        self._parser.put_byte(byte)
            else:
                break

        return self._parser.num_pending()

class Output(iobase.Output):
    """
    PortMidi Output
    """

    # Todo: default device

    def __init__(self, name=None):
        devices = get_devices(name=name)
        if devices:
            self.dev = devices[0]
        else:
            raise ValueError('Unknown output device %r' % name)
    
    def _send(self, msg):
        """Send a message on the output port"""

        # This is very inefficient, since it starts amidi
        # for every message.
        hexdata = ' '.join(['%02X' % byte for byte in serialize(msg)])
        # print(hexdata)
        subprocess.check_call(['amidi', '-p', self.dev.port, '-S', hexdata])
