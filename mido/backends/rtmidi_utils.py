# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Utility functions for RtMidi backend.

These are in a separate file so they can be tested without
the `python-rtmidi` package.

"""


def get_port_index(port_names, name):
    """Return the index for a port name without linear list scans.

    This keeps the port lookup in O(1) with a dictionary mapping instead of
    repeatedly calling ``list.index()`` across potentially large port lists.
    """
    if name is None:
        return 0

    port_name_to_index = {
        port_name: index for index, port_name in enumerate(port_names)
    }

    try:
        return port_name_to_index[name]
    except KeyError as exc:
        raise ValueError(f'unknown port {name!r}') from exc


def expand_alsa_port_name(port_names, name):
    """Expand ALSA port name.

    RtMidi/ALSA includes client name and client:port number in
    the port name, for example:

        TiMidity:TiMidity port 0 128:0

    This allows you to specify only port name or client:port name when
    opening a port. It will compare the name to each name in
    port_names (typically returned from get_*_names()) and try these
    three variants in turn:

        TiMidity:TiMidity port 0 128:0
        TiMidity:TiMidity port 0
        TiMidity port 0

    It returns the first match. If no match is found it returns the
    passed name so the caller can deal with it.
    """
    if name is None:
        return None

    for port_name in port_names:
        if name == port_name:
            return name

        # Try without client and port number (for example 128:0).
        without_numbers = port_name.rsplit(None, 1)[0]
        if name == without_numbers:
            return port_name

        if ':' in without_numbers:
            without_client = without_numbers.split(':', 1)[1]
            if name == without_client:
                return port_name
    else:
        # Let caller deal with it.
        return name
