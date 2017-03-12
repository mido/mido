Contributing
============


Testing
-------

`pytest <http://doc.pytest.org/>`_ is used for unit testing. The tests
are found in `mido/test_*.py`.

If you can please run tests in both Python 2 and Python 3 before you
commit code. I've renamed the executables so I can just run `pytest2
&& pytest3` instead of remembering what the programs are called. (I
think they were `py.test` and `py.test-3`.)

You can also set up a commit hook::

    echo "pytest2 && pytest3" >.git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

This will run tests when you commit and cancel the commit if any tests
fail.



Testing MIDI file support
-------------------------

Test Files
^^^^^^^^^^

The `Lakh MIDI Dataset <http://www.colinraffel.com/projects/lmd/>`_ is
a great resouce for testing the MIDI file parser.


Publishing (Release Checklist)
------------------------------

I am currently the only one with access to publishing on PyPI and
readthedocs. This will hopefully change in the future.


First Time: Register With PyPI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    ./setup.py register


Test
^^^^

::

    rm -rf docs/_build && ./setup.py docs
    pytest2 && pytest3
    check-manifest -v

(`pip3 install check-manifest`)

You can also test that the package installs by installing it in a
virtualenv with `pip` and `easy_install` (Python 2 and 3) and
importing it. This is a bit tedious. Perhaps there is a good way to
automate it.



Bump Version
^^^^^^^^^^^^

X.Y.Z is the version, for example 1.1.18 or 1.2.0.

* update version and date in `docs/changes.rst`

* update version in `mido/version.py`

* `git commit -a -c "Bumped version to X.Y.Z."`

Then:

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


Publish
^^^^^^^

Publish in PyPI::

    python setup.py publish
    python setup.py bdist_wheel upload

Last thing:


Update readthedocs
^^^^^^^^^^^^^^^^^^

