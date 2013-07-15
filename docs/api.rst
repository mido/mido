.. _api:

Developer Interface
====================

Creating Message and Opening Ports
-----------------------------------

.. module:: mido

.. autofunction:: open_input
.. autofunction:: open_output
.. autofunction:: open_ioport

.. autofunction:: get_input_names
.. autofunction:: get_output_names
.. autofunction:: get_ioport_names


Parsing and Parser class
-------------------------

.. autofunction:: parse
.. autofunction:: parse_all
.. autoclass:: Parser
   :members:
   :inherited-members:


Message Objects
----------------

.. autoclass:: mido.Message
   :members:
   :inherited-members:


Port Objects
-------------

.. autoclass:: mido.portmidi.Input
   :members:
   :inherited-members:

.. autoclass:: mido.portmidi.Output
   :members:
   :inherited-members:


IOPort Objects
---------------

`IOPort` contain an `Input` and an `Output` object, and forwards all
method calls to these.

.. autoclass:: mido.ports.IOPort
   :members:
   :inherited-members:


Useful Port Functions
----------------------

.. module:: mido.ports

.. autofunction:: multi_receive
.. autofunction:: multi_iter_pending


String Serialization
---------------------

.. module:: mido

There is not `format_as_string()`, but you can use `str(message)`.

.. autofunction:: parse_string
.. autofunction:: parse_string_stream
