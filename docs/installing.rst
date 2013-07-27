Installing Mido
================

Requirements
-------------

Mido targets Python 2.7 and 3.2 and runs on Ubuntu and Mac OS X. May
also run on other systems.

If you want to use message ports, you will need `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_ installed on
your system. The PortMidi library is loaded on demand, so you can use
the parser and messages without it.


Installing
-----------

To install::

    $ pip install mido

The PortMidi wrapper is written with `ctypes`, so no compilation is
required.


Installing PortMidi
--------------------

If you want to use ports, you need the PortMidi shared library. The
Ubuntu package is called ``libportmidi-dev``.  It can also be found in
`MacPorts <http://www.macports.org/>`_ and `Homebrew
<http://mxcl.github.io/homebrew/>`_ under the name ``portmidi``.
