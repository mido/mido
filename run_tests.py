#!/usr/bin/env python
"""
Run unit tests in Python 2 and 3.
"""
from __future__ import print_function
import re
import sys
from subprocess import Popen, PIPE

def get_version(program):
    try:
        proc = Popen([program, '--version'], stdout=PIPE, stderr=PIPE)
        line = proc.stdout.read().decode('utf-8')
        line += proc.stderr.read().decode('utf-8')
        proc.wait()
    except OSError:
        return None

    # The line contains "Python 2.7.4".
    # Get the version number as a tuple of ints.
    match = re.search('Python (\d+)\.(\d+)\.(\d+)', line)
    if match:
        return tuple(map(int, match.groups()))
    else:
        return None


def get_python(required_version):
    major = required_version[0]
    minor = required_version[1]

    for program in ['python{}'.format(major), 'python']:
        version = get_version(program)
        if version[0] == major and version >= required_version:
            return program

    return None

REQUIRED_VERSIONS = [(2, 7, 0), (3, 2, 0)]

def main():
    programs = []
    for version in REQUIRED_VERSIONS:
        program = get_python(version)
        if program is None:
            print('Python {} >= {} not found'.format(version[0],
                                                     version), file=sys.stderr)
        else:
            programs.append(program)

    if len(programs) < len(REQUIRED_VERSIONS):
        return 1

    for program in programs:
        proc = Popen([program, 'tests.py'])
        proc.wait()
        if proc.returncode != 0:
            sys.exit('Tests failed with {}.'.format(python))

            
sys.exit(main())
