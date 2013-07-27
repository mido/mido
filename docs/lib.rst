.. _api:

Library Reference
==================

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

.. autoclass:: Message
   :members:
   :inherited-members:


String Serialization
---------------------

There is not `format_as_string()`, but you can use `str(message)`.

.. autofunction:: parse_string
.. autofunction:: parse_string_stream


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
