About MIDI
===========

MIDI is a simple binary protocol for communicating with synthesizers
and other electronic music equipment.

It was developed in 1981 by Dave Smith and Chet Wood of Sequential
Circuits with the assistance of Ikutaro Kakehashi of Roland. MIDI was
quickly embraced by all the major synth manufacturers, and led to
developments such as microcomputer sequencers, and with them the
electronic home studio. Although many attempts have been made to
replace it, it is still the industry standard.

MIDI was designed for the 8-bit micro controllers found in synthesizers
at the beginning of the 80's. As such, it is a very minimal
byte-oriented protocol. The message for turning a note on is only
three bytes long (here shown in hexadecimal)::

    92 3C 64

This message consists of::

    92 -- 9 == message type note on
          2 == channel 2

    3C -- note 60 (middle C)

    64 -- velocity (how hard the note is hit)

The first byte is called a status byte. It has the upper bit set,
which is how you can tell it apart from the following data
bytes. Data bytes as thus only 7 bits (0..127).

Each message type has a given number of data bytes, the exception
being the System Exclusive message which has a start and a stop byte,
and can have any number of data bytes in-between these two.

Messages can be divided into four groups:

* Channel messages. These are used to turn notes on and off, to change
  patches and change controllers (pitch bend, modulation wheel, pedal
  and many others). 

* System common messages.

* System real time messages, the include start, stop, continue, song
  position (for playback of songs) and reset.

* System Exclusive messages (often called Sysex messages). These are
  used for sending and receiving device specific such as patch data.


Some Examples of Messages
--------------------------

::

    # Turn on and off middle C
    92 3C 64  note_on channel=2 note=60 velocity=100
    82 3C 64  note_off channel=2 note=60 velocity=100

    # Program change with program=4 on channel 2.
    # (The synth will switch to another sound.)
    C2 04

    # Continue. (Starts a song that has been paused.)
    FB

    # Data request for the Roland SH-201 synthesizer.
    F0 41 10 00 00 16 11 20 00 00 00 00 00 00 21 3F F7


More About MIDI
----------------

* `Wikipedia's page on MIDI <https://en.wikipedia.org/wiki/Midi>`_

* `MIDI Manufacturers Association <http://www.midi.org/>`_

* `A full table of MIDI messages <http://www.midi.org/techspecs/midimessages.php>`_

