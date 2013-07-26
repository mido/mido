import mido
from mido import sockets

server = sockets.PortServer('192.168.1.101', 8080)
sh201 = mido.open_output('SH-201')

while 1:
    conn = server.accept()
    for message in conn:
        print(message)
        sh201.send(message)
