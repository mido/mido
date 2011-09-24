import time
import pprint
import protomidi.amidi as amidi

input = amidi.Input('SH-201 MIDI 1')
while 1:
    for msg in input:
        print(msg)

    time.sleep(0.001)
