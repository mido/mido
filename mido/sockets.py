"""
Experimental MIDI over TCP/IP.
"""

import time
import socket
import select
from collections import deque
from .parser import Parser
from .ports import MultiPort, BaseInput, BaseOutput, multi_iter_pending, sleep
from .messages import parse_string

def _is_readable(socket):
    """Return True if there is data to be read on the socket."""

    timeout = 0
    (rlist, wlist, elist) = select.select(
        [socket.fileno()], [], [], timeout)
    
    return bool(rlist)

class Server(MultiPort):
    # Todo: queue size.

    def __init__(self, host, portno):
        BaseInput.__init__(self, format_address(host, portno))
        self.ports = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self._socket.setblocking(True)
        self._socket.bind((host, portno))
        self._socket.listen(backlog)

    def _get_device_type(self):
        return 'server'

    def _close(self):
        # Close all connections.
        for port in self.ports:
            port.close()
        self._socket.close()

    def _update_ports(self):
        """Remove closed port ports."""
        self.ports = [port for port in self.ports if not port.closed]

    def accept(self, block=True):
        """
        Accept a connection from a client.

        Will block until there is a new connection, and then return a
        SocketPort object.

        If block=False, None will be returned if there is no
        new connection waiting.
        """
        if not block and not _is_readable(self._socket):
            return None

        self._update_ports()

        conn, (host, port) = self._socket.accept()
        return SocketPort(host, port, conn=conn)

    def _pending():
        port = self.accept(block=False)
        if port:
            self.ports.append(port)
        self._update_ports()
        self._messages.extend(multi_iter_pending(self.ports))


class SocketPort(BaseInput, BaseOutput):
    def __init__(self, host, portno, conn=None):
        self.name = format_address(host, portno)
        self.closed = False
        self._parser = Parser()
        self._messages = self._parser._parsed_messages

        if conn is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setblocking(True)
            self._socket.connect((host, portno))
        else:
            self._socket = conn

        self._file = self._socket.makefile('r+', bufsize=0)

    def _get_device_type(self):
        return 'socket'

    def _pending(self):
        while 1:
            if not _is_readable(self._socket):
                break

            try:
                byte = self._file.read(1)
            except socket.error:
                # Todo: handle this more gracefully?
                self.close()
                break
            if byte == '':
                # End of stream.
                self.close()
                break
            else:
                self._parser.feed_byte(ord(byte))

    def _send(self, message):
        self._file.write(message.bin())
        self._file.flush()

    def _close(self):
        self._socket.close()


def connect(host, portno):
    """Connect to a socket port server.

    The return value is a SocketPort object connected to another
    SocketPort object at the server end. Messages can be sent either way.
    """
    return SocketPort(host, portno)


def parse_address(address):
    """Parse and address on the format host:port.

    Returns a tuple (host, port). Raises ValueError if format is
    invalid or port is not an integer or out of range.
    """
    words = address.split(':')
    if len(words) != 2:
        raise ValueError('address must contain exactly one colon')

    host, port = words
    try:
        port = int(port)
    except ValueError:
        raise ValueError('port number must be an integer')

    # Note: port 0 is not allowed.
    if not 0 < port < (2**16):
        raise ValueError('port number out of range')

    return (host, port)


def format_address(host, portno):
    return '{}{:d}'.format(host, portno)

