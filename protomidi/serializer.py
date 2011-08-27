"""
For now I have a module "parser" and a module "serializer". I am wondering
if this is a good way to organize the code.

There is more than one way to serialize a MIDI message.

  - bytes / bytearray:  bytearray(b'\x90<\x7f')
  - hex dump:           90 3c 7f
  - repr():             note_on(time=0, channel=0, note=60, velocity=127)

Perhaps the encode / decode implementation for each of these belong together.

There's one thing I just realized: The MIDI message itself should not know
how long it is.

I was going to have it compute its length in bytes and have it return that
in its __len__() method. But MIDIMessage() is an abstract MIDI message. It
is not actually a string of bytes.
"""
