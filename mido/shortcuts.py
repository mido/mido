import sys
import functools
import mido.messages

__all__ = []

def _init():
    for spec in mido.messages.get_message_specs():
        this_module = sys.modules[__name__]

        name = spec.type
        if name == 'continue':
            name = 'continue_'

        func = functools.partial(mido.new, spec.type)
        func.__name__ = name
        func.__doc__ = spec.signature()
        setattr(this_module, name, func)
        __all__.append(name)

_init()
