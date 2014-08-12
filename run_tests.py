#!/usr/bin/env python
"""
Runs tests in Python 2 and 3.
 
If you want tests to run before each commit you can install this as
a pre-commit hook:

   ln -sf ../../run_tests.py .git/hooks/pre-commit

The commit will now be canceled if tests fail.
"""
import os
import sys
sys.path.insert(0, '.')

def print_yellow(message):
    print('\033[0;33m{}\033[0m'.format(message))

print_yellow('Python 2')
if os.system('py.test'):
    sys.exit(1)

print_yellow('Python 3')
if os.system('py.test-3'):
    sys.exit(1)
