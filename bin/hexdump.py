#!/usr/bin/env python

from __future__ import print_function
import sys
import subprocess

def lookup_port(device_name):
    """
    Look up ALSA port by name.
    """

    p = subprocess.Popen(['amidi', '-l'], stdout=subprocess.PIPE)
    for line in p.stdout:
        line = line.strip()
        direction, port, name = line.split(None, 2)
 
        if name == device_name:
            return port
    
    return None

device_name = sys.argv[1]
port = lookup_port(device_name)
if port:
    p = subprocess.call(['amidi', '-p', port, '-d'])
else:
    print('No ALSA device named %r' % device_name, file=sys.stderr)


