Writing a New Backend
=====================

A backend is a Python module with one or more of these::

    Input -- an input port class
    Output -- an output port class
    IOPort -- an I/O port class
    get_devices() -- returns a list of devices

Once written, the backend can be used by setting the environment
variable ``MIDO_BACKEND`` or by calling ``mido.set_backend()``. In
both cases, the path of the module is used.

``Input``

   And input class for ``open_input()``. This is only required if the
   backend supports input.

``Output``

   And output class for ``open_output()``. This is only required if the
   backend supports output.

``IOPort``

   An I/O port class for ``open_ioport()``. If this is not found,
   ``open_ioport()`` will return ``mido.ports.IOPort(Input(),
   Output())``.

``get_devices(**kwargs)``

   Returns a list of devices, where each device is dictionary with at
   least these three values::

      {
        'name': 'Some MIDI Input Port',
        'is_input': True,
        'is_output': False,
      }

   These are used to build return values for ``get_input_names()`` etc..
   This function will also be available to the user directly.

For examples, see ``mido/backends/``.
