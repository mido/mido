#!/usr/bin/env python
"""
Run unit tests in Python 2 and 3.
"""
import re
import sys
from subprocess import Popen, PIPE

requirements = {2: (2, 7, 0),
                3: (3, 2, 0)}

def get_pythons():
    pythons = {2: None,
               3: None}

    """Locates Pyhton 2 and 3 and returns them as a tuple."""
    for major_version, requirement in requirements.items():
        for python in ['python', 'python2', 'python3']:
            try:
                proc = Popen([python, '--version'], stderr=PIPE)
                line = proc.stderr.read().decode('utf-8')
                proc.wait()
            except OSError:
                # Program was not found.
                continue

            # The line contains "Python 2.7.4".
            # Get the version number as a tuple of ints.
            match = re.search('Python (\d+)\.(\d+)\.(\d+)', line)
            if match:
                version = tuple(map(int, match.groups()))
                if version[0] == major_version and version > requirement:
                    pythons[major_version] = python

    for major_version in pythons:
        if pythons[major_version] is None:
            sys.exit('Python {} >= {} not found'.format(
                    major_version,
                    requirements[major_version]))

    return (pythons[2], pythons[3])

for python in get_pythons():
    proc = Popen([python, 'tests.py'])
    proc.wait()
    if proc.returncode != 0:
        sys.exit('Tests failed with {}.'.format(python))
