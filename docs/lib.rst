.. _api:

Library Reference
==================

Convenience Functions
----------------------

.. module:: mido

.. autofunction:: open_input
.. autofunction:: open_output
.. autofunction:: open_ioport

.. autofunction:: get_input_names
.. autofunction:: get_output_names
.. autofunction:: get_ioport_names


Ports
------

.. module:: mido.ports

.. autoclass:: BaseInput
   :members:
   :inherited-members:

.. autoclass:: BaseOutput
   :members:
   :inherited-members:

.. autoclass:: IOPort
   :members:
   :inherited-members:

.. autofunction:: multi_receive
.. autofunction:: multi_iter_pending


Messages
---------

.. module:: mido

.. autoclass:: Message
   :members:
   :inherited-members:


Parsing
--------

.. module:: mido

.. autofunction:: parse
.. autofunction:: parse_all
.. autoclass:: Parser
   :members:
   :inherited-members:


String Serialization
---------------------

.. module:: mido

.. autofunction:: parse_string
.. autofunction:: parse_string_stream
.. autofunction:: format_as_string


MIDI Files
-----------

.. module:: mido.midifiles

.. autoclass:: MidiFile
   :members:
   :inherited-members:

.. autoclass:: Track
   :members:
   :inherited-members:

.. autoclass:: MetaMessage
   :members:
   :inherited-members:


Socket Ports
-------------

.. module:: mido.sockets

.. autoclass:: PortServer
   :members:
   :inherited-members:

.. autoclass:: SocketPort
   :members:
   :inherited-members:

.. autofunction:: parse_address
