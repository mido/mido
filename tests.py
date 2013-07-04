from __future__ import print_function
import sys
import random
import unittest
import mido

# http://docs.python.org/2/library/unittest.html

python2 = (sys.version_info.major == 2)

if python2:
    from StringIO import StringIO
else:
    from io import StringIO

class TestMessages(unittest.TestCase):
    def test_msg_equality(self):
        """Two messages created with same parameters should be equal."""
        msg1 = mido.new('note_on', channel=1, note=2, velocity=3)
        msg2 = mido.new('note_on', channel=1, note=2, velocity=3)

        self.assertTrue(msg1 == msg2)

    def test_set_type(self):
        a = mido.new('note_on')
        self.assertRaises(AttributeError, setattr, a, 'type', 'sysex')

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
        a = mido.new('pitchwheel', pitch=0)
        b = mido.parse(a.bytes())

        self.assertTrue(a == b)

    def test_channel_value(self):
        """See if the channel masking and overrides work in init."""

        self.assertTrue(mido.new('note_on').channel == 0)
        self.assertTrue(mido.new('note_on', channel=1).channel == 1)

        self.assertTrue(mido.new(0x90).channel == 0)
        self.assertTrue(mido.new(0x91).channel == 1)
        self.assertTrue(mido.new(0x90, channel=1).channel == 1)

    def test_sysex(self):
        original = mido.new('sysex', data=(1, 2, 3, 4, 5))
        parsed = mido.parse(original.bytes())
        self.assertTrue(original == parsed)

    def test_check_functions(self):
        """Test the check_*() functions."""
        m = mido.messages

        # 'time' field only allows int and float.
        m.check_time(1)
        m.check_time(1.5)
        if python2:
            m.check_time(long('9829389283L'))
        self.assertRaises(TypeError, m.check_time, None)
        self.assertRaises(TypeError, m.check_time, 'abc')

        # Channel
        self.assertRaises(TypeError, m.check_channel, None)
        self.assertRaises(TypeError, m.check_channel, 'abc')
        self.assertRaises(TypeError, m.check_channel, 0.5)
        self.assertRaises(ValueError, m.check_channel, -1)
        self.assertRaises(ValueError, m.check_channel, 16)
        m.check_channel(0)
        m.check_channel(15)

        # Song position
        self.assertRaises(TypeError, m.check_pos, None)
        self.assertRaises(TypeError, m.check_pos, 'abc')
        self.assertRaises(ValueError, m.check_pos, m.MIN_SONGPOS - 1)
        self.assertRaises(ValueError, m.check_pos, m.MAX_SONGPOS + 1)
        m.check_pos(m.MIN_SONGPOS)
        m.check_pos(m.MAX_SONGPOS)

        # Pitchwheel pitch
        self.assertRaises(TypeError, m.check_pitch, None)
        self.assertRaises(TypeError, m.check_pitch, 0.5)
        self.assertRaises(TypeError, m.check_pitch, 'abc')
        self.assertRaises(ValueError, m.check_pitch, m.MIN_PITCHWHEEL - 1)
        self.assertRaises(ValueError, m.check_pitch, m.MAX_PITCHWHEEL + 1)
        m.check_pitch(m.MIN_PITCHWHEEL)
        m.check_pitch(m.MAX_PITCHWHEEL)

        # Data byte
        self.assertRaises(TypeError, m.check_databyte, None)
        self.assertRaises(TypeError, m.check_databyte, 0.5)
        self.assertRaises(ValueError, m.check_databyte, -1)
        self.assertRaises(ValueError, m.check_databyte, 128)
        m.check_databyte(0)
        m.check_databyte(127)

        # Data (sysex)
        self.assertEqual((0, 1, 2), m.check_data([0, 1, 2]))
        self.assertEqual((0, 1, 2), m.check_data((i for i in range(3))))
        self.assertRaises(TypeError, m.check_data, 1)
        self.assertRaises(TypeError, m.check_data, ('a', 'b', 'c'))
        self.assertRaises(ValueError, m.check_data, (-1, -2, -3))

    def test_encode_functions(self):
        """Test the encode_*() functions."""
        m = mido.messages

        # These have no type and value checks, since the data
        # is assumed to be correct already. (It was checked on
        # the way into the object.)

        # Channel should be ignored, and an empty list returned.
        # Thus, there is no reason to check for TypeError
        # and ValueError.
        self.assertEqual(m.encode_channel(channel=0), [])

        # Encode data
        sysex_end_byte = 0xf7
        self.assertEqual([1, 2, 3, sysex_end_byte], m.encode_data((1, 2, 3)))

        # Pitchwheel pitch
        self.assertEqual([0, 0], m.encode_pitch(m.MIN_PITCHWHEEL))
        self.assertEqual([127, 127], m.encode_pitch(m.MAX_PITCHWHEEL))
        self.assertEqual([0, 64], m.encode_pitch(0))

        # Song position
        self.assertEqual([0, 0], m.encode_pos(0))
        self.assertEqual([127, 127], m.encode_pos(m.MAX_SONGPOS))
        # Check endian
        self.assertEqual([16, 78], m.encode_pos(10000))


class TestStringFormat(unittest.TestCase):
    def test_parse_string(self):
        m = mido.messages

        self.assertEqual(m.parse_string('note_on channel=2 note=3'),
                         mido.new('note_on', channel=2, note=3))

        self.assertEqual(m.parse_string('sysex data=(1,2,3)'),
                         mido.new('sysex', data=(1, 2, 3)))

        a = m.parse_string('note_on channel=2 note=3 time=0.5')
        b = mido.new('sysex', data=(1, 2, 3), time=0.5)
        self.assertEqual(a.time, b.time)

        # nan and inf should be allowed
        a = m.parse_string('note_on time=inf')
        b = m.parse_string('note_on time=nan')
        self.assertTrue(a.time == float('inf'))
        self.assertTrue(str(b.time) == 'nan')

        # Should raise ValueError if something is wrong with the string.
        # Extra comma after 'channel=2':
        self.assertRaises(ValueError,
                          m.parse_string, 'note_on channel=2, note=3')      
        self.assertRaises(ValueError,
                          m.parse_string, 'note_on channel=2, note=3')
        self.assertRaises(ValueError,
                          m.parse_string, '++++S+S+SOIO(KOPKEPOKFWKF')
        self.assertRaises(ValueError,
                          m.parse_string, 'note_on banana=2')
        self.assertRaises(ValueError,
                          m.parse_string, 'sysex (1, 2, 3)')
        self.assertRaises(ValueError,
                          m.parse_string, 'sysex (1  2  3)')

    def test_format_as_string(self):
        f = mido.messages._format_as_string

        msg = mido.new('note_on', channel=9)
        self.assertEqual(f(msg), 'note_on channel=9 note=0 velocity=0 time=0')

        msg = mido.new('sysex', data=(1, 2, 3))
        self.assertEqual(f(msg), 'sysex data=(1,2,3) time=0')

        msg = mido.new('sysex', data=())
        self.assertEqual(f(msg), 'sysex data=() time=0')

        msg = mido.new('continue')
        self.assertEqual(f(msg), 'continue time=0')

    def test_parse_string_stream(self):
        m = mido.messages

        # Correct input.
        stream = StringIO("""
             note_on channel=1  # Ignore this
             # and this
             continue
        """)
        gen = m.parse_string_stream(stream)
        self.assertEqual(next(gen), (mido.new('note_on', channel=1), None))
        self.assertEqual(next(gen), (mido.new('continue'), None))

        # Invalid input. It should catch the ValueError
        # from parse_string() and return (None, 'Error message').
        stream = StringIO('ijsoijfdsf\noiajoijfs')
        gen = m.parse_string_stream(stream)
        self.assertEqual(next(gen)[0], None)
        self.assertEqual(next(gen)[0], None)
        self.assertRaises(StopIteration, next, gen)

    def test_parse_string_time(self):
        parse_time = mido.messages.parse_time

        # These should work:
        parse_time('0')
        parse_time('12')
        parse_time('-9')
        parse_time('0.5')
        parse_time('10e10')
        parse_time('inf')
        parse_time('-inf')
        parse_time('nan')
        parse_time('2389284878375')  # Will be a long in Python 2

        # These should not
        self.assertRaises(ValueError, parse_time, 'banana')
        self.assertRaises(ValueError, parse_time, 'None')
        self.assertRaises(ValueError, parse_time, '-')
        self.assertRaises(ValueError, parse_time, '938938958398593L')

class TestParser(unittest.TestCase):
    
    def test_parse(self):
        """Parse a note_on msg and compare it to one created with new()."""
        parsed = mido.parse(b'\x90\x4c\x20')
        other = mido.new('note_on', channel=0, note=76, velocity=32)
        self.assertTrue(parsed == other)

    def test_parse_stray_data(self):
        """The parser should ignore stray data bytes."""
        ret = mido.parse_all(b'\x20\x30')
        
        self.assertTrue(ret == [])

    def test_parse_stray_status_bytes(self):
        """The parser should ignore stray status bytes."""
        ret = mido.parse_all(b'\x90\x90\xf0')
        
        self.assertTrue(ret == [])

    def test_encode_and_parse(self):
        """Encode a message and then parse it.

        Should return the same message.
        """
        msg1 = mido.new('note_on')
        msg2 = mido.parse(msg1.bytes())
        self.assertTrue(msg1 == msg2)

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
    def test_parse_random_bytes(self):
        parser = mido.Parser()
        for _ in range(10000):
            byte = random.randrange(256)
            parser.feed_byte(byte)

    def test_running_status(self):
        # Two note_on messages. (The second has no status byte,
        # so the last seen status byte is used instead.)
        a = mido.parse_all([0x90, 0x01, 0x02, 0x01, 0x02])
        b = [mido.new('note_on', note=1, velocity=2)] * 2
        self.assertEqual(a, b)

        # System common messages should cancel running status.
        # (0xf3 is 'songpos'. This should be 'song song=2'
        # followed by a stray data byte.
        a = mido.parse_all([0xf3, 2, 3])
        b = [mido.new('song', song=2)]
        self.assertEqual(a, b)
            
if __name__ == '__main__':
    unittest.main()
