#!/usr/bin/env python
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

elif sys.argv[-1] == "docs":
    os.system("sphinx-build docs docs/_build")
    sys.exit()

version = '1.2.8'
author = 'Ole Martin Bjorndalen'
email = 'ombdalen@gmail.com'
url = 'https://mido.readthedocs.io/'
license = 'MIT'

setup(
    name='mido',
    version=version,
    description='MIDI Objects for Python',
    long_description=open('README.rst', 'rt').read(),
    author=author,
    author_email=email,
    url=url,
    license=license,
    package_data={'': ['LICENSE']},
    package_dir={'mido': 'mido'},
    packages=['mido', 'mido.backends'],
    scripts=['bin/mido-play',
             'bin/mido-ports',
             'bin/mido-serve',
             'bin/mido-connect'],
    include_package_data=True,
    install_requires=[],
    extras_require={
        'dev': ['check-manifest>=0.35',
                'flake8>=3.4.1',
                'pytest>=3.2.2',
                'sphinx>=1.6.3',
                'tox>=2.8.2'
                ],
        'ports': ['python-rtmidi>=1.1.0']
    },
    zip_safe=False,
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
