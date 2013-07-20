#!/usr/bin/env python
import os
import sys
import mido

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

# Todo: what about python 3?
if sys.argv[-1] == "test":
    os.system("python tests.py")
    sys.exit()

required = []

setup(
    name='mido',
    version=mido.__version__,
    description='MIDI Objects for Python',
    long_description=open('README.rst').read(),
    author=mido.__author__,
    author_email=mido.__email__,
    package_data={'': ['LICENSE']},
    package_dir={'requests': 'requests'},
    packages = ['mido'],
    include_package_data=True,
    url=mido.__url__,
    # install_requires=required,  # Unknown option in Python 3
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
    ),
)
