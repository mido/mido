import sys
from pytest import raises
from .messages import Message, parse_time
from .messages import parse_string, format_as_string, parse_string_stream

PY2 = (sys.version_info.major == 2)

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO

def test_parse_string():
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

def test_format_as_string():
    assert (format_as_string(Message('note_on', channel=9))
            == 'note_on channel=9 note=0 velocity=64 time=0')

    assert (format_as_string(Message('sysex', data=(1, 2, 3)))
            == 'sysex data=(1,2,3) time=0')

    assert (format_as_string(Message('sysex', data=()))
            == 'sysex data=() time=0')

    assert (format_as_string(Message('continue'))
            == 'continue time=0')

def test_parse_string_stream():
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

def test_parse_string_time():
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
