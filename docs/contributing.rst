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

    pip install -e .[dev]

This will install all needed dependencies for testing and documentation.


Testing
-------

`pytest <http://doc.pytest.org/>`_ is used for unit testing. The tests
are found in `mido/test_*.py`.

Tests can be run using the command::

    pip install -q -e .[dev]
    pytest . -rs -q

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

X.Y.Z is the version, for example 1.1.18 or 1.2.0.

* update version and date in `docs/changes.rst`

* update version in `mido/__about__.py`

* `git commit -a -c "Bumped version to X.Y.Z."`



Publish on PyPI
^^^^^^^^^^^^^^^

I like to do this before I push to GitHub. This way if the package
fails to upload I can roll back and fix it before I push my changes.

::

    rm -rf dist/*

    python setup.py bdist_wheel --universal
    python setup.py sdist

    twine upload dist/*


Push to GitHub
^^^^^^^^^^^^^^

::

    git tag X.Y.Z
    git push
    git push --tags


Update the stable branch (if this is a stable release):

::

   git checkout stable
   git pull . main
   git push
   git checkout main


Update Read the Docs
^^^^^^^^^^^^^^^^^^^^

Log into readthedocs.org and build the latest documentation. This is
set up to use the stable branch.
