from __future__ import print_function
import sys
import random
from unittest import TestCase, main
from contextlib import contextmanager
import mido
from mido import Message

# http://docs.python.org/2/library/unittest.html

PY2 = (sys.version_info.major == 2)

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO

@contextmanager
def raises(exception):
    try:
        yield
        raise AssertionError('code should have raised exception')
    except exception:
        pass

class TestMessages(TestCase):
    def test_msg_equality(self):
        args = dict(type='note_on', channel=1, note=2, velocity=3)
        assert Message(**args) == Message(**args)

    def test_set_type(self):
        with raises(AttributeError):
            Message('note_on').type = 'note_off'

    def test_pitchwheel(self):
        """Check if pitchwheel type check and encoding is working."""
        msg = Message('pitchwheel', pitch=mido.messages.MIN_PITCHWHEEL)
        bytes = msg.bytes()
        assert bytes[1] == bytes[2]

        msg = Message('pitchwheel', pitch=mido.messages.MAX_PITCHWHEEL)
        bytes = msg.bytes()
        assert bytes[1] == bytes[2] == 127

    def test_pitchwheel_encode_parse(self):
        """Encode and parse pitchwheel with value=0."""
        wheel = Message('pitchwheel', pitch=0)
        assert wheel == mido.parse(wheel.bytes())

    def test_quarter_frame_encode_parse(self):
        """Encode and parse quarter_frame."""
        frame = Message('quarter_frame', frame_type=1, frame_value=2)
        assert frame == mido.parse(frame.bytes())

    def test_sysex(self):
        sysex = Message('sysex', data=(1, 2, 3, 4, 5))
        assert sysex == mido.parse(sysex.bytes())

    def test_check_time(self):
        from mido.messages import check_time

        check_time(1)
        check_time(1.5)

        if PY2:
            # long should be allowed. (It doesn't exist in Python3,
            # so there's no need to check for it here.)
            check_time(long('9829389283L'))

        with raises(TypeError): check_time(None)
        with raises(TypeError): check_time('abc')

        with raises(TypeError): check_time(None)
        with raises(TypeError): check_time('abc')

    def test_check_channel(self):
        from mido.messages import check_channel

        check_channel(0)
        check_channel(15)
        with raises(TypeError): check_channel(None)
        with raises(TypeError): check_channel('abc')
        with raises(TypeError): check_channel(0.5)
        with raises(ValueError): check_channel(-1)
        with raises(ValueError): check_channel(16)

    def test_check_pos(self):
        from mido.messages import check_pos, MIN_SONGPOS, MAX_SONGPOS

        check_pos(0)
        check_pos(MIN_SONGPOS)
        check_pos(MAX_SONGPOS)
        with raises(TypeError): check_pos(None)
        with raises(TypeError): check_pos('abc')
        with raises(ValueError): check_pos(MIN_SONGPOS - 1)
        with raises(ValueError): check_pos(MAX_SONGPOS + 1)

    def test_check_pitch(self):
        from mido.messages import check_pitch, MIN_PITCHWHEEL, MAX_PITCHWHEEL

        # Pitchwheel pitch
        check_pitch(MIN_PITCHWHEEL)
        check_pitch(MAX_PITCHWHEEL)
        with raises(TypeError): check_pitch(None)
        with raises(TypeError): check_pitch(0.5)
        with raises(TypeError): check_pitch('abc')
        with raises(ValueError): check_pitch(MIN_PITCHWHEEL - 1)
        with raises(ValueError): check_pitch(MAX_PITCHWHEEL + 1)

    def test_check_data(self):
        from mido.messages import check_data

        # check_data() should return the data as a tuple.
        assert type(check_data([0, 1, 2]) == tuple)
        assert check_data([0, 1, 2]) == (0, 1, 2)
        assert check_data(i for i in [1, 2, 3]) == (1, 2, 3)

        with raises(TypeError): check_data(1)
        with raises(TypeError): check_data(('a', 'b', 'c'))
        with raises(ValueError): check_data((-1, -2, -3))

    def test_check_frame_type(self):
        from mido.messages import check_frame_type

        # Qarter frame type
        check_frame_type(0)
        check_frame_type(7)
        with raises(TypeError): check_frame_type(None)
        with raises(TypeError): check_frame_type(0.5)
        with raises(ValueError): check_frame_type(-1)
        with raises(ValueError): check_frame_type(8)

    def test_check_databyte(self):
        from mido.messages import check_databyte

        # Data byte
        check_databyte(0)
        check_databyte(15)
        with raises(TypeError): check_databyte(None)
        with raises(TypeError): check_databyte(0.5)
        with raises(ValueError): check_databyte(-1)
        with raises(ValueError): check_databyte(128)

    def test_encode_channel(self):
        from mido.messages import encode_channel

        # Channel should be ignored, and an empty list returned.
        # Thus, there is no reason to check for TypeError
        # and ValueError.
        assert encode_channel(channel=0) == []

    def test_encode_data(self):
        from mido.messages import encode_data

        # Note: encode_data() includes the sysex end byte (0xf7) to avoid a
        # special case in bytes().
        assert encode_data([1, 2, 3]) == [1, 2, 3, 0xf7]

    def test_encode_(self):
        from mido.messages import encode_pitch, MIN_PITCHWHEEL, MAX_PITCHWHEEL

        # Pitchwheel pitch
        assert encode_pitch(MIN_PITCHWHEEL) == [0, 0]
        assert encode_pitch(MAX_PITCHWHEEL) == [127, 127]
        assert encode_pitch(0) == [0, 64]

    def test_encode_pos(self):
        from mido.messages import encode_pos, MIN_SONGPOS, MAX_SONGPOS

        assert encode_pos(MIN_SONGPOS) == [0, 0]
        assert encode_pos(MAX_SONGPOS) == [127, 127]
        # Check endian
        assert [16, 78] == encode_pos(10000)

    def test_get_spec(self):
        from mido.messages import get_spec

        assert get_spec('note_on').type == 'note_on'
        assert get_spec(0x80).type == 'note_off'
        assert get_spec(0x82).type == 'note_off'

        with raises(LookupError): get_spec(-1)
        with raises(LookupError): get_spec(0)
        with raises(LookupError): get_spec('banana')

    def test_sysex_data_type(self):
        """Is messages.data turned into a tuple?"""
        data = range(1)

        message = mido.Message('sysex')
        message.data = data
        assert isinstance(message.data, tuple)

        message = mido.Message('sysex', data=data)
        assert isinstance(message.data, tuple)

        a = mido.Message('sysex', data=(1, 2))
        b = mido.parse(a.bytes())
        assert isinstance(b.data, tuple)

    def test_copy(self):
        orig = Message('note_on', note=22, time=123)
        copy = orig.copy()

        assert orig == copy
        assert orig.time == copy.time
        assert orig.__dict__ == copy.__dict__

        copy = orig.copy(velocity=1)
        orig.velocity = 1

        assert orig == copy

    def test_copy_invalid_attribute(self):
        orig = Message('note_on')
        valid_spec = mido.messages.get_spec('note_on')

        # Pass arguments with invalid names.
        with raises(ValueError): orig.copy(_spec=valid_spec)
        with raises(ValueError): orig.copy(type='continue')
        with raises(ValueError): orig.copy(banana=1)

        # Valid arguments should pass.
        orig.copy(note=0, velocity=0, time=0)

    def test_set_invalid_attribute(self):
        """Set an attribute that is not settable."""
        valid_spec = mido.messages.get_spec('note_on')
        msg = Message('note_on')

        with raises(AttributeError): msg._spec = valid_spec
        with raises(AttributeError): msg.type = 'continue'
        with raises(AttributeError): msg.invalid = 'banana'

class TestStringFormat(TestCase):
    def test_parse_string(self):
        from mido import parse_string

        assert (parse_string('note_on channel=2 note=3')
                == Message('note_on', channel=2, note=3))

        assert (parse_string('sysex data=(1,2,3)')
                == Message('sysex', data=(1, 2, 3)))

        assert (parse_string('note_on time=0.5').time
                == Message('note_on', time=0.5).time)

        # nan and inf should be allowed
        assert parse_string('note_on time=inf').time == float('inf')
        assert str(parse_string('note_on time=nan').time) == 'nan'

        # Commas are not allowed
        with raises(ValueError): parse_string('note_on channel=2, note=3')

        with raises(ValueError): parse_string('++++S+S+SOIO(KOPKEPOKFWKF')
        with raises(ValueError): parse_string('note_on banana=2')
        with raises(ValueError): parse_string('sysex (1, 2, 3)')
        with raises(ValueError): parse_string('sysex (1  2  3)')

    def test_format_as_string(self):
        from mido import format_as_string

        assert (format_as_string(Message('note_on', channel=9))
                == 'note_on channel=9 note=0 velocity=64 time=0')

        assert (format_as_string(Message('sysex', data=(1, 2, 3)))
                == 'sysex data=(1,2,3) time=0')

        assert (format_as_string(Message('sysex', data=()))
                == 'sysex data=() time=0')

        assert (format_as_string(Message('continue'))
                == 'continue time=0')

    def test_parse_string_stream(self):
        from mido import parse_string_stream

        # Correct input.
        stream = StringIO("""
             note_on channel=1  # Ignore this
             # and this
             continue
        """)
        gen = parse_string_stream(stream)
        assert next(gen) == (Message('note_on', channel=1), None)
        assert next(gen) == (Message('continue'), None)

        # Invalid input. It should catch the ValueError
        # from parse_string() and return (None, 'Error message').
        stream = StringIO('ijsoijfdsf\noiajoijfs')
        gen = parse_string_stream(stream)
        assert next(gen)[0] == None
        assert next(gen)[0] == None
        with raises(StopIteration): next(gen)

    def test_parse_string_time(self):
        from mido.messages import parse_time

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
        with raises(ValueError): parse_time('banana')
        with raises(ValueError): parse_time('None')
        with raises(ValueError): parse_time('-')
        with raises(ValueError): parse_time('938938958398593L')

class TestParser(TestCase):
    
    def test_parse(self):
        """Parse a note_on msg and compare it to one created with Message()."""
        parsed = mido.parse(b'\x90\x4c\x20')
        other = Message('note_on', channel=0, note=0x4c, velocity=0x20)
        assert parsed == other

    def test_parse_stray_data(self):
        """The parser should ignore stray data bytes."""
        assert mido.parse_all(b'\x20\x30') == []

    def test_parse_stray_status_bytes(self):
        """The parser should ignore stray status bytes."""
        assert mido.parse_all(b'\x90\x90\xf0') == []

    def test_encode_and_parse(self):
        """Encode a message and then parse it.

        Should return the same message.
        """
        note_on = Message('note_on')
        assert note_on == mido.parse(note_on.bytes())

    def test_encode_and_parse_all(self):
        """Encode and then parse all message types.

        This checks mostly for errors in the parser.
        """
        parser = mido.Parser()
        for spec in mido.messages.get_message_specs():
            msg = Message(spec.type)
            parser.feed(msg.bytes())
            outmsg = parser.get_message()
            assert outmsg is not True
            assert outmsg.type == spec.type

    def test_feed_byte(self):
        """Put various things into feed_byte()."""
        parser = mido.Parser()

        parser.feed_byte(0)
        parser.feed_byte(255)

        with raises(TypeError): parser.feed_byte([1, 2, 3])
        with raises(ValueError): parser.feed_byte(-1)
        with raises(ValueError): parser.feed_byte(256)

    def test_feed(self):
        """Put various things into feed()."""
        parser = mido.Parser()

        parser.feed([])
        parser.feed([1, 2, 3])
        # Todo: add more valid types.

        with raises(TypeError): parser.feed(1)
        with raises(TypeError): parser.feed(None)
        with raises(TypeError): parser.feed()

    # Todo: Parser should not crash when parsing random data
    def not_test_parse_random_bytes(self):
        randrange = random.Random('a_random_seed').randrange
        parser = mido.Parser()
        for _ in range(10000):
            byte = randrange(256)
            parser.feed_byte(byte)

    def test_running_status(self):
        return # Running doesn't work with PortMidi, so it's turned off.

        # Two note_on messages. (The second has no status byte,
        # so the last seen status byte is used instead.)
        assert (mido.parse_all([0x90, 0x01, 0x02, 0x01, 0x02])
                == [Message('note_on', note=1, velocity=2)] * 2)

        # System common messages should cancel running status.
        # (0xf3 is 'songpos'. This should be 'song song=2'
        # followed by a stray data byte.
        assert mido.parse_all([0xf3, 2, 3]) == [Message('song', song=2)]

    def test_parse_channel(self):
        """Parser should not discard the channel in channel messages."""
        assert mido.parse([0x90, 0x00, 0x00]).channel == 0
        assert mido.parse([0x92, 0x00, 0x00]).channel == 2
 
    def test_one_byte_message(self):
        """Messages that are one byte long should not wait for data bytes."""
        messages = mido.parse_all([0xf6])  # Tune request.
        assert len(messages) == 1
        assert messages[0].type == 'tune_request'

    def test_undefined_messages(self):
        """The parser should ignore undefined status bytes and sysex_end."""
        messages = mido.parse_all([0xf4, 0xf5, 0xf7, 0xf9, 0xfd])
        assert messages == []

    def test_realtime_inside_sysex(self):
        """Realtime message inside sysex should be delivered first."""
        messages = mido.parse_all([0xf0, 0, 0xfb, 0, 0xf7])
        assert len(messages) == 2
        assert messages[0].type == 'continue'
        assert messages[1].type == 'sysex'

    def test_undefined_realtime_inside_sysex(self):
        """Undefined realtime message inside sysex should ignored."""
        messages = mido.parse_all([0xf0, 0, 0xf9, 0xfd, 0, 0xf7])
        assert len(messages) == 1
        assert messages[0].type == 'sysex'

class TestSockets(TestCase):
    
    def test_parse_address(self):
        from mido.sockets import parse_address

        assert parse_address(':8080') == ('', 8080)
        

        assert parse_address('localhost:8080') == ('localhost', 8080)
        with raises(ValueError): parse_address(':to_many_colons:8080')
        with raises(ValueError): parse_address('only_hostname')
        with raises(ValueError): parse_address('')
        with raises(ValueError): parse_address(':')
        with raises(ValueError): parse_address(':shoe')
        with raises(ValueError): parse_address(':0')
        with raises(ValueError): parse_address(':65536')  # Out of range.

class TestMidiFiles(TestCase):
    def test_meta_specs(self):
        """Test that meta specs are implemented correctly."""
        from mido.midifiles_meta import MetaMessage, _specs

        for key in _specs:
            # Specs are indexed by name and type byte.
            # Make sure we don't check them twice.
            if isinstance(key, int):
                spec = _specs[key]
                m = MetaMessage(spec.type)
                encoded1 = m.bytes()[3:]  # [3:] skips 0xff, type and length.
                decoded = spec.decode(m, encoded1)
                encoded2 = spec.encode(m)

                assert encoded1 == encoded2
                assert len(spec.attributes) == len(spec.defaults)

    def test_meta_copy(self):
        # Todo: this could probably be combined with the test_copy().
        from mido.midifiles import MetaMessage

        orig = MetaMessage('key_signature', key='Bb')
        copy = orig.copy()

        assert orig == copy
        assert orig.time == copy.time

        copy = orig.copy(key='F#m')
        orig.key = 'F#m'

        assert orig == copy
        assert orig.__dict__ == copy.__dict__

class TestPorts(TestCase):
    def test_base_ioport(self):
        from mido.ports import BaseIOPort

        class Port(BaseIOPort):
            def _open(self):
                self.test_value = True

            def _send(self, message):
               self._messages.append(message)

            def _close(self):
                self.test_value = False

        with Port('Name') as port:
            assert port.name == 'Name'
            assert not port.closed

            assert port._messages is port._parser._parsed_messages

            with raises(TypeError): port.send('not a message')

            # Send message.
            message = Message('note_on')
            port.send(message)

            # Receive a message. (Blocking.)
            assert isinstance(port.receive(), Message)

            # Receive a message. (Non-blocking.)
            port.send(message)
            assert isinstance(port.receive(block=False), Message)
            assert port.receive(block=False) is None

            port.send(message)
            port.send(message)
            assert port.pending() == 2
            assert list(port.iter_pending()) == [message, message]

            # Todo: should this type of port close (and/or stop iteration)
            # when there are no messages?
            # port.send(message)
            # port.send(message)
            # assert port.pending() == 2
            # assert list(port) == [message, message]

        assert port.closed

    def test_non_finite_port(self):
        # This type of port can close when it runs out of messages.
        # (And example of this is socket ports.)
        #
        # Iteration should then stop after all messages in the
        # internal queue have been received.
        from mido.ports import BaseIOPort

        message = Message('note_on')

        class Port(BaseIOPort):
            def _open(self):
                # Simulate some messages that arrived
                # earlier.
                self._messages.extend([message, message])

            def _receive(self, block=True):
                # Oops, the other end hung up.
                self.close()

        with Port() as port:
            assert len(list(port)) == 2

if __name__ == '__main__':
    main()
