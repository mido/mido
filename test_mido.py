from __future__ import print_function
import sys
import random
import unittest
import mido
from mido import Message

# http://docs.python.org/2/library/unittest.html

PY2 = (sys.version_info.major == 2)

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO

class TestMessages(unittest.TestCase):
    def test_msg_equality(self):
        """Two messages created with same parameters should be equal."""
        msg1 = Message('note_on', channel=1, note=2, velocity=3)
        msg2 = Message('note_on', channel=1, note=2, velocity=3)

        self.assertTrue(msg1 == msg2)

    def test_set_type(self):
        a = Message('note_on')
        self.assertRaises(AttributeError, setattr, a, 'type', 'sysex')

    def test_pitchwheel(self):
        """Check if pitchwheel type check and encoding is working."""
        msg = Message('pitchwheel', pitch=mido.messages.MIN_PITCHWHEEL)
        bytes = msg.bytes()
        self.assertTrue(bytes[1] == bytes[2] == 0)

        msg = Message('pitchwheel', pitch=mido.messages.MAX_PITCHWHEEL)
        bytes = msg.bytes()
        self.assertTrue(bytes[1] == bytes[2] == 127)

    def test_pitchwheel_encode_parse(self):
        """Encode and parse pitchwheel with value=0."""
        a = Message('pitchwheel', pitch=0)
        b = mido.parse(a.bytes())

        self.assertTrue(a == b)

    def test_quarter_frame_encode_parse(self):
        """Encode and parse quarter_frame."""
        a = Message('quarter_frame', frame_type=1, frame_value=2)
        b = mido.parse(a.bytes())
        
        self.assertTrue(a == b)

    def test_sysex(self):
        original = Message('sysex', data=(1, 2, 3, 4, 5))
        parsed = mido.parse(original.bytes())
        self.assertTrue(original == parsed)

    def test_check_functions(self):
        """Test the check_*() functions."""
        m = mido.messages

        # 'time' field only allows int and float.
        m.check_time(1)
        m.check_time(1.5)
        if PY2:
            m.check_time(long('9829389283L'))
        self.assertRaises(TypeError, m.check_time, None)
        self.assertRaises(TypeError, m.check_time, 'abc')

        # Channel
        m.check_channel(0)
        m.check_channel(15)
        self.assertRaises(TypeError, m.check_channel, None)
        self.assertRaises(TypeError, m.check_channel, 'abc')
        self.assertRaises(TypeError, m.check_channel, 0.5)
        self.assertRaises(ValueError, m.check_channel, -1)
        self.assertRaises(ValueError, m.check_channel, 16)

        # Song position
        m.check_pos(m.MIN_SONGPOS)
        m.check_pos(m.MAX_SONGPOS)
        self.assertRaises(TypeError, m.check_pos, None)
        self.assertRaises(TypeError, m.check_pos, 'abc')
        self.assertRaises(ValueError, m.check_pos, m.MIN_SONGPOS - 1)
        self.assertRaises(ValueError, m.check_pos, m.MAX_SONGPOS + 1)

        # Pitchwheel pitch
        m.check_pitch(m.MIN_PITCHWHEEL)
        m.check_pitch(m.MAX_PITCHWHEEL)
        self.assertRaises(TypeError, m.check_pitch, None)
        self.assertRaises(TypeError, m.check_pitch, 0.5)
        self.assertRaises(TypeError, m.check_pitch, 'abc')
        self.assertRaises(ValueError, m.check_pitch, m.MIN_PITCHWHEEL - 1)
        self.assertRaises(ValueError, m.check_pitch, m.MAX_PITCHWHEEL + 1)

        # Data (sysex)
        self.assertEqual((0, 1, 2), m.check_data([0, 1, 2]))
        self.assertEqual((0, 1, 2), m.check_data((i for i in range(3))))
        self.assertRaises(TypeError, m.check_data, 1)
        self.assertRaises(TypeError, m.check_data, ('a', 'b', 'c'))
        self.assertRaises(ValueError, m.check_data, (-1, -2, -3))

        # Qarter frame type
        m.check_frame_type(0)
        m.check_frame_type(7)
        self.assertRaises(TypeError, m.check_frame_type, None)
        self.assertRaises(TypeError, m.check_frame_type, 0.5)
        self.assertRaises(ValueError, m.check_frame_type, -1)
        self.assertRaises(ValueError, m.check_frame_type, 8)

        # Qarter frame value
        m.check_frame_type(0)
        m.check_frame_type(7)
        self.assertRaises(TypeError, m.check_frame_type, None)
        self.assertRaises(TypeError, m.check_frame_type, 0.5)
        self.assertRaises(ValueError, m.check_frame_type, -1)
        self.assertRaises(ValueError, m.check_frame_type, 16)

        # Data byte
        m.check_databyte(0)
        m.check_databyte(15)
        self.assertRaises(TypeError, m.check_databyte, None)
        self.assertRaises(TypeError, m.check_databyte, 0.5)
        self.assertRaises(ValueError, m.check_databyte, -1)
        self.assertRaises(ValueError, m.check_databyte, 128)

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
        # Note: encode_data() includes the sysex end byte (0xf7) to avoid a
        # special case in bytes().
        self.assertEqual([1, 2, 3, 0xf7], m.encode_data((1, 2, 3)))

        # Pitchwheel pitch
        self.assertEqual([0, 0], m.encode_pitch(m.MIN_PITCHWHEEL))
        self.assertEqual([127, 127], m.encode_pitch(m.MAX_PITCHWHEEL))
        self.assertEqual([0, 64], m.encode_pitch(0))

        # Song position
        self.assertEqual([0, 0], m.encode_pos(0))
        self.assertEqual([127, 127], m.encode_pos(m.MAX_SONGPOS))
        # Check endian
        self.assertEqual([16, 78], m.encode_pos(10000))

    def test_get_spec(self):
        get_spec = mido.messages.get_spec

        self.assertTrue(get_spec('note_on').type == 'note_on')
        self.assertTrue(get_spec(0x80).type == 'note_off')
        self.assertTrue(get_spec(0x82).type == 'note_off')

        self.assertRaises(LookupError, get_spec, 0)

    def test_sysex_data_type(self):
        """Is messages.data turned into a tuple?"""
        data = range(1)

        message = mido.Message('sysex')
        message.data = data
        self.assertTrue(isinstance(message.data, tuple))

        message = mido.Message('sysex', data=data)
        self.assertTrue(isinstance(message.data, tuple))

        a = mido.Message('sysex', data=(1, 2))
        b = mido.parse(a.bytes())
        self.assertTrue(isinstance(b.data, tuple))


class TestStringFormat(unittest.TestCase):
    def test_parse_string(self):
        m = mido.messages

        self.assertEqual(m.parse_string('note_on channel=2 note=3'),
                         Message('note_on', channel=2, note=3))

        self.assertEqual(m.parse_string('sysex data=(1,2,3)'),
                         Message('sysex', data=(1, 2, 3)))

        a = m.parse_string('note_on channel=2 note=3 time=0.5')
        b = Message('sysex', data=(1, 2, 3), time=0.5)
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
        f = mido.messages.format_as_string

        msg = Message('note_on', channel=9)
        self.assertEqual(f(msg), 'note_on channel=9 note=0 velocity=0 time=0')

        msg = Message('sysex', data=(1, 2, 3))
        self.assertEqual(f(msg), 'sysex data=(1,2,3) time=0')

        msg = Message('sysex', data=())
        self.assertEqual(f(msg), 'sysex data=() time=0')

        msg = Message('continue')
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
        self.assertEqual(next(gen), (Message('note_on', channel=1), None))
        self.assertEqual(next(gen), (Message('continue'), None))

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
        """Parse a note_on msg and compare it to one created with Message()."""
        parsed = mido.parse(b'\x90\x4c\x20')
        other = Message('note_on', channel=0, note=0x4c, velocity=0x20)
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
        msg1 = Message('note_on')
        msg2 = mido.parse(msg1.bytes())
        self.assertTrue(msg1 == msg2)

    def test_encode_and_parse_all(self):
        """Encode and then parse all message types.

        This checks mostly for errors in the parser.
        """
        p = mido.Parser()
        for spec in mido.messages.get_message_specs():
            msg = Message(spec.type)
            p.feed(msg.bytes())
            outmsg = p.get_message()
            self.assertTrue(outmsg is not True)
            self.assertTrue(outmsg.type == spec.type)


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
    def not_test_parse_random_bytes(self):
        r = random.Random('a_random_seed')
        parser = mido.Parser()
        for _ in range(10000):
            byte = r.randrange(256)
            parser.feed_byte(byte)

    def test_running_status(self):
        return # Running doesn't work with PortMidi, so it's turned off.

        # Two note_on messages. (The second has no status byte,
        # so the last seen status byte is used instead.)
        a = mido.parse_all([0x90, 0x01, 0x02, 0x01, 0x02])
        b = [Message('note_on', note=1, velocity=2)] * 2
        self.assertEqual(a, b)

        # System common messages should cancel running status.
        # (0xf3 is 'songpos'. This should be 'song song=2'
        # followed by a stray data byte.
        a = mido.parse_all([0xf3, 2, 3])
        b = [Message('song', song=2)]
        self.assertEqual(a, b)

    def test_parse_channel(self):
        """Parser should not discard the channel in channel messages."""
        self.assertTrue(mido.parse([0x90, 0x00, 0x00]).channel == 0)
        self.assertTrue(mido.parse([0x92, 0x00, 0x00]).channel == 2)
           
    def test_one_byte_message(self):
        """Messages that are one byte long should not wait for data bytes."""
        messages = mido.parse_all([0xf6])  # Tune request.
        self.assertTrue(len(messages) == 1)
        self.assertTrue(messages[0].type == 'tune_request')

    def test_undefined_messages(self):
        """The parser should ignore undefined status bytes and sysex_end."""
        messages = mido.parse_all([0xf4, 0xf5, 0xf7, 0xf9, 0xfd])
        self.assertTrue(messages == [])


class TestSockets(unittest.TestCase):
    
    def test_parse_address(self):
        from mido.sockets import parse_address

        self.assertTrue(('', 8080) == parse_address(':8080'))
        self.assertTrue(('localhost', 8080) == parse_address('localhost:8080'))
        self.assertRaises(ValueError, parse_address, ':to_many_colons:8080')
        self.assertRaises(ValueError, parse_address, 'only_hostname')
        self.assertRaises(ValueError, parse_address, '')
        self.assertRaises(ValueError, parse_address, ':')
        self.assertRaises(ValueError, parse_address, ':shoe')
        self.assertRaises(ValueError, parse_address, ':0')
        self.assertRaises(ValueError, parse_address, ':65536')  # Out of range.

class TestMidiFiles(unittest.TestCase):
    def test_encode_decode_signed_byte(self):
        from mido.midifiles_meta import encode_signed_byte, decode_signed_byte

        for i in range(0, 256):
            self.assertEqual(i, encode_signed_byte(decode_signed_byte(i)))

    def test_encode_signed_byte(self):
        from mido.midifiles_meta import encode_signed_byte as encode

        self.assertEqual(encode(0), 0)
        self.assertEqual(encode(-1), 255)

        self.assertRaises(ValueError, encode, 'not an integer')
        self.assertRaises(ValueError, encode, None)
        # Out of range
        self.assertRaises(ValueError, encode, -129)
        self.assertRaises(ValueError, encode, 128)

    def test_decode_signed_byte(self):
        from mido.midifiles_meta import decode_signed_byte as decode

        self.assertEqual(decode(0), 0)
        self.assertEqual(decode(255), -1)

        self.assertRaises(ValueError, decode, 'not an integer')
        self.assertRaises(ValueError, decode, None)
        # Out of range
        self.assertRaises(ValueError, decode, -1)
        self.assertRaises(ValueError, decode, 256)

if __name__ == '__main__':
    unittest.main()
