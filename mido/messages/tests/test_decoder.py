from ..decode import Decoder


def decode(data):
    """Decode bytes and return an (possibly empty) list of message dicts."""
    d = Decoder()
    d.feed(data)
    return list(d)


def test_note_on():
    note_on = dict(type='note_on', note=1, velocity=2, channel=0, time=0)
    assert decode(b'\x90\x01\x02') == [note_on]


def test_sysex():
    sysex = dict(type='sysex', data=b'\x01\x02\x03', time=0)
    assert decode(b'\xf0\x01\x02\x03\xf7') == [sysex]
