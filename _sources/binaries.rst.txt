.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Included Programs
=================

A few sample programs are installed with Mido and available directly from the
:term:`CLI`.

.. warning::

    These are intended to demonstrate the capabilities of Mido and used as a
    template for your own programs. These are not fully fledged and may miss
    crucial features.


mido-ports
----------

Lists all available input and output ports, shows environment variables
and the current backend module.


mido-play
---------

Plays back one or more MIDI files::

    $ mido-play song1.mid [song2.mid]


mido-serve
----------

Serves one or more ports over the network, for example::

    $ mido-serve :9080 'Integra-7'

You can now connect to this port with ``mido-forward`` (or use
``mido.sockets.connect()`` and send messages to it. The messages will
be forwarded to every port you listed (in this case 'Integra-7').


mido-connect
------------

Forwards all messages that arrive on one or more ports to a server.

For example, to use the SH-201 keyboard connected to this computer to
play sounds on the Integra-7 on a computer named ``mac.local`` (which
runs the server as above), you can do::

    $ mido-connect mac.local:9080 'SH-201'

Note that you may experience latency and jitter, so this may not be
very useful for live playing or for playing back songs.

There is also no security built in, so you should only use this on a
trusted network. (Anyone can connect and send anything, including
harmful sysex messages.)

``mido-serve`` and ``mido-connect`` are only included as fun programs
to play with, but may in the future be expanded into something more
usable.
