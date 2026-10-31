.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Message Types
=============


Supported Messages
------------------

==============  ==============================
Name            Keyword Arguments / Attributes
==============  ==============================
note_off        channel note velocity
note_on         channel note velocity
polytouch       channel note value
control_change  channel control value
program_change  channel program
aftertouch      channel value
pitchwheel      channel pitch
sysex           data
quarter_frame   frame_type frame_value
songpos         pos
song_select     song
tune_request
clock
start
continue
stop
active_sensing
reset
==============  ==============================

``quarter_frame`` is used for SMPTE time codes.


Parameter Types
---------------

===========  ======================  ================
Name         Valid Range             Default Value
===========  ======================  ================
channel      0..15                   0
frame_type   0..7                    0
frame_value  0..15                   0
control      0..127                  0
note         0..127                  0
program      0..127                  0
song         0..127                  0
value        0..127                  0
velocity     0..127                  64
data         (0..127, 0..127, ...)   () (empty tuple)
pitch        -8192..8191             0
pos          0..16383                0
time         any integer or float    0
===========  ======================  ================

.. note::

    Mido numbers channels 0 to 15 instead of 1 to 16. This makes them
    easier to work with in Python but you may want to add and subtract
    1 when communicating with the user.

``velocity`` is how fast the note was struck or released. It defaults
to 64 so that if you don't set it, you will still get a reasonable
value. (64 is the recommended default for devices that don't support
it attack or release velocity.)

The ``time`` is used in MIDI files as delta time.

The ``data`` parameter accepts any iterable that generates numbers in
0..127. This includes::

    mido.Message('sysex', data=[1, 2, 3])
    mido.Message('sysex', data=range(10))
    mido.Message('sysex', data=(i for i in range(10) if i % 2 == 0))
