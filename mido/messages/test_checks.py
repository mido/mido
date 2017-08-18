from pytest import raises
from .checks import check_time, check_data, check_pitch
from ..messages import checks
from ..py2 import PY2


def test_check_time():
    check_time(1)
    check_time(1.5)

    if PY2:
        # long should be allowed. (It doesn't exist in Python3,
        # so there's no need to check for it here.)
        check_time(long('9829389283L'))

    with raises(TypeError):
        check_time(None)

    with raises(TypeError):
        check_time('abc')

    with raises(TypeError):
        check_time(None)

    with raises(TypeError):
        check_time('abc')

def test_check_data():
    check_data(b'\x00\x7f')

    with raises(ValueError):
      check_data(b'\x80')

    with raises(ValueError):
      check_data(b'\xff')

    checks.ALLOW_DATA_LARGE_BYTES = True
    check_data(b'\x80')
    check_data(b'\xff')
    checks.ALLOW_DATA_LARGE_BYTES = False

def test_check_pitchwheel():
    check_pitch(0)
    check_pitch(8191)

    with raises(ValueError):
      check_pitch(8192)

    with raises(ValueError):
      check_pitch(32768)

    checks.ALLOW_LARGE_PITCHWHEEL_RANGE = True
    check_pitch(8192)
    check_pitch(-9000)
    checks.ALLOW_LARGE_PITCHWHEEL_RANGE = False
