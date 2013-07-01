Mido Ports API
===============

.. code:: python

Common Attributes and Methods
------------------------------

.. code:: python

    .name -- name of the port
    .closed -- True if the port is closed
    
    .__init__(name=None) -- if name is None, open the default port
    .close() -- close the port
    .__del__() -- calls .close()
    .__enter__() -- context manager
    .__exit__()


Input Port
-----------

.. code:: python

    .receive() => message -- blocks until there is a message)
    .pending() => number of messages pending
    .__iter__() => generator that does 'yeild receive()` in a loop

    
Output Port
------------

    .__init__(name=None)
    .send(message)
