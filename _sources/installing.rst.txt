.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
.. SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Installing
==========


Requirements
------------

Mido requires :term:`Python` version 3.7 or higher.

A few dependencies are also required in order to allow Mido to introspect its
own version:

* `packaging`
* `importlib_metadata` for :term:`Python` < 3.8

.. note::

    Dependency management is handled automatically when installing using the
    recommended methods. No need to bother installing these manually.


Optional
--------

Dependencies for the loaded on-demand :term:`port` :term:`backend(s)` are
optional unless you want to use the :term:`ports` feature.

See :doc:`backends/index` for help choosing a :term:`backend`.


Installation
------------

The recommended installation method is to use :term:`pip` to retrieve the
package from :term:`PyPi`.

.. note::

    Consider using a *virtual environment* to isolate your installation from
    your current environment.

This ensures that you always get the latest released stable version::

    python3 -m pip install mido

Or, alternatively, if you want to use :term:`ports` with the default
:term:`backend`::

    python3 -m pip install mido[ports-rtmidi]

See :doc:`backends/index` for installation instructions for other
:term:`backends`.
