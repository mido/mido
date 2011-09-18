# http://pytest.org/latest/getting-started.html#getstarted
# http://pytest.org/latest/goodpractises.html#test-discovery

# (I installed py.test with 'sudo easy_install -U pytest')

import protomidi

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
