"""
Backend for python-rtmidi:

http://pypi.python.org/pypi/python-rtmidi/
"""
from __future__ import absolute_import
import os
import sys
import time
import threading

PY2 = (sys.version_info.major == 2)
if PY2:
    import Queue as queue
else:
    import queue

import rtmidi
from .. import ports
from ..parser import Parser

def _get_api_lookup():
    api_to_name = {}
    name_to_api = {}

    for name in dir(rtmidi):
        if name.startswith('API_'):
            value = getattr(rtmidi, name)
            name = name.replace('API_', '')
            name_to_api[name] = value
            api_to_name[value] = name

    return api_to_name, name_to_api


_api_to_name, _name_to_api = _get_api_lookup()


def _get_api_id(name=None):
    if name is None:
        return rtmidi.API_UNSPECIFIED

    try:
        api = _name_to_api[name]
    except KeyError:
        raise ValueError('unknown API {}'.format(name))

    if name in get_api_names():
        return api
    else:
        raise ValueError('API {} not compiled in'.format(name))


def get_devices(api=None, **kwargs):
    devices = []

    rtapi = _get_api_id(api)

    input_names = set(rtmidi.MidiIn(rtapi=rtapi).get_ports())
    output_names = set(rtmidi.MidiOut(rtapi=rtapi).get_ports())

    for name in sorted(input_names | output_names):
        devices.append({
                'name': name,
                'is_input': name in input_names,
                'is_output': name in output_names,
                })

    return devices


def get_api_names():
    return [_api_to_name[n] for n in rtmidi.get_compiled_api()]


def _open_port(client, name, virtual=False):
    ports = client.get_ports()
    if len(ports) == 0:
        raise IOError('no ports available')

    if virtual:
        client.open_virtual_port(name)
    else:
        if name is None:
            name = ports[0]
            port_id = 0
        elif name in ports:
            port_id = ports.index(name)
        else:
            raise IOError('unknown port {!r}'.format(name))

        try:
            client.open_port(port_id)
        except RuntimeError as err:
            raise IOError(*err.args)

    return name


class Port(object):
    def __init__(self, name=None, is_input=False, is_output=False,
                 client_name=None, virtual=False, api=None,
                 callback=None, autoreset=False, **kwargs):

        if client_name is not None:
            virtual = True

        if virtual and name is None:
            raise IOError('virtual port must have a name')

        if is_input is is_output is None:
            raise IOError('port must be input or output or both')

        rtapi = _get_api_id(api)

        self.virtual = virtual
        self.is_input = is_input
        self.is_output= is_output
        self.autoreset = autoreset
        self.closed = False

        if client_name:
            self.virtual = True

        self._lock = threading.RLock()
        self._callback = None

        self._midiin = self._midiout = None
        input_name = output_name = None

        if is_input:
            self._midiin = rtmidi.MidiIn(name=client_name, rtapi=rtapi)
            input_name = _open_port(self._midiin, name, self.virtual)

            self._midiin.ignore_types(False, False, True)
            self._queue = queue.Queue()
            self._parser = Parser()
            self.callback = callback

        if is_output:
            self._midiout = rtmidi.MidiOut(name=client_name, rtapi=rtapi)
            output_name = _open_port(self._midiout, name, self.virtual)
            # Turn of ignore of sysex, time and active_sensing.

        # What if is_input and is_output and these differ?
        self.name = input_name or output_name

        client = self._midiin or self._midiout
        self.api = _api_to_name[client.get_current_api()]

    def close(self):
        # Note: not thread safe.
        if not self.closed:
            if self.is_input:
                self._midiin.close_port()
                del self._midiin

            if self.is_output:
                if self.autoreset:
                    self.reset()

                self._midiout.close_port()
                del self._midiout

            # Virtual ports are closed when this is deleted.
            self.closed = True

    def send(self, msg):
        self._check_closed()
        if not self.is_output:
            raise IOError('not an output port')

        with self._lock:
            self._midiout.send_message(msg.bytes())

    def panic(self):
        self._check_closed()
        ports.send_panic(self)

    def reset(self):
        self._check_closed()
        ports.send_reset(self)

    panic.__doc__ = ports.send_panic.__doc__
    reset.__doc__ = ports.send_reset.__doc__

    # In Python 2 queue.get() doesn't respond to CTRL-C. A workaroud is
    # to call queue.get(timeout=100) (very high timeout) in a loop, but all
    # that does is poll with a timeout of 50 milliseconds. This results in
    # much too high latency.
    #
    # It's better to do our own polling with a shorter sleep time.
    #
    # See Issue #49 and https://bugs.python.org/issue8844
    def receive(self, block=True):
        self._check_closed()
        if not self.is_input:
            raise IOError('not an input port')

        if PY2:
            sleep_time = ports.get_sleep_time()
            while True:
                try:
                    return self._queue.get_nowait()
                except queue.Empty:
                    if block:
                        time.sleep(sleep_time)
                        continue
                    else:
                        return None
        else:
            try:
                return self._queue.get(block=block)
            except queue.Empty:
                return None

    def poll(self):
        return self.receive(block=False)

    def iter_pending(self):
        while True:
            msg = self.poll()
            if msg:
                yield msg
            else:
                return

    def __iter__(self):
        while True:
            yield self.receive()

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, func):
        with self._lock:
            self._midiin.cancel_callback()

            if func:
                # First send all queued messages to the callback.
                while True:
                    try:
                        func(self._queue.get_nowait())
                    except queue.Empty:
                        break

            if func is None:
                self._midiin.set_callback(self._feed_queue)
                self._callback = None
            else:
                self._midiin.set_callback(self._feed_callback)
                self._callback = func

    def _check_closed(self):
        if self.closed:
            raise IOError('port is closed')

    def _feed_queue(self, msg_data, data):
        self._parser.feed(msg_data[0])
        for msg in self._parser:
            self._queue.put(msg)

    def _feed_callback(self, msg_data, data):
        self._parser.feed(msg_data[0])
        for msg in self._parser:
            self._callback(msg)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return False

    def __repr__(self):
        if self.closed:
            state = 'closed'
        else:
            state = 'open'

        capabilities = self.is_input, self.is_output
        port_type = {
            (True, False): 'input',
            (False, True): 'output',
            (True, True): 'I/O port',
            }[capabilities]

        if self.virtual:
            port_type = 'virtual ' + port_type

        name = self.name or ''

        return '<{} {} {!r} (RtMidi/{})>'.format(
            state, port_type, name, self.api)


def open_input(name=None, **kwargs):
    return Port(name=name, is_input=True, **kwargs)


def open_output(name=None, **kwargs):
    return Port(name=name, is_output=True, **kwargs)


def open_ioport(name=None, **kwargs):
    return Port(name=name, is_input=True, is_output=True, **kwargs)


Input = open_input
Output = open_output
IOPort = open_ioport
