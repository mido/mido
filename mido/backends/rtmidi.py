"""Backend for python-rtmidi:

http://pypi.python.org/pypi/python-rtmidi/
"""
from __future__ import absolute_import
import threading

import rtmidi
from .. import ports
from ..messages import Message
from ._parser_queue import ParserQueue
from .rtmidi_utils import expand_alsa_port_name


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
        devices.append({'name': name,
                        'is_input': name in input_names,
                        'is_output': name in output_names,
                        })

    return devices


def get_api_names():
    return [_api_to_name[n] for n in rtmidi.get_compiled_api()]


def _open_port(rt, name=None, client_name=None, virtual=False, api=None):

    if api == 'LINUX_ALSA':
        name = expand_alsa_port_name(rt.get_ports(), name)

    if client_name is not None:
        virtual = True

    if virtual:
        if name is None:
            raise IOError('virtual port must have a name')

        rt.open_virtual_port(name)
        return name

    port_names = rt.get_ports()
    if len(port_names) == 0:
        raise IOError('no ports available')

    if name is None:
        name = port_names[0]
        port_id = 0
    elif name in port_names:
        port_id = port_names.index(name)
    else:
        raise IOError('unknown port {!r}'.format(name))

    try:
        rt.open_port(port_id)
    except RuntimeError as err:
        raise IOError(*err.args)

    return name


class PortCommon(object):
    def _close(self):
        self._rt.close_port()


class Input(PortCommon, ports.BaseInput):
    _locking = False

    def _open(self, client_name=None, virtual=False,
              api=None, callback=None, **kwargs):

        self.closed = True
        self._callback_lock = threading.RLock()
        self._queue = ParserQueue()

        rtapi = _get_api_id(api)
        self._rt = rtmidi.MidiIn(name=client_name, rtapi=rtapi)

        self.api = _api_to_name[self._rt.get_current_api()]
        self._device_type = 'RtMidi/{}'.format(self.api)

        self.name = _open_port(self._rt, self.name, client_name=client_name,
                               virtual=virtual, api=self.api)
        self._rt.ignore_types(False, False, True)
        self.closed = False

        # We need to do this last when everything is set up.
        self.callback = callback

    # We override receive() and poll() instead of _receive() and
    # _poll() to bypass locking.
    def receive(self, block=True):
        if block:
            return self._queue.get()
        else:
            return self._queue.poll()

    def poll(self):
        return self._queue.poll()

    receive.__doc__ = ports.BaseInput.receive.__doc__
    poll.__doc__ = ports.BaseInput.poll.__doc__

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, func):
        with self._callback_lock:
            # Make sure the callback doesn't run while were swapping it out.
            self._rt.cancel_callback()

            if func:
                # Make sure the callback gets all the queued messages.
                for msg in self._queue.iterpoll():
                    func(msg)

            self._callback = func
            self._rt.set_callback(self._callback_wrapper)

    def _callback_wrapper(self, msg_data, data):
        try:
            msg = Message.from_bytes(msg_data[0])
        except ValueError:
            # Ignore invalid message.
            return

        (self._callback or self._queue.put)(msg)


class Output(PortCommon, ports.BaseOutput):
    _locking = False

    def _open(self, client_name=None, virtual=False,
              api=None, callback=None, **kwargs):

        self.closed = True
        self._send_lock = threading.RLock()

        rtapi = _get_api_id(api)
        self._rt = rtmidi.MidiOut(name=client_name, rtapi=rtapi)

        self.api = _api_to_name[self._rt.get_current_api()]
        self._device_type = 'RtMidi/{}'.format(self.api)

        self.name = _open_port(self._rt, self.name, client_name=client_name,
                               virtual=virtual, api=self.api)
        self.closed = False

    # We override send() instead of _send() to bypass locking.
    def send(self, msg):
        """Send a message on the port."""
        with self._send_lock:
            self._rt.send_message(msg.bytes())

    send.__doc__ = ports.BaseOutput.send.__doc__
