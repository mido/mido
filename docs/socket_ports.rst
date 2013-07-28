Socket Ports - MIDI over TCP/IP
================================

About Socket Ports
-------------------

Socket ports allow to send MIDI messages over for example the wireless
network. You can set up a server and send messages to it that you can
then relay to soft synths or external equipment.

The protocol is standard MIDI bytes over a TCP stream.

Socket ports behave like any other Mido I/O port, with all the usual
``send()``, ``receive()``, ``pending()`` and other methods.


A Simple Server
----------------

A server can be set up with::

    from mido.sockets import PortServer

    with PortServer('', 8080) as server:
        while 1:
            client = server.accept()
            for message in client:
                print(message)

This will print all messages from the client until the client
disconnects, and then wait for another client. ``client`` is a
``SocketPort`` object.


Connecting to a Server
-----------------------

You can connect to a server by creating a ``SocketPort``, passing the
host name and port as arguments::

    from mido.sockets import SocketPort

    server = SocketPort('localhost', 8080)
    server.send(mido.Message('program_change', program=20))
    server.close()

Socket ports are two-way, but usually it's best to send only once way.


Parsing an Address
-------------------

A function is provided for parsing addresses::

    hostname, port = parse_address('localhost:8080')

The ``name`` attribute of a ``SocketPort`` has this format, so you can do::

    >>> port = SocketPort('localhost', 8080)
    >>> port.name
    'localhost:8080'
    >>> port
    <open I/O port 'localhost:8080' (socket)>

See examples/socket/ for more examples.
