from .defs import _MSG_DEFS_BY_TYPE, make_msgdict


def msg2str(msgdict, include_time=True):
    type_ = msgdict['type']
    msgdef = _MSG_DEFS_BY_TYPE[type_]

    words = [type_]

    for name in msgdef['value_names']:
        words.append('{}={}'.format(name, msgdict[name]))

    if include_time:
        words.append('time={}'.format(msgdict['time']))
    
    return str.join(' ', words)


def _parse_time(value):
    # Convert to int if possible.
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    raise ValueError('invalid time {!r}'.format(value))


def str2msg(text):
    type_, *args = text.split()

    msgdict = {}

    for arg in args:
        name, value = arg.split('=', 1)
        if name == 'time':
            value = _parse_time(value)
        else:
            value = int(value)

        msgdict[name] = value

    # Todo: hmm, this needs to be rethought.
    # Where should the type and value checking happen?
    return make_msgdict(type_, **msgdict)
