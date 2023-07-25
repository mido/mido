.. SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
.. SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Contributing
============


Questions
---------

If you have questions about using  Mido, contributing code or suggestions
for how to make contributing easier, please write at
https://github.com/mido/mido/discussions.


Bugs & Feature Requests
-----------------------

.. note::

    If you don't have a precise idea, please use the questions section outlined
    above instead of opening an issue.

If you encounter a bug that is reproducible or want to suggest
a new feature - including its implementation details -
that would fit the project nicely, feel free to open an issue at
https://github.com/mido/mido/issues

Please provide as much information as possible to allow us to analyze,
including but not limited to:

* Operating system name & version

* Python version

* ``mido`` package version & installation method
  (Distribution repository, PyPI, source…)

* backend used (``amidi``, ``portmidi``, ``rtmidi``, ``PyGame``…
  Defaults to ``python-rtmidi``.)


Forking & Pull Requests
-----------------------

The project welcomes all contributions!

If you wish to make a change, be it code or documentation, please
fork the repository from
https://github.com/mido/mido
and send your pull request to
https://github.com/mido/mido/pulls.

Your changes will be reviewed by a maintainer and integrated for publication
in the next version of `mido` once approved.

Installation
------------

Users
^^^^^

For general usage, see :doc:`installing`.


If you wish to install from source,
run the following command from the sources root directory::

    python3 -m pip install --editable .

Or, alternatively if you want to use ports::

    python3 -m pip install --editable .[ports-rtmidi]


.. note::

    *No support* will be provided if you install from source.

Developers
^^^^^^^^^^

.. warning::

    We recommend that you first setup a *virtual environment* to
    avoid conflicts with already installed files.

    .. seealso::

        https://packaging.python.org/en/latest/tutorials/installing-packages/

Then, to install the *development dependencies*, you can run the following
command from inside your virtual environment::

    python3 -m pip install --editable .[dev]

Or, alternatively, if you want to use ports::

    python3 -m pip install --editable .[dev,ports-rtmidi]

This will install all needed dependencies for
linting, testing, documentation generation and publishing releases.


Code Checks
-----------

.. note::

    The following code checks are done automatically using
    a GitHub Actions Workflow (Defined in :file:`.github/workflow/tests.yml`)
    for each push to the ``main`` branch and each Pull Request.

It's good practice to check your changes *locally* before submitting.


Linting
^^^^^^^

Linting is done with `flake8 <https://flake8.pycqa.org/en/latest/>`_.
Its configuration can be found in `.flake8`.

You can lint your code using::

    flake8


Copyright and REUSE Compliance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The project is `REUSE <https://reuse.software>`_ compliant.

If you wish to add your copyright to a file,
please add an SPDX header if the form of:

.. code-block:: python

    # SPDX-FileCopyrightText: YYYY First_Name Last_Name <email_address>
    #
    # SPDX-License-Identifier: MIT

.. note::

    Use the appropriate comment format and license for the file and only add the
    first line below existing copyright mentions if modifying an existing file.

    The year should only be set the first time you edit a file and never touched
    again. There is **no** benefit in updating it constantly!

then run::

    reuse lint


Testing
^^^^^^^

`pytest <https://doc.pytest.org>`_
is used for unit testing. The tests are found in
`tests/test_*.py <../tests/>`_.
The default configuration is declared in the ``tool.pytest.ini_options``
section of :file:`pyproject.toml`.

The test suite can be run using the command::

    pytest


Checking the Release Manifest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To make sure the repository and
source code manifest (:file:`.MANIFEST.in`)
are in sync::

    check-manifest --verbose


Building the Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

The  documentation is generated using
`Sphinx <https://www.sphinx-doc.org/>`_.

To generate the HTML documentation::

    sphinx-build -j auto -q -W -E --keep-going docs docs/_build


If you wish to build a PDF version for *local* use:

#. Install a `LaTeX <https://www.latex-project.org/get>`_ distribution

#. Install `ImageMagick <https://imagemagick.org>`_

#. use::

    sphinx-build -M latexpdf docs docs/_build


You'll find the resulting PDF file at :file:`docs/_build/latex/Mido.pdf`.

Once generated and copied in a safe place,
you may want to remove the build artifacts::

    sphinx-build -M clean docs docs/_build


Testing MIDI File Support
-------------------------


Test Files
^^^^^^^^^^

The
`Lakh MIDI Dataset <https://www.colinraffel.com/projects/lmd/>`_
is a great resource for testing the MIDI file parser.


Releasing
---------

The processes are now automated.

.. note::
    The whole team has access to manual publishing
    to :term:`PyPI` and :term:`Read the Docs` in case of automation defect.


Documentation
^^^^^^^^^^^^^

To generate the official documentation, we use :term:`Read the Docs` integration
services for GitHub. Every time a new commit is pushed or merged onto our
``main`` development branch on GitHub, the ``latest`` version of the
documentation is updated by Read the Docs. Each time a new version is tagged,
the new  documentation version is created, built, published and eventually
promoted to``stable`` following Semantic Versioning.
The ``stable`` version of the documentation is the one served by default if
no specific version is chosen.

We also build a mirror of the current ``main`` development branch documentation
using a GitHub Workflow and hosted on GitHub pages.

All of this is defined by :file:`.github/workflow/documentation.yml`


Package
^^^^^^^

The process uses GitHub Action Workflow defined by
:file:`.github/workflow/release.yml` and is triggered upon receiving a tag.


Preparation
^^^^^^^^^^^

Make sure all the tests pass, documentation has been updated and everything
is in good order before proceeding.

Update the Changelog and Bump Version number.

.. note::

    The version number should be :pep:`440` & SemVer compliant.

    ``X.Y.Z`` is the version, for example ``1.1.18`` or ``1.2.0``.

#. update the changelog in :file:`docs/changes.rst`. The following commands
   may prove useful to retrieve all Pull Requests & all commits::

    previous_release_tag=git describe --abbrev=0
    git log --oneline --merges --reverse "${previous_release_tag}.."
    git log --oneline --no-merges --reverse "${previous_release_tag}.."

#. update version and date in :file:`docs/changes.rst`

#. commit the changes::

    git commit -a -c "Prepare <X.Y.Z> release."

#. set the version number by tagging the release::

    git tag -a <X.Y.Z> -m "mido version <X.Y.Z>"

   .. note::

        We use an annotated tag here to retain all information about the tagger
        and create a proper object in the GIT database instead of a commit alias.

        .. seealso:: https://git-scm.com/book/en/v2/Git-Basics-Tagging

#. don’t forget to push your changes including the tags to GitHub to trigger
   the auto-release process::

    git push --tags


Manual steps (Recovery)
^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

    Only use if the automatic process fails for some reason.

#. Prepare a clean environment::

    git clone --branch <X.Y.Z> --single-branch https://github.com/mido/mido mido-<X.Y.Z>
    cd mido-<X.Y.Z>
    python3 -m venv mido-build

#. Build::

    source mido-build/bin/activate
    python3 -m pip install --upgrade pip setuptools wheel build twine
    python3 -m build

#. Publish on Test PyPI::

    python3 -m build
    twine upload --repository testpypi dist/*

#. Check that the published package is good::

    python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps mido
    python3 -c "import mido; print(mido.version_info)"

   .. todo::

        Now would be a good time to run some integration tests once we have them.

#. Publish on PyPI::

    twine upload dist/*

   .. warning::

        This is the most critical step of the process. This **cannot** be undone.
        Make sure everything is in good order before pressing the "big red button"!
