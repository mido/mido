Socket Ports - MIDI over TCP/IP
================================

About Socket Ports
-------------------

Socket ports allow you to send MIDI messages over a computer
network.

The protocol is standard MIDI bytes over a TCP stream.


Sending Messages to a Server
-----------------------------

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


Turning Things on their Head
-----------------------------

If you want the server to send messages the client, you can instead
do::

    server = PortServer('localhost', 8080):
    while 1:
        server.send(message)
        ...

and then on the client side::

    for message in connect('localhost', 8080):
        print(message)

The client will now print any message that the server sends. Each
message that the server sends will be received by all connected
clients.


Under the Hood
---------------

The examples above use the server and client ports as normal I/O
ports. This makes it easy to write simple servers, but you don't have
any control connections and the way messages are sent and received.

To get more control, you can ignore all the other methods of the
``PortServer`` object and use only ``accept()``. Here's a simple
server implemented this way::

    with PortServer('localhost', 8080) as server:
        while 1:
            client = server.accept()
            for message in client:
                print(message)

``accept()`` waits for a client to connect, and returns a SocketPort
object which is connected to the SocketPort object returned by
``connect()`` at the other end.

The server above has one weakness: it allows only one connection at a
time. You can get around this by using ``accept(block=False)``. This
will return a SocketPort if there is a connection waiting and None if
there is connection yet.

Using this, you can write the server any way you like, for example::

    with PortServer('localhost', 8080) as server:
        clients = []
        while 1:
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

