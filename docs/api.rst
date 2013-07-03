.. _api:

Developer Interface
====================

.. module:: mido

.. autofunction:: new

.. autofunction:: input
.. autofunction:: output
.. autofunction:: ioport

.. autofunction:: input_names
.. autofunction:: output_names
.. autofunction:: ioport_names


Parsing and Parser class
-------------------------

.. autofunction:: parse
.. autofunction:: parse_all
.. autoclass:: Parser
   :inherited-members:


Message Objects
----------------

.. autoclass:: mido.messages.Message
   :inherited-members:


Port Objects
-------------

.. autoclass:: mido.portmidi.Input
   :inherited-members:

.. autoclass:: mido.portmidi.Output
   :inherited-members:


IOPort Objects
---------------

`IOPort` objects has all the attibutes and methods of `Input` and
`Output` objects.

.. autoclass:: mido.ports.IOPort
   :inherited-members:


Useful Port Functions
----------------------

.. module:: mido.ports

.. autofunction:: multi_receive
.. autofunction:: multi_iter_pending


String Serialization
---------------------

There is not `format_as_string()`, but you can use `str(message)`.

.. autofunction:: parse_string
.. autofunction:: parse_string_stream
