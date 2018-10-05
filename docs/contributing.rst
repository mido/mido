Contributing
============


Questions
---------

If you have questions about contributing code or suggestions
for how to make contributing easier, please write to
https://groups.google.com/forum/#!forum/mido-community.


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

    py.test

Before submission, it is required that the tox tests run and pass. Run the tox tests using::

    tox 

It is required to test on at least 2.7 and 3.5 before submission. Any other passes are nice to have

You can also set up a commit hook::

    echo "tox" >.git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

This will run tests when you commit and cancel the commit if any tests
fail.



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
   git pull . master
   git push
   git checkout master


Update Read the Docs
^^^^^^^^^^^^^^^^^^^^

Log into readthedocs.org and build the latest documentation. This is
set up to use the stable branch.
