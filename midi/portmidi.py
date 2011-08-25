from __future__ import print_function
import time
from contextlib import contextmanager
# import midi

"""
Mock implementation of PortMidi wrapper. I will fill in the implementation later.

http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py
http://portmedia.sourceforge.net/portmidi/doxygen/portmidi_8h-source.html
"""

# Some kind of global variable.
# Should probably be kept in the context manager.
vars = {
    'start_time' : None,
}

def _initialize():
    """
    Initialize PortMidi. This will also start the timer.

    Do not call this method directly. Instead, use the
    context manager:

    with portmidi.portmidi():
        # Do stuff
    """
    vars['start_time'] = 
    

def _terminate():
    """
    Terminates PortMidi. This must be called to clean up, or you
    may have a nasty crash on some operating systems. If you use
    the context manager, there is no need to worry about this, as
    it calls _terminate() for you, even if exceptions occur.

    with portmidi.portmidi():
        # Do stuff
    """
    pass

@contextmanager
def portmidi():
    """
    Use this context manager around the code that uses portaudio, and
    it will automatically initialize and terminate the system for you,
    even if exceptions occur. A good place to do this is your main()
    function:
 
    def main():
        with portmidi.portmidi():
            # Do stuff
    """

    _initialize()
    yield
    _terminate()

def get_default_input_id():
    return 0

def get_default_output_id():
    return 1

def count_devices():
    return 2

def get_device_info(i):
    return "Don't know what to return here yet."

def get_time():
    """
    Returns the current value of the PortMidi timer in seconds.
    The timer is started when you initialize PortMidi.
    """
    return 0

class Input:
    """
    PortMidi Input
    """

    def __init__(self, device=None):
        """
        Create an input port. If 'device' is not passed, the default
        device is used. Todo: What exactly is 'device'? An integer?
        """
        if device == None:
            device = get_default_input_id()

    def set_filter(self, filters):
        """
        set_filter(['active', 'sysex'])
        """
        pass

    def set_channel_mask(self, mask):
        """
        16-bit bitfield.
        """
        pass

    def poll(self):
        """
        Returns True if there are one or more pending messages to
        read.
        """
        return False

    def read(self, maxnum=None):
        """
        Read up to maxnum pending messages, and return them
        in a list. If there are no pending messages, an
        empty list is returned.
        
        If maxnum is not set, all pending messages will
        be returned.
        """
        return None

class Output:
    """
    PortMidi Output
    """
    def __init__(self, device=None):
        if device == None:
            device = get_default_output_device()

    def __dealloc__(self):
        pass
    
    def send(self, msg):
        """Send a message on the output port"""
        pass
