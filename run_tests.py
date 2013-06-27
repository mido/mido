#!/usr/bin/env python
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
        msg = mido.new('pitchwheel', pitch=mido.messages.MIN_PITCHWHEEL)
        bytes = msg.bytes()
        self.assertTrue(bytes[1] == bytes[2] == 0)

        msg = mido.new('pitchwheel', pitch=mido.messages.MAX_PITCHWHEEL)
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
        ret = mido.parse_all(b'\x20\x30')
        
        self.assertEqual(ret, [])

    def test_parse_stray_status_bytes(self):
        """The parser should ignore stray status bytes."""
        ret = mido.parse_all(b'\x90\x90\xf0')
        
        self.assertEqual(ret, [])

    def test_encode_and_parse(self):
        """Encode a message and then parse it.

        Should return the same message.
        """
        msg1 = mido.new('note_on')
        msg2 = mido.parse(msg1.bytes())
        self.assertEqual(msg1, msg2)

    def test_feed_byte(self):
        """Put various things into feed_byte()."""
        import mido.parser

        parser = mido.parser.Parser()

        parser.feed_byte(0)
        parser.feed_byte(255)

        self.assertRaises(TypeError, parser.feed_byte, [1, 2, 3])
        self.assertRaises(ValueError, parser.feed_byte, -1)
        self.assertRaises(ValueError, parser.feed_byte, 256)    

    # Todo: Parser should not crash when parsing random data
    #def test_parse_random_bytes(self):
    #    pass

if __name__ == '__main__':
    unittest.main()
