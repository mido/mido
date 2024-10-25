.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

About MIDI
==========

A Short Introduction To MIDI
----------------------------

MIDI is a simple binary protocol for communicating with synthesizers
and other electronic music equipment.

It was developed in 1981 by Dave Smith and Chet Wood of Sequential
Systems. MIDI was quickly embraced by all the major synth
manufacturers and led to developments such as microcomputer
sequencers, and with them the electronic home studio. Although many
attempts have been made to replace it, it is still the industry
standard.

MIDI was designed for the 8-bit micro controllers found in synthesizers
at the beginning of the 80's. As such, it is a very minimal
byte-oriented protocol. The message for turning a note on is only
three bytes long (here shown in hexadecimal):

.. code-block:: text

    92 3C 64

This message consists of:

.. code-blocK:: text

    92 -- 9 == message type note on
          2 == channel 2

    3C -- note 60 (middle C)

    64 -- velocity (how hard the note is hit)

The first byte is called a ``status`` byte. It has the upper bit set,
which is how you can tell it apart from the following ``data``
bytes. Data bytes are thus *always* 7 bits (Values: 0..127).

Each message type has a given number of data bytes, the exception
being the :term:`System Exclusive` message which has a start (``SOX``) and a
stop (``EOX``) byte and any number of data bytes in-between these two:

.. code-block:: text

    F0 ... F7

Messages can be divided into four groups:

* Channel Messages. These are used to turn notes on and off, to change
  patches, and change controllers (pitch bend, modulation wheel, pedal
  and many others). There are 16 channels, and the channel number is
  encoded in the lower 4 bits (aka :term:`nibble`) of the status byte.
  Each synth can choose which channel (or channels) it responds to. This can
  typically be configured.

* System Common Messages.

* System Real Time Messages, includes ``start``, ``stop``, ``continue``,
  ``song position`` (for playback of songs) and ``reset``.

* System Exclusive Messages (often called :term:`SysEx` messages) are
  used for sending and receiving *device specific* data such as patches and
  proprietary controls.


Some Examples of Messages
-------------------------

.. code-block:: text

    # Turn on middle C on channel 2:
    92 3C 64

    # Turn it back off:
    82 3C 64

    # Change to program (sound) number 4 on channel 2:
    C2 04

    # Continue (Starts a song that has been paused):
    FB

    # Sysex data request for the Roland SH-201 synthesizer:
    F0 41 10 00 00 16 11 20 00 00 00 00 00 00 21 3F F7
