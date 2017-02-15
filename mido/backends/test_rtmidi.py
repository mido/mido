from .rtmidi import _expand_alsa_port_name


def test_expand_alsa_port_name():
    port_names = sorted(['A:port 128:0',
                         'B:port 129:0',
                         'B:port 129:0',
                         'Z:port 130:0'])

    def expand(name):
        return _expand_alsa_port_name(port_names, name)

    # Should return first matching port.
    assert expand('port') == 'A:port 128:0'

    assert expand('A:port') == 'A:port 128:0'
    assert expand('B:port') == 'B:port 129:0'

    # Full name should also work.
    assert expand('A:port 128:0') == 'A:port 128:0'

    # If the port is not found the original name should be returned
    # for the caller to deal with.
    assert expand('invalid name') == 'invalid name'
