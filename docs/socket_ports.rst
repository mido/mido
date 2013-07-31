Socket Ports - MIDI over TCP/IP
================================

About Socket Ports
-------------------

Socket ports allow you to send MIDI messages over a computer
network. You set up a server, and clients can then connect to it. The
end points of the connection are SocketPort objects, which behave like
any other Mido I/O port.

The protocol is standard MIDI bytes over a TCP stream.


A Simple Server
----------------

The easiest way to set up a server is to do::

    with mido.sockets.PortServer('localhost', 8080) as server:
        while 1:
            client_port = server.accept()
            for message in client_port:
                print(message)

This will wait for a client to connect and then iterate over all
incoming messages until the client disconnects. It will then wait for
another client.

To connect to the server and send messages::

    with mido.sockets.connect('localhost', 8080) as server_port:
        server_port.send(mido.Message('program_change', program=10))

``client_port`` and ``server_port`` behave like normal Mido I/O ports,
with all the usual methods. (Messages can be sent either way, but it's
usually best to settle on one way and stick to that.)


Handling More Connections
---------------------------

The example above has one weakness: only one client can connect at a
time. The easiest way to get around this is to do::

    with mido.sockets.PortServer('localhost', 8080) as server:
        for message in server:
            print(message)

This will iterate over all messages from all clients, and handle
connections automatically. This is equivalent to::

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
