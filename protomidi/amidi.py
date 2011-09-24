"""
"""

from __future__ import print_function
import sys
import subprocess

from .serializer import serialize
from .parser import Parser
from .msg import opcode2msg

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

def _get_all_devices():
    devices = []

    p = subprocess.Popen(['amidi', '-l'], stdout=subprocess.PIPE)
    for line in p.stdout:

        line = line.strip()
        dir, port, name = line.split(None, 2)
        if dir == 'Dir':
            continue  # Skip heading line

        for d in dir:
            dev = Device()
            dev['name'] = name
            dev['port'] = port
            dev['input'] = (d == 'I')
            dev['output'] = (d == 'O')

            devices.append(dev)
        
    return devices

def get_devices(**query):
    """
    Somewhat experimental function to get device info
    as a list of Device objects.
    """

    devices = []

    for dev in _get_all_devices():
        for (name, value) in query.items():
            if name in dev and dev[name] != value:
                    break
        else:
            devices.append(dev)

    return devices
            

class Error(Exception):
    pass

class Port:
    pass

hexchars = '0123456789ABCDEFabcdef'

class Input(Port):
    """
    PortMidi Input
    """

    # Todo: default device

    def __init__(self, name=None):
        devices = get_devices(name=name)
        if devices:
            dev = devices[0]
        else:
            raise ValueError('Unknown input device')

        self._parser = Parser()
        self._proc = subprocess.Popen(['amidi', '-p', dev.port, '-d'],
                                      stdout=subprocess.PIPE)

    def _parse(self):
        # Todo:
        #   - make it read more than one byte at a time
        #   - make sure this doesn't block
        a = self._proc.stdout.read(1)
        if a in hexchars:
            b = self._proc.stdout.read(1)
            if b in hexchars:
                byte = int(a+b, base=16)
                self._parser.put_byte(byte)

        return self._parser.num_pending()

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

    # Todo: default device

    def __init__(self, name=None):
        devices = get_devices(name=name)
        if devices:
            self.dev = devices[0]
        else:
            raise ValueError('Unknown input device')
    
    def send(self, msg):
        """Send a message on the output port"""

        # This is very inefficient, since it starts amidi
        # for every message.

        hexdata = ' '.join(['%02X' % byte for byte in serialize(msg)])
        # print(hexdata)
        subprocess.check_call(['amidi', '-p', self.dev.port, '-S', hexdata])
