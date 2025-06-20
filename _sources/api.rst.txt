.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
.. SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

.. _api:

API Reference
=============


Messages
--------

.. module:: mido

.. autoclass:: Message
   :members:
   :inherited-members:
   :undoc-members:

.. module:: mido.messages

.. todo:: Expose more of the internals? (Checks, decode…)


Frozen Messages
^^^^^^^^^^^^^^^

.. module:: mido.frozen

.. autofunction:: freeze_message
.. autofunction:: thaw_message
.. autofunction:: is_frozen

.. autoclass:: Frozen
.. autoclass:: FrozenMessage
.. autoclass:: FrozenMetaMessage
.. autoclass:: FrozenUnknownMetaMessage


Parsing
-------

.. module:: mido.parser

.. autofunction:: parse
.. autofunction:: parse_all
.. autoclass:: Parser
   :members:
   :inherited-members:
   :undoc-members:


Tokenizing
----------

.. module:: mido.tokenizer

.. autoclass:: Tokenizer
   :members:
   :inherited-members:
   :undoc-members:

.. todo: Add a dedicated section in the documentation.


Backends
--------

.. module:: mido
   :noindex:

.. autofunction:: set_backend

.. autoclass:: Backend
   :members:
   :inherited-members:
   :undoc-members:

.. module:: mido.backends

.. todo:: Expose each built-in backend internal API?


Ports
-----


Management
^^^^^^^^^^

.. module:: mido
   :noindex:

.. autofunction:: open_input
.. autofunction:: open_output
.. autofunction:: open_ioport

.. autofunction:: get_input_names
.. autofunction:: get_output_names
.. autofunction:: get_ioport_names


Socket Ports
^^^^^^^^^^^^

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


API
^^^

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
.. autofunction:: multi_send
.. autofunction:: sleep
.. autofunction:: set_sleep_time
.. autofunction:: get_sleep_time
.. autofunction:: panic_messages
.. autofunction:: reset_messages


Files
------

Standard MIDI Files
^^^^^^^^^^^^^^^^^^^

.. module:: mido
   :noindex:

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

.. autofunction:: tick2second

.. autofunction:: second2tick

.. autofunction:: bpm2tempo

.. autofunction:: tempo2bpm

.. autofunction:: merge_tracks

.. module:: mido.midifiles

.. todo: Expose more of the internal API? (meta, tracks, units…)


SYX
^^^

.. module:: mido.syx

.. autofunction:: read_syx_file

.. autofunction:: write_syx_file
