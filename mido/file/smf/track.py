# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from .event.meta import MetaEvent


class MidiTrack(list):
    @property
    def name(self):
        """Name of the track.

        This will return the name from the first track_name meta
        event in the track, or '' if there is no such event.

        Setting this property will update the name field of the first
        track_name event in the track. If no such event is found,
        one will be added to the beginning of the track with a delta
        time of 0."""
        for event in self:
            if event.type == 'track_name':
                return event.name
        else:
            return ''

    @name.setter
    def name(self, name):
        # Find the first track_name event and modify it.
        for event in self:
            if event.type == 'track_name':
                event.name = name
                return
        else:
            # No track name found, add one.
            self.insert(0,
                        MetaEvent(delta_time=0, type='track_name', name=name))

    def copy(self):
        return self.__class__(self)

    def __getitem__(self, index_or_slice):
        # Retrieve item from the MidiTrack
        lst = list.__getitem__(self, index_or_slice)
        if isinstance(index_or_slice, int):
            # If an index was provided, return the list element
            return lst
        else:
            # Otherwise, construct a MidiTrack to return.
            # TODO: this make a copy of the list. Is there a better way?
            return self.__class__(lst)

    def __add__(self, other):
        return self.__class__(list.__add__(self, other))

    def __mul__(self, other):
        return self.__class__(list.__mul__(self, other))

    def __repr__(self):
        if len(self) == 0:
            events = ''
        elif len(self) == 1:
            events = f'[{self[0]}]'
        else:
            events = '[\n  {}]'.format(',\n  '.join(repr(m) for m in self))
        return f'{self.__class__.__name__}({events})'


def _to_abstime(events):
    """Convert events to absolute time."""
    now = 0
    for event in events:
        now += event.delta_time
        # FIXME: absolute time should not be in delta_time
        yield event.copy(delta_time=now)


def _to_reltime(events):
    """Convert events to relative time."""
    now = 0
    for event in events:
        delta_time = event.delta_time - now
        yield event.copy(delta_time=delta_time)
        now = event.delta_time


def fix_end_of_track(events):
    """Remove all end_of_track events and add one at the end.

    This is used by merge_tracks() and MidiFile.save()."""
    # Accumulated delta time from removed end of track events.
    # This is added to the next event.
    accum = 0

    for event in events:
        if event.type == 'end_of_track':
            accum += event.delta_time
        else:
            if accum:
                delta_time = accum + event.delta_time
                yield event.copy(delta_time=delta_time)
                accum = 0
            else:
                yield event

    yield MetaEvent(delta_time=accum, type='end_of_track')


def merge_tracks(tracks):
    """Returns a MidiTrack object with all events from all tracks.

    The events are returned in playback order with delta times
    as if they were all in one track.
    """
    events = []
    for track in tracks:
        events.extend(_to_abstime(track))

    events.sort(key=lambda event: event.delta_time)

    return MidiTrack(fix_end_of_track(_to_reltime(events)))
