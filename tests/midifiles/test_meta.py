# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import pytest

from mido.midifiles.meta import (
    KeySignatureError,
    MetaMessage,
    MetaSpec_key_signature,
    UnknownMetaMessage,
)


def test_copy_invalid_argument():
    with pytest.raises(ValueError):
        MetaMessage('track_name').copy(a=1)


def test_copy_cant_override_type():
    with pytest.raises(ValueError):
        MetaMessage('track_name').copy(type='end_of_track')


class TestKeySignature:
    @pytest.mark.parametrize('bad_key_sig', [[8, 0], [8, 1], [0, 2],
                                             [9, 1], [255 - 7, 0]])
    def test_bad_key_sig_throws_key_signature_error(self, bad_key_sig):
        with pytest.raises(KeySignatureError):
            MetaSpec_key_signature().decode(MetaMessage('key_signature'),
                                            bad_key_sig)

    @pytest.mark.parametrize('input_bytes,expect_sig', [([0, 0], 'C'),
                                                        ([0, 1], 'Am'),
                                                        ([255 - 6, 0], 'Cb'),
                                                        ([255 - 6, 1], 'Abm'),
                                                        ([7, 1], 'A#m')
                                                        ])
    def test_key_signature(self, input_bytes, expect_sig):
        msg = MetaMessage('key_signature')
        MetaSpec_key_signature().decode(msg, input_bytes)
        assert msg.key == expect_sig


def test_meta_message_repr():
    msg = MetaMessage('end_of_track', time=10)
    msg_eval = eval(repr(msg))  # noqa: S307
    assert msg == msg_eval


def test_unknown_meta_message_repr():
    msg = UnknownMetaMessage(type_byte=99, data=[1, 2], time=10)
    msg_eval = eval(repr(msg))  # noqa: S307
    assert msg == msg_eval


def test_meta_from_bytes_invalid():
    test_bytes = [
        0xC0,  # Not a meta event (Program Change channel 1)
        0x05   # Program #5
    ]
    with pytest.raises(ValueError):
        MetaMessage.from_bytes(test_bytes)


def test_meta_from_bytes_data_too_short():
    test_bytes = [
        0xFF,  # Meta event
        0x01,  # Event Type: Text
        0x04,  # Length
        ord('T'), ord('E'), ord('S'),  # Text: TES
    ]
    with pytest.raises(ValueError):
        MetaMessage.from_bytes(test_bytes)


def test_meta_from_bytes_data_too_long():
    test_bytes = [
        0xFF,  # Meta event
        0x01,  # Event Type: Text
        0x04,  # Length
        ord('T'), ord('E'), ord('S'), ord('T'), ord('S')  # Text: TESTS
    ]
    with pytest.raises(ValueError):
        MetaMessage.from_bytes(test_bytes)


def test_meta_from_bytes_text():
    test_bytes = [
        0xFF,  # Meta event
        0x01,  # Event Type: Text
        0x04,  # Length
        ord('T'), ord('E'), ord('S'), ord('T')  # Text: TEST
    ]
    msg = MetaMessage.from_bytes(test_bytes)
    assert msg.type == 'text'
    assert msg.text == 'TEST'


# Meta events in real files are sometimes shorter than the spec requires.
# Decoding used to index into the payload unconditionally and raise
# IndexError, so files that other players open fine could not be loaded at
# all. The documented defaults are used instead. (See issue #358.)
#
# (type_byte, payload, expected attributes)
TRUNCATED_PAYLOADS = [
    (0x00, [], {'number': 0}),                      # sequence_number
    (0x00, [1], {'number': 0}),                     # sequence_number, half
    (0x20, [], {'channel': 0}),                     # channel_prefix
    (0x51, [], {'tempo': 500000}),                  # set_tempo
    (0x51, [7, 161], {'tempo': 500000}),            # set_tempo, 2 of 3
    (0x54, [], {'frame_rate': 24, 'hours': 0,       # smpte_offset
                'minutes': 0, 'seconds': 0, 'frames': 0, 'sub_frames': 0}),
    (0x54, [0, 1, 2], {'frame_rate': 24, 'hours': 0,  # smpte_offset, 3 of 5
                       'minutes': 0, 'seconds': 0, 'frames': 0, 'sub_frames': 0}),
    (0x58, [], {'numerator': 4, 'denominator': 4,   # time_signature
                'clocks_per_click': 24,
                'notated_32nd_notes_per_beat': 8}),
    (0x58, [6, 3], {'numerator': 4, 'denominator': 4,  # time_signature, 2 of 4
                    'clocks_per_click': 24,
                    'notated_32nd_notes_per_beat': 8}),
    (0x59, [], {'key': 'C'}),                       # key_signature
    (0x59, [0], {'key': 'C'}),                      # key_signature, 1 of 2
]


@pytest.mark.parametrize('type_byte,payload,expected', TRUNCATED_PAYLOADS)
def test_truncated_payload_uses_defaults(type_byte, payload, expected):
    msg = MetaMessage.from_bytes([0xFF, type_byte, len(payload), *payload])
    for name, value in expected.items():
        assert getattr(msg, name) == value


@pytest.mark.parametrize('type_byte,payload,expected', TRUNCATED_PAYLOADS)
def test_truncated_payload_round_trips(type_byte, payload, expected):
    msg = MetaMessage.from_bytes([0xFF, type_byte, len(payload), *payload])
    assert MetaMessage.from_bytes(msg.bytes()) == msg


def test_complete_payloads_are_still_decoded():
    # The guard must not shadow data the file did supply.
    assert MetaMessage.from_bytes([0xFF, 0x59, 2, 0, 1]).key == 'Am'
    signature = MetaMessage.from_bytes([0xFF, 0x58, 4, 6, 3, 24, 8])
    assert (signature.numerator, signature.denominator,
            signature.clocks_per_click,
            signature.notated_32nd_notes_per_beat) == (6, 8, 24, 8)
    assert MetaMessage.from_bytes([0xFF, 0x51, 3, 0x07, 0xA1, 0x20]).tempo == 500000
    assert MetaMessage.from_bytes([0xFF, 0x00, 2, 0x12, 0x34]).number == 0x1234
