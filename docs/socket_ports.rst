Socket Ports - MIDI over TCP/IP
================================

About Socket Ports
-------------------

Socket ports allow you to send MIDI messages over a computer
network.

The protocol is standard MIDI bytes over a TCP stream.


A Simple Server and Client
---------------------------

To get a connection going, you must first set up a server::

    with mido.sockets.PortServer('localhost', 8080) as server:
        while 1:
            client_port = server.accept()
            for message in client_port:
                print(message)

You can then connect to the server with::

    server_port = mido.sockets.connect('localhost', 8080):

``client_port`` and ``server_port`` are normal Mido I/O ports with all
the usual methods, so to send a message to the server, you can simply
do::

    server_port.send(message)

Messages can be sent either way, but it's usually best to settle on
one way and stick to that.


Handling More Connections
---------------------------

The example above has one weakness: only one client can connect at a
time. This is easily fixed by doing::

    with mido.sockets.PortServer('localhost', 8080) as server:
        for message in server:
            print(message)

This will iterate over all messages from all clients, and handle
connections automatically. The cost is control over connections and
client ports.

By using the non-blocking version of ``accept()``, you can get more
control and still allow multiple connections. As an example, here's
the implementation of ``for message in server`` above::

    with mido.sockets.PortServer('localhost', 8080) as server:
        clients = []
        while 1:
            # Update connection list.
            client = self.accept(block=False)
            if client:
                clients.append(client)
            clients = [client for client in clients if not client.closed]

            # Receive messages from clients.
            for message in multi_iter_pending(clients):
                print(message)

            time.sleep(0.001)
