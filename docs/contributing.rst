Contributing
============


Questions
---------

If you have questions about contributing code or suggestions
for how to make contributing easier, please write at
https://github.com/mido/mido/discussions.


Installing for developers
-------------------------

To install the dev dependencies, you can run the command::

    python3 -m pip install --editable .[dev]

This will install all needed dependencies for testing and documentation.


Testing
-------

`pytest <http://doc.pytest.org/>`_ is used for unit testing. The tests
are found in `mido/test_*.py`.

Tests can be run using the command::

    python3 -m pip install --quiet --editable .[dev]
    pytest

This is also run automatically at every push to the `main` branch and
at every pull request, as part of the GitHub Actions workflow.


Testing MIDI file support
-------------------------

Test Files
^^^^^^^^^^

The `Lakh MIDI Dataset <http://www.colinraffel.com/projects/lmd/>`_ is
a great resource for testing the MIDI file parser.


Publishing (Release Checklist)
------------------------------

I am currently the only one with access to publishing on PyPI and
readthedocs. This will hopefully change in the future.


Bump Version
^^^^^^^^^^^^

The version number should be `PEP440 <https://peps.python.org/pep-0440/>`_ compliant.

X.Y.Z is the version, for example 1.1.18 or 1.2.0.

* update version and date in `docs/changes.rst`

* `git commit -a -c "Bumped version to X.Y.Z."`

* `git tag X.Y.Z"`


Publish on Test PyPI
^^^^^^^^^^^^^^^^^^^^

.. warning::
    TODO: Move to GitHub actions

I like to do this before I push to GitHub. This way if the package
fails to upload I can roll back and fix it before I push my changes.

::

    python3 -m pip install --upgrade setuptools twine
    rm -rf dist/*
    python3 -m build
    twine upload --repository testpypi dist/*


Push to GitHub
^^^^^^^^^^^^^^

If all went well everything is ready for prime time.

::

    git push --tags


Update Read the Docs
^^^^^^^^^^^^^^^^^^^^

.. warning::
    TODO: Move to GitHub actions

Log into readthedocs.org and build the latest documentation. This is
set up to use the stable branch.


Publish on PyPI
^^^^^^^^^^^^^^^

.. warning::
    TODO: Move to GitHub actions

::

    twine upload dist/*


