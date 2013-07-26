import mido
from mido import sockets

server = sockets.PortServer('192.168.1.101', 8080)
sh201 = mido.open_output('SH-201')

while 1:
    conn = server.accept()
<<<<<<< HEAD
    for message in conn:
        print(message)
        sh201.send(message)
=======
    print('New connection!')

    while 1:
        if conn.closed:
            break

        for message in conn.iter_pending():
            print(message)
            sh201.send(message)

    print('End of connection')
>>>>>>> c30e3286961df201d36065e450e79b1b204fd7f6
