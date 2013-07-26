"""
Input filters typically wrap a generator around the iterator:

    for message in only_notes(port):
        ...

    for message in transpose(port.iter_pending(), amount=12):
        ...

Output filters can filter or add messages before they are sent on a
port. There are two ways of using these filters. The first is to
attach them to a port object:

    # Replaces the send() method with a wrapper.
    port.send = monophonic(port.send)

    # Filters can be stacked.
    port.send = other(filters(port.send))

    # Remove all filters from the port.
    del port.send

The other, and less intrusive way is:

    mono = monophonic(port.send)

    port.send()         # send a polyphonic message
    mono.send(message)  # send a monophonic message

Note that these will wrap any function that takes a message as its
only argument.

Some possible input and output filters:

    - change channel
    - drop certain channels
    - drop certain messages
    - custom filter callback
"""

import random
from .messages import Message





class monophonic(object):
    """
    Experimental! Please don't rely on this for now.

    Output filter which makes all notes on one channel monophonic.

    Example:
    
        # Wrap around only the send method.
        port.send = monophonic(port.send)

    To remove the filter:

        del port.send

    channel=0  -- the channel to apply the effect to.
    select=max  -- how to select the note to be played, when more than
                   one note is held at once. If a string is passed, then
                   the value must be one of 'min', 'max', 'first', 'last',
                   'random'. Alternatively, you can pass function that
                   takes a list of integers (note values) and returns one
                   value from that list.
    """
    # Todo: you can't change select once object is running.
    #       Use a property?
    def __init__(self, output, channel=0, select='latest'):
        self.output = output
        self.notes = []
        self.current_note = None
        self.channel = channel

        self._select = None
        self.select = select

    def _set_select(self, select):
        def first(lst):
            return lst[0]

        def latest(lst):
            return lst[-1]

        if callable(select):
            self._select = select
        else:
            select_choices = {
                'first': first,
                'latest': latest,
                'max': max,
                'min': min,
                'random': random.choice,
                }
            try:
                self._select = select_choices[select]
            except KeyError:
                choices = ' '.join(sorted(select_choices.keys()))
                raise ValueError('select must be one of: {}'.format(choices))

    def _get_select(self):
        return self._select

    select = property(fget=_get_select, fset=_set_select)
    del _get_select, _set_select

    def __call__(self, message):
        self.send(message)

    def __repr__(self):
        return 'monophonic output={} channel={} select={}'.format(
            self.output,
            self.channel,
            self.select)

    def send(self, message):
        send = self.output

        if message.type not in ['note_on', 'note_off'] or \
                message.channel != self.channel:
            send(message)
            return

        if message.type == 'note_on':
            if message.note not in self.notes:
                self.notes.append(message.note)
        elif message.type == 'note_off':
            if message.note in self.notes:
                self.notes.remove(message.note)

        # Select a new note to play.
        if self.notes:
            note = self.select(self.notes)
        else:
            note = None

        if note == self.current_note:
            return  # Same note as before, no change.

        if self.current_note is not None:
            off = Message('note_off',
                          note=self.current_note,
                          velocity=message.velocity)
            send(off)
            self.current_note = None

        if note is not None:
            on = Message('note_on',
                         note=note,
                         velocity=message.velocity)
            send(on)
            self.current_note = note

class fifth:
    def __init__(self, output):
        pass
