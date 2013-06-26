import unittest
import mido

# http://docs.python.org/2/library/unittest.html

class TestMessages(unittest.TestCase):
    def test_msg_equality(self):
        """Two messages created with same parameters should be equal."""
        msg1 = mido.new('note_on', channel=1, note=2, velocity=3)
        msg2 = mido.new('note_on', channel=1, note=2, velocity=3)

        self.assertEqual(msg1, msg2)

    def test_pitchwheel(self):
        """Check if pitchwheel type check and encoding is working."""
        msg = mido.new('pitchwheel', pitch=mido.msg.MIN_PITCHWHEEL)
        bytes = msg.bytes()
        self.assertTrue(bytes[1] == bytes[2] == 0)

        msg = mido.new('pitchwheel', pitch=mido.msg.MAX_PITCHWHEEL)
        bytes = msg.bytes()
        self.assertTrue(bytes[1] == bytes[2] == 127)

    def test_pitchwheel_encode_parse(self):
        """Encode and parse pitchwheel with value=0."""
        msg1 = mido.new('pitchwheel', pitch=0)
        msg2 = mido.parse(msg1.bytes())
        
        self.assertEqual(msg1, msg2)

    def test_channel_value(self):
        """See if the channel masking and overrides work in init."""

        self.assertEqual(mido.new('note_on').channel, 0)
        self.assertEqual(mido.new('note_on', channel=1).channel, 1)

        self.assertEqual(mido.new(0x90).channel, 0)
        self.assertEqual(mido.new(0x91).channel, 1)
        self.assertEqual(mido.new(0x90, channel=1).channel, 1)

class TestParser(unittest.TestCase):
    
    def test_parse(self):
        """Parse a note_on msg and compare it to one created with new()."""
        parsed = mido.parse(b'\x90\x4c\x20')
        other = mido.new('note_on', channel=0, note=76, velocity=32)
        self.assertEqual(parsed, other)

    def test_parse_stray_data(self):
        """The parser should ignore stray data bytes."""
        ret = mido.parseall(b'\x20\x30')
        
        self.assertEqual(ret, [])

    def test_parse_stray_status_bytes(self):
        """The parser should ignore stray status bytes."""
        ret = mido.parseall(b'\x90\x90\xf0')
        
        self.assertEqual(ret, [])

    def test_encode_and_parse(self):
        """Encode a message and then parse it.

        Should return the same message.
        """
        msg1 = mido.new('note_on')
        msg2 = mido.parse(msg1.bytes())
        self.assertEqual(msg1, msg2)

    def test_put_byte(self):
        """Put various things into put_byte()."""
        import mido.parser

        p = mido.parser.Parser()

        p.put_byte(0)
        p.put_byte(255)

        self.assertRaises(TypeError, p.put_byte, [1, 2, 3])
        self.assertRaises(ValueError, p.put_byte, -1)
        self.assertRaises(ValueError, p.put_byte, 256)    

    # Todo: Parser should not crash when parsing random data
    #def test_parse_random_bytes(self):
    #    pass

if __name__ == '__main__':
    unittest.main()
Message('note_on', channel=1, note=2, velocity=3, time=0)
Message('note_on', channel=1, note=2, velocity=3, time=0)
