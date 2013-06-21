#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import modo

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
    name='modo',
    version=modo.__version__,
    description='library for writing MIDI applications',
    long_description=open('README.rst').read(),
    author=modo.__author__,
    email=modo.__email__,
    url=modo.__url__,
    packages=[
        'modo',
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
