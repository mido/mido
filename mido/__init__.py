# -*- coding: utf-8 -*-

"""
Ole Martin Bjørndalen
ombdalen@gmail.com
http://nerdly.info/ole/
"""

__author__ = 'Ole Martin Bjørndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://nerdly.info/ole/'
__license__ = 'MIT'
__version__ = '0.0.0'

__all__ = []  # Prevent splat import

from .msg import Message
from .parser import Parser, parse, parseall
new = Message  # Shortcut
