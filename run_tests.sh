#!/bin/sh
#
# Run tests with Python 2 and 3:
#
#     ./run_tests.sh
# 
# If you don't have Python 3, you can run tests with:
#
#     python tests.py
#
# To run only one test, you can do:
#
#     ./run_tests.sh TestParser.test_realtime_inside_sysex
#

export PYTHONPATH=$(pwd):$PYTHONPATH

# 'python2' doesn't exist in OS X, so we need some tests here.
if [ -z $(which python2) ]
then
    python2=python
else
    python2=python2
fi

if [ -z $(which python3) ]
then
    python3=python
else
    python3=python3
fi

$python2 setup.py test $* && $python3 setup.py test $*
