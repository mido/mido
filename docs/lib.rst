.. _api:

Library Reference
==================

Messages
---------

.. module:: mido

.. autoclass:: Message
   :members:
   :inherited-members:
   :undoc-members:


Ports
------

.. autofunction:: open_input
.. autofunction:: open_output
.. autofunction:: open_ioport

.. autofunction:: get_input_names
.. autofunction:: get_output_names
.. autofunction:: get_ioport_names


Backends
---------

.. autofunction:: set_backend

.. autoclass:: Backend
   :members:
   :inherited-members:
   :undoc-members:


Parsing
--------

.. autofunction:: parse
.. autofunction:: parse_all
.. autoclass:: Parser
   :members:
   :inherited-members:
   :undoc-members:


Port Classes and Functions
---------------------------

.. module:: mido.ports

.. autoclass:: BaseInput
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseOutput
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: IOPort
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: MultiPort
   :members:
   :inherited-members:
   :undoc-members:

.. autofunction:: multi_receive
.. autofunction:: multi_iter_pending
.. autofunction:: sleep
.. autofunction:: set_sleep_time


MIDI Files
-----------

.. module:: mido.midifiles

.. autoclass:: MidiFile
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: MidiTrack
   :members: 
   :inherited-members:
   :undoc-members:

.. autoclass:: MetaMessage
   :members:
   :inherited-members:
   :undoc-members:

.. autofunction:: debug


Socket Ports
-------------

.. module:: mido.sockets

.. autoclass:: PortServer
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: SocketPort
   :members:
   :inherited-members:
   :undoc-members:

.. autofunction:: parse_address
