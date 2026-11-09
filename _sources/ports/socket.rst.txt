.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Socket Ports - MIDI over TCP/IP
-------------------------------


About
^^^^^

Socket :term:`ports` allows you to send :term:`MIDI` messages over a computer
network.

The protocol is a simple MIDI bytes stream over :term:`TCP`.

.. warning::

    It is **not** :term:`rtpmidi`!


Caveats
^^^^^^^

The data is sent over an *unencrypted channel*. Also, the default server
allows connections from any host and also accepts arbitrary :term:`sysex`
messages, which could allow anyone to for example overwrite patches on
your synths (or **worse**). Use **only** on *trusted networks*.

If you need more security, you can build a *custom server* with a whitelist
of clients allowed to connect.

If *timing* is critical, *latency* and *jitter* (especially on *wireless
networks*) may make socket ports *unusable*.


Sending Messages to a Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, let's import some things::

    from mido.sockets import PortServer, connect

After that, a simple server is only two lines::

    for message in PortServer('localhost', 8080):
        print(message)

You can then connect to the server and send it messages::

    output = connect('localhost', 8080):
    output.send(message)

Each end of the connection behaves like a normal Mido I/O port, with
all the usual methods.

The host may be an host name or IP address (as a string). It may also be '',
in which case connections are accepted from any IP address on the computer.

.. todo::

    Test and clarify "Any IP address on the computer".
    Does this mean only local adresses can connect or that any connection
    from any network is allowed?


Turning Things on their Head
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want the server to send messages the client, you can instead
do::

    server = PortServer('localhost', 8080):
    while True:
        server.send(message)
        ...

and then on the client side::

    for message in connect('localhost', 8080):
        print(message)

The client will now print any message that the server sends. Each
message that the server sends will be received by all connected
clients.


Under the Hood
^^^^^^^^^^^^^^

The examples above use the server and client ports as normal Mido I/O
ports. This makes it easy to write simple servers, but you don't have
any control on connections and the way messages are sent and received.

To get more control,you can ignore all the other methods of the
``PortServer`` object and use only ``accept()``. Here's a simple
server implemented this way::

    with PortServer('localhost', 8080) as server:
        while True:
            client = server.accept()
            for message in client:
                print(message)

``accept()`` waits for a client to connect, and returns a ``SocketPort``
object which is connected to the ``SocketPort`` object returned by
``connect()`` on the other end.

The server above has one weakness: it only allows one connection at a
time. You can get around this by using ``accept(block=False)``. This
will return a ``SocketPort`` if there's a connection waiting and ``None`` if
there is connection yet.

.. todo:: Clarify "Connection waiting" vs "There is a connection yet".

Using this you can write the server any way you like, for example::

    with PortServer('localhost', 8080) as server:
        clients = []
        while True:
            # Handle connections.
            client = server.accept(block=False)
            if client:
                print('Connection from {}'.format(client.name))
                clients.append(client)

            for i, client in reversed(enumerate(clients)):
                if client.closed:
                    print('{} disconnected'.format(client.name))
                    del clients[i]

            # Receive messages.
            for client in clients:
                for message in client.iter_pending()
                    print('Received {} from {}'.format(message, client))

            # Do other things
            ...


Possible Future Additions
^^^^^^^^^^^^^^^^^^^^^^^^^

Optional HTTP-style headers could be added. As long as these are 7-bit
:term:`ASCII`, they will be counted as data bytes and ignored by clients or
servers who don't expect them.
