Freezing to EXE File
====================

PyInstaller
-----------

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
<http://pythonhosted.org/PyInstaller/#listing-hidden-imports>`_.


bbFreeze, py2exe, cx_Freeze, py2app, etc.
-----------------------------------------

I suspect the same is true for these, but I have not had a chance to
try it out yet.

Adding the explicit ``import`` statement should always work, though,
since Mido backends are just normal Python modules.
