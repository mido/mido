from mido import sockets

server = sockets.PortServer('localhost', 8080)

while 1:
    conn = server.accept()
    for message in conn:
        print(message)
