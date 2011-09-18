# http://pytest.org/latest/getting-started.html#getstarted
# http://pytest.org/latest/goodpractises.html#test-discovery

# (I installed py.test with 'sudo easy_install -U pytest')

import protomidi

#
# Messages
#

def test_msg_equality():
    """
    Two messages created with same parameters should be equal.
    """
    msg1 = protomidi.msg.note_on(channel=1, note=2, velocity=3)
    msg2 = protomidi.msg.note_on(channel=1, note=2, velocity=3)

    assert msg1 == msg2

def test_msg_inequality():
    """
    Two messages created with different parameters should be inequal.
    """
    msg1 = protomidi.msg.note_on(channel=1, note=2, velocity=3)
    msg2 = protomidi.msg.note_on(channel=1, note=2, velocity=4)

    assert msg1 != msg2

def test_msg_identity():
    """
    Clone with no overrides should return the same object.
    """
    msg1 = protomidi.msg.note_on
    msg2 = msg1()

    assert id(msg1) == id(msg2)

def test_pitchwheel_min():
    """
    Check if pitchwheel with minimal value serializes correctly.
    """
    msg = protomidi.msg.pitchwheel(value=protomidi.msg.pitchwheel_min)
    bytes = protomidi.serialize(msg)

    assert bytes[1] == bytes[2] == 0

def test_pitchwheel_max():
    """
    Check if pitchwheel with maximal value serializes correctly.
    """
    msg = protomidi.msg.pitchwheel(value=protomidi.msg.pitchwheel_max)
    bytes = protomidi.serialize(msg)

    assert bytes[1] == bytes[2] == 127

def test_pitchwheel_serialize_parse():
    """
    Check if pitchwheel with maximal value serializes correctly.
    """
    msg1 = protomidi.msg.pitchwheel(value=0)
    bytes = protomidi.serialize(msg1)
    msg2 = protomidi.parse(bytes)[0]

    assert msg1 == msg2

#
# Serialize and parse
#

def test_parse():
    """
    Parse a note_on msg.
    """
    parsed = protomidi.parse(b'\x90\x4c\x20')[0]
    other = protomidi.msg.note_on(channel=0, note=76, velocity=32)
    assert parsed == other

def test_parse_stray_data():
    """
    Stray data bytes (not inside a message) should be ignored.
    """
    ret = protomidi.parse(b'\x20\x30')

    assert ret == []

def test_parse_stray_opcodes():
    """
    Stray opcodes (opcode followed by too few data bytes)
    should be ignored.
    """
    ret = protomidi.parse(b'\x90\x90\xf0')

    assert ret == []

def test_serialize_and_parse():
    """
    Serialize a message and parse it. Should return the same message.
    """
    msg1 = protomidi.msg.note_on
    msg2 = protomidi.parse(protomidi.serialize(msg1))[0]
    assert msg2 == msg1

def dont_test_parse_random_bytes():
    data = bytearray(b"}kR\x87\xd6\xe0\xb2\x96\xe5\x18}\x1a{[\x0b\x0f\xa7\xc3\x13\r\xbd\xe4\x17\xca\xf3-\x05)\xf8\x1b\x16\x98/\x05\x1e.\xc2\x11;\x04K2cN\x9f-\'\xe2\xe7\xb5\xb6Y\x821\x99\x93\xa7m\xc0[b\xc34\xdbCd\x95\x8fdtOM5\xb5\xdb\xbb\xa6\x0e\xb2\x88\xfd\x15U=\x97\xdd\xd1F\x8b\xb0\x18\xee!}\xf4\x8f+\xde8\xb0")

    protomidi.parse(data)
