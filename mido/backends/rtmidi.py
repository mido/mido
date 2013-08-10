# Import one of the rtmidi modules.

try:
    from .python_rtmidi import *
except ImportError:
    from .rtmidi_python import *
