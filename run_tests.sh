#!/bin/bash
#
# Runs tests in Python 2 and 3.
#
# If you want tests to run before each commit you can install this as
# a pre-commit hook:
#
#   ln -sf ../../run_tests.sh .git/hooks/pre-commit
#
# The commit will now be canceled if tests fail.
#
function display() {
  echo -e '\e[0;33m' $* '\e[0m'
}

display Python 2
py.test || exit 1

display Python 3
py.test-3 || exit 1
