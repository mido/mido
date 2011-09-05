import protomidi
from protomidi.msg import *

p = protomidi.Parser()
p.feed('\x90\x01\x02')
print p._messages
