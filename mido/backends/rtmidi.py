# Import one of the rtmidi modules.

try:
    from .python_rtmidi import *
except ImportError:
    try:
        from .rtmidi_python import *
    except ImportError:
        raise ImportError('no module named rtmidi or rtmidi_python')
