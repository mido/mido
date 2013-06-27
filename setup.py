#!/usr/bin/env python
import os
import sys
import mido

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



# if sys.argv[-1] == "publish":
#     os.system("python setup.py sdist upload")
#     sys.exit()

if sys.argv[-1] == "test":
    os.system("python -m pytest")
    sys.exit()

required = []

setup(
    name='mido',
    version=mido.__version__,
    description='library for writing MIDI applications',
    long_description=open('README.rst').read(),
    author=mido.__author__,
    email=mido.__email__,
    url=mido.__url__,
    packages=[
        'mido',
    ],
    py_modules=[
    ],
    # install_requires=required,  # Unknown option in Python 3
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
    ),
)
