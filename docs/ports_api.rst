Mido Ports API
===============

.. code:: python

Attributes and Methods Common to Input and Output Ports
--------------------------------------------------------

.. code:: python

    .name -- name of the port
    .closed -- True if the port is closed
    
    .__init__(name=None) -- if name is None, open the default port
    .close() -- close the port
    .__del__() -- calls .close()
    .__enter__() -- context manager
    .__exit__()


Methods Specific to Input Ports
--------------------------------

.. code:: python

    .receive() => message -- blocks until there is a message
    .pending() => number of messages pending
    .__iter__() => generator that does 'yeild receive()` in a loop

    
Methods Specific to Output Ports
---------------------------------

.. code:: python

    .__init__(name=None)
    .send(message)
