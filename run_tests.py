import unittest
import mido

# http://docs.python.org/2/library/unittest.html

class TestMessages(unittest.TestCase):
    def test_msg_equality(self):
        """
        Two messages created with same parameters should be equal.
        """
        msg1 = mido.new('note_on', channel=1, note=2, velocity=3)
        msg2 = mido.new('note_on', channel=1, note=2, velocity=3)

        self.assertEqual(msg1, msg2)

    def test_pitchwheel_min(self):
        """
        Check if pitchwheel with minimal value encodes correctly.
        """
        msg = mido.new('pitchwheel', value=mido.msg.pitchwheel_min)
        bytes = msg.bytes()

        self.assertTrue(bytes[1] == bytes[2] == 0)

    def test_pitchwheel_max(self):
        """
        Check if pitchwheel with maximal value encodes correctly.
        """
        msg = mido.new('pitchwheel', value=mido.msg.pitchwheel_max)
        bytes = msg.bytes()

        self.assertTrue(bytes[1] == bytes[2] == 127)

    def test_pitchwheel_encode_parse(self):
        """
        Check if pitchwheel with maximal value encodes correctly.
        """
        msg1 = mido.new('pitchwheel', value=0)
        msg2 = mido.parse(msg1.bytes())
        
        self.assertEqual(msg1, msg2)

class TestParser(unittest.TestCase):
    
    def test_parse(self):
        """
        Parse a note_on msg.
        """
        parsed = mido.parse(b'\x90\x4c\x20')
        other = mido.new('note_on', channel=0, note=76, velocity=32)
        self.assertEqual(parsed, other)

    def test_parse_stray_data(self):
        """
        Stray data bytes (not inside a message) should be ignored.
        """
        ret = mido.parseall(b'\x20\x30')
        
        self.assertEqual(ret, [])

    def test_parse_stray_status_bytes(self):
        """
        Stray status bytes (status byte followed by too few data bytes)
        should be ignored.
        """
        ret = mido.parseall(b'\x90\x90\xf0')
        
        self.assertEqual(ret, [])

    def test_encode_and_parse(self):
        """
        Encode a message and parse it. Should return the same message.
        """
        msg1 = mido.new('note_on')
        msg2 = mido.parse(msg1.bytes())
        self.assertEqual(msg1, msg2)

    # Todo: Parser should not crash when parsing random data
    #def test_parse_random_bytes(self):
    #    pass

if __name__ == '__main__':
    unittest.main()
Message('note_on', channel=1, note=2, velocity=3, time=0)
Message('note_on', channel=1, note=2, velocity=3, time=0)
