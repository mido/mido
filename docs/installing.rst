Installing Mido
===============

Requirements
------------

Mido targets Python 2.7 and 3.2. It is developed and testeqd in Ubuntu
and Mac OS X, but should also work in Windows.

Everything is implemented in pure Python, so no compilation is
required.

There are no external dependencies unless you want to use the port
backends, which are loaded on demand.

Mido comes with backends for `PortMidi
<http://portmedia.sourceforge.net/portmidi/>`_, `python-rtmidi
<http://github.com/superquadratic/rtmidi-python>`_ and `Pygame
<http://www.pygame.org/docs/ref/midi.html>`_.


Installing
----------

To install::

    $ pip install mido


Installing PortMidi (Optional)
------------------------------

PortMidi is available in Ubuntu as ``libportmidi-dev`` and in
`MacPorts <http://www.macports.org/>`_ and `Homebrew
<http://mxcl.github.io/homebrew/>`_ as ``portmidi``.


Installing python-rtmidi (Optional)
-----------------------------------

python-rtmidi requires ``librtmidi.so``, which is available in Ubuntu
as ``librtmidi-dev`` (and possible also available as a package in
MacPorts and Homebrew.

To install::

    $ pip install python-rtmidi

This may fail in OS X due to a problem with the package. If this
happens, you can try::

   $ pip install --pre python-rtmidi

The ``--pre`` is because pip refuses to install when the library looks
like a pre-release, and says: "Could not find a version that satisfies
the requirement XYZ.")


Using Mido with PyInstaller
---------------------------

When you build an executable with PyInstaller and run it you may get
import errors like this one::

    ImportError: No module named mido.backends.portmidi

The reason is that Mido uses ``import_module()`` to import the backend
modules, while PyInstaller looks for ``import`` statements.

The easiest fix is to import the module at the top of the program::

    import mido
    import mido.backends.portmidi  # The backend you want to use.
    print(mido.get_input_names())

and then run ``pyinstaller`` like usual::

    $ pyinstaller --onefile midotest.py
    $ ./dist/midotest 
    [u'Midi Through Port-0']

If you don't want to change the program, you can instead declare the
backend module as a `hidden import
<http://www.pyinstaller.org/export/develop/project/doc/Manual.html#listing-hidden-imports>`_.
