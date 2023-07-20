.. SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0


Glossary
========

.. glossary::

    ascii
        American Standard Code for Information Interchange.
        The most popular character encoding standard.

    backend
    backends
    backend(s)
        A Mido backend is the interface between the library and the operating
        system level MIDI stack.
        See :doc:`backends/index` for more informations.

    callback
        A function called by the :term:`backend` when message(s) are ready to
        process.

    cli
        Command Line Interface.

    file
    files
    midi file
    standard midi file
    SMF
        A standard MIDI file.
        As defined by the MIDI Association's specification.

    message
    messages
        A MIDI message.

    midi
        The Musical Instrument Digital Interface. The specification is
        maintained by the `MIDI Association <https://midi.org>`_.

    nibble
        Half a byte (usually 4 bits).
        An 8-bit byte has 2 nibbles: an upper and a lower nibble.

    pip
        The `Python Package Installer <https://pypi.org/project/pip/>`_.

    port
    ports
        A MIDI port.

    pypi
        The `Python Package Index <https://pypi.org>`_.

    python
        The `Python programming language <https://www.python.org>`_.

    rtd
    read the docs
        `Read the Docs <https://www.readthedocs.org>`_ or RTD for short
        is a popular service to build, manage versions and host documentation
        generated from Sphinx (and now MkDocs) in the Python ecosystem.

    rtpmidi
        A standard protocol to send MIDI over a TCP/IP link.

        .. seealso::

            * :rfc:`4695`

            * :rfc:`4696`

    tcp
        Transmission Control Protocol.

        .. seealso:: :rfc:`9293`

    tick
    ticks
        The :term:`MIDI File` unit of time.

    sysex
    system exclusive
        Special :term:`MIDI` messages that are intended for consumption by a
        specific device. Details about the structure and meaning of these
        messages are often found in the device's manual.


.. todo:: Fill this glossary and add the ``:term:`` directive where
          appropriate.
