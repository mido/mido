#!/bin/sh

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

$python2 test_mido.py && $python3 test_mido.py
