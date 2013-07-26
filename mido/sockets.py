"""
Experimental MIDI over TCP/IP.
"""

import socket
import select
from collections import deque
from .parser import Parser
from .ports import BaseInput, BaseOutput
from .messages import parse_string

class PortServer:
    # Todo: queue size.

    def __init__(self, host, port, backlog=1):
        self.host = host
        self.port = port

        #if self.host == '':
        #    family = socket.AF_UNIX
        #else:

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.socket.setblocking(True)
        self.socket.bind((self.host, self.port))
        self.socket.listen(backlog)
        
        self.file = self.socket.makefile('r+')

    def accept(self):
        conn, (host, port) = self.socket.accept()
        return SocketPort(host, port, conn=conn)

    # Todo: add __enter__() and __exit__().

class SocketPort(BaseInput, BaseOutput):
    def __init__(self, host, port, conn=None, string_protocol=False):
        self.closed = False
        self._parser = Parser()
        self._messages = self._parser._parsed_messages
        self.string_protocol = string_protocol

        if conn is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(True)
            self.socket.connect((host, port))
        else:
            self.socket = conn

        self.file = self.socket.makefile('r+')

    def _pending(self):
        while 1:
            timeout = 0
            (rlist, wlist, elist) = select.select(
                [self.socket.fileno()], [], [self.socket.fileno()], timeout)

            if not rlist:
                break

            if self.string_protocol:
                line = self.file.readline()
                if line == '':
                    # End of stream.
                    self.close()
                    return
                else:
                    message = parse_string(line)
                    self._messages.append(message)
            else:
                byte = self.file.read(1)
                if byte == '':
                    # End of stream.
                    self.close()
                    return
                else:
                    self._parser.feed_byte(ord(byte))

        return len(self._messages)

    def _send(self, message):
        if self.string_protocol:
            self.file.write('{}\n'.format(message))
        else:
            self.file.write(message.bin())

        self.file.flush()

    def _close(self):
        self.socket.close()

    def __iter__(self):
        while 1:
            for message in self.iter_pending():
                yield message

            if self.closed:
                break
            
def connect(host, port):
    return SocketPort(host, port)
