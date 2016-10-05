"""
Backend for python-rtmidi:

http://pypi.python.org/pypi/python-rtmidi/
"""
from __future__ import absolute_import
import os
import sys
import time

PY2 = (sys.version_info.major == 2)
if PY2:
    import Queue as queue
else:
    import queue

import rtmidi
from ..ports import get_sleep_time, BaseInput, BaseOutput


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

class PortCommon(object):
    def _open(self, api=None, virtual=False, **kwargs):

        rtapi = _get_api_id(api)
        opening_input = hasattr(self, 'receive')

        if opening_input:
            self._rt = rtmidi.MidiIn(rtapi=rtapi)
            self._rt.ignore_types(False, False, True)
            self._queue = queue.Queue()
            self.callback = kwargs.get('callback')
        else:
            self._rt = rtmidi.MidiOut(rtapi=rtapi)
            # Turn of ignore of sysex, time and active_sensing.

        ports = self._rt.get_ports()

        if virtual:
            if self.name is None:
                raise IOError('virtual port must have a name')
            self._rt.open_virtual_port(self.name)
        else:
            if self.name is None:
                # Todo: this could fail if list is empty.
                # In RtMidi, the default port is the first port.
                try:
                    self.name = ports[0]
                except IndexError:
                    raise IOError('no ports available')

            try:
                port_id = ports.index(self.name)
            except ValueError:
                raise IOError('unknown port {!r}'.format(self.name))

            try:
                self._rt.open_port(port_id)
            except RuntimeError as err:
                raise IOError(*err.args)

        api = _api_to_name[self._rt.get_current_api()]
        self._device_type = 'RtMidi/{}'.format(api)
        if virtual:
            self._device_type = 'virtual {}'.format(self._device_type)

    def _close(self):
        self._rt.close_port()
        del self._rt  # Virtual ports are closed when this is deleted.

class Input(PortCommon, BaseInput):
    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, func):
        self._rt.cancel_callback()

        if func:
            # First send all queued messages to the callback.
            while True:
                try:
                    func(self._queue.get_nowait())
                except queue.Empty:
                    break

        if func is None:
            self._rt.set_callback(self._feed_queue)
            self._callback = None
        else:
            self._rt.set_callback(self._feed_callback)
            self._callback = func

    def _feed_queue(self, message_data, data):
        self._parser.feed(message_data[0])
        for message in self._parser:
            self._queue.put(message)

    def _feed_callback(self, message_data, data):
        self._parser.feed(message_data[0])
        for message in self._parser:
            self._callback(message)

    # receive() implementation:
    #
    # We need to override receive() here because _receive() doesn't allow
    # us to return a messages directly and putting it in self._messages is
    # not an option.
    #
    # Todo: add doc strings.

    if PY2:
        # In Python 2 queue.get() doesn't respond to CTRL-C. A workaroud is
        # to call queue.get(timeout=100) (very high timeout) in a loop, but all
        # that does is poll with a timeout of 50 milliseconds. This results in
        # much too high latency.
        #
        # It's better to do our own polling with a shorter sleep time.
        #
        # See Issue #49 and https://bugs.python.org/issue8844

        def receive(self, block=True):
            sleep_time = get_sleep_time()
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

        def receive(self, block=True):
            try:
                return self._queue.get(block=block)
            except queue.Empty:
                return None

    receive.__doc__ = BaseInput.receive.__doc__

    def pending(self):
        return self._queue.qsize()

class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self._rt.send_message(message.bytes())
