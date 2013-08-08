Backends
=========

To change the current backend::

    mido.set_backend('mido.backend')

This will not unload the old backend, since the module is still in
Python's cache.

You can use multiple backends at the same time. For example, to send
messages from an rtmidi port to a portmidi port::

    rt = mido.Backend('mido.backend.rtmidi')
    pm = mido.Backend('mido.backend.portmidi')

You can use multiple backends at the same time. For example, to send
messages from an rtmidi port to a portmidi port:

    rt = mido.Backend('mido.backend.rtmidi')
    pm = mido.Backend('mido.backend.portmidi')

    with rt.open_input() as input, rt.open_output() as output:
        for message in input:
            print(message)

By default, Backend will load the module on demand. This happens when
one of the open_() or get_() functions are called. If you want the
module loaded right away, you can pass ``on_demand=False``.

The new backend will not look at the environment variables. If you
want it to, you can pass ``use_environ=True``.
