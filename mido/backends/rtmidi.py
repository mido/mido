"""Backend for python-rtmidi:

http://pypi.python.org/pypi/python-rtmidi/
"""
from __future__ import absolute_import
import os
import sys
import time
import threading
from ..py2 import PY2

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


class Port(ports.BaseIOPort):
    """RtMidi port

    The following methods are thread safe::

        send()
        reset()
        panic()

        receive()
        poll()
        iter_pending()
        __iter__()

        @callback  (set and clear callback)

    When self.callback is set it will be called every time a messages
    comes in::

        RtMidi -> self._feed_callback -> self.callback

    If self.callback is not set the messages will instead be put in a
    queue where other threads can get them::

                                          Consumer threads:

                                            /-> receive()
        RtMidi -> self._feed_queue -> queue --> receive()
                                            \-> poll()

    The queue ensures that the port is thread safe and that threads
    actually block rather than poll and wait (Python 3 only, see
    comment inside receive()`.

    send() uses a lock for thread safety.
    """
    # We do our own locking.
    locking = False

    def _open(self, is_input=False, is_output=False,
              client=None, virtual=False, api=None,
              callback=None, **kwargs):

        if client is not None:
            virtual = True

        if virtual and self.name is None:
            raise IOError('virtual port must have a name')

        if is_input is is_output is None:
            raise IOError('port must be input or output or both')

        rtapi = _get_api_id(api)

        self.virtual = virtual
        self.is_input = is_input
        self.is_output= is_output

        if client:
            self.virtual = True

        self._callback = None

        self._midiin = self._midiout = None
        input_name = output_name = None

        if is_input:
            self._midiin = rtmidi.MidiIn(name=client, rtapi=rtapi)
            input_name = _open_port(self._midiin, self.name, self.virtual)

            self._midiin.ignore_types(False, False, True)
            self._queue = queue.Queue()
            self._parser = Parser()
            self.callback = callback

        if is_output:
            self._midiout = rtmidi.MidiOut(name=client, rtapi=rtapi)
            output_name = _open_port(self._midiout, self.name, self.virtual)
            # Turn of ignore of sysex, time and active_sensing.

        # What if is_input and is_output and these differ?
        self.name = input_name or output_name

        client = self._midiin or self._midiout
        self.api = _api_to_name[client.get_current_api()]
        self._device_type = 'RtMidi/{}'.format(self.api)


    def _close(self):
        # Note: not thread safe.
        if self.is_input:
            self._midiin.close_port()
            del self._midiin

        if self.is_output:
            if self.autoreset:
                self.reset()

            self._midiout.close_port()
            del self._midiout

    def _send(self, msg):
        """Send a message on the port."""
        if not self.is_output:
            raise ValueError('not an output port')

        with self._lock:
            self._midiout.send_message(msg.bytes())

    def _receive(self, block=True):
        # In Python 2 queue.get() doesn't respond to CTRL-C. A workaroud is
        # to call queue.get(timeout=100) (very high timeout) in a loop, but all
        # that does is poll with a timeout of 50 milliseconds. This results in
        # much too high latency.
        #
        # It's better to do our own polling with a shorter sleep time.
        #
        # See Issue #49 and https://bugs.python.org/issue8844
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

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, func):
        if not self.is_input:
            raise ValueError('not an input port')

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

    def _feed_queue(self, msg_data, data):
        self._parser.feed(msg_data[0])
        for msg in self._parser:
            self._queue.put(msg)

    def _feed_callback(self, msg_data, data):
        self._parser.feed(msg_data[0])
        for msg in self._parser:
            self._callback(msg)


# A bit of trickery to keep the Backend object happy.

def Input(name=None, **kwargs):
    return Port(name=name, is_input=True, **kwargs)


def Output(name=None, **kwargs):
    return Port(name=name, is_output=True, **kwargs)


def IOPort(name=None, **kwargs):
    return Port(name=name, is_input=True, is_output=True, **kwargs)
