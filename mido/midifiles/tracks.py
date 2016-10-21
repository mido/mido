class MidiTrack(list):
    @property
    def name(self):
        """Name of the track.

        This will return the name from the first track_name meta
        message in the track, or '' if there is no such message.

        Setting this property will update the name field of the first
        track_name message in the track. If no such message is found,
        one will be added to the beginning of the track with a delta
        time of 0."""
        for message in self:
            if message.type == 'track_name':
                return message.name
        else:
            return u''

    @name.setter
    def name(self, name):
        # Find the first track_name message and modify it.
        for message in self:
            if message.type == 'track_name':
                message.name = name
                return
        else:
            # No track name found, add one.
            self.insert(0, MetaMessage('track_name', name=name, time=0))

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
            # Todo: this make a copy of the list. Is there a better way?
            return self.__class__(lst)

    def __add__(self, other):
        return self.__class__(list.__add__(self, other))

    def __mul__(self, other):
        return self.__class__(list.__mul__(self, other))

    def __repr__(self):
        return '<midi track {!r} {} messages>'.format(self.name, len(self))


def merge_tracks(tracks):
    """Returns a MidiTrack object with all messages from all tracks.

    The messages are returned in playback order with delta times
    as if they were all in one track.
    """
    max_time = 0
    messages = MidiTrack()
    for track in tracks:
        now = 0
        for message in track:
            now += message.time
            if message.type not in ('track_name', 'end_of_track'):
                messages.append(message.copy(time=now))
            if message.type == 'end_of_track':
                break
        max_time = max(max_time, now)

    messages.sort(key=lambda x: x.time)
    messages.append(MetaMessage('end_of_track', time=max_time))

    # Convert absolute time back to delta time.
    last_time = 0
    for message in messages:
        message.time -= last_time
        last_time += message.time

    return messages
