Socket Ports - MIDI over TCP/IP
================================

About Socket Ports
-------------------

Socket ports allow you to send MIDI messages over a computer
network.

The protocol is standard MIDI bytes over a TCP stream.


A Simple Server and Client
---------------------------

First, let's import some things::

    from mido.sockets import Server, connect

To get a connection going you must first set up a server::

    for message in Server('localhost', 8080):
        print(message)

You can then connect to the server and send it messages::

    output = connect('localhost', 8080):
    output.send(message)

If you want to turn things on their head, you can let the server send
messages to the clients::

    with Server('localhost', 8080) as output:
        while 1:
            output.send(message)

and then on the client side::

    input = connect()
    for message in connect('localhost', 8080):
        print(message)

The client will now print any message that the server sends.


Under the Hood
---------------

The examples above use the server and client ports as normal I/O
ports. This makes it easy to write simple servers, but you don't have
any control of the client connections.

To get more control, you can ignore the port methods of the Server
object and use only the ``accept()`` method. Here's a
simple server implemented this way::

    with Server('localhost', 8080) as server:
        while 1:
            # Wait for a client.
            client = server.accept()

            # Print all messages until the client disconnects.
            for message in client:
                print(message)

This will only handle one client at a time. To get around this, you
can use the non-blocking version of ``accept()``. You now need to keep
a list of clients::

    with Server('localhost', 8080) as server:
        clients = []
        while 1:
            client = server.accept(block=False)
            if client:
                clients.append(client)
            clients = [c for c in clients if not c.closed]

            for client in clients:
                for message in client.iter_pending()
                    print(message)

            ... do other things

This is how the ``__iter__()`` method of Server is implemented.
