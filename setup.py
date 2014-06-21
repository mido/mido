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

if sys.argv[-1] == "test":
    os.system("python run_tests.py")
    sys.exit()

setup(
    name='mido',
    version=mido.__version__,
    description='MIDI Objects for Python',
    long_description=open('README.rst', 'rt').read(),
    author=mido.__author__,
    author_email=mido.__email__,
    url=mido.__url__,
    package_data={'': ['LICENSE']},
    package_dir={'mido': 'mido'},
    packages = ['mido', 'mido.backends'],
    scripts = ['bin/mido-play',
               'bin/mido-ports',
               'bin/mido-serve',
               'bin/mido-connect'],
    include_package_data=True,
    install_requires=[],
    license='MIT',
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
