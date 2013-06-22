import time
import modo.portmidi as pm

port = pm.Input('SH-201 MIDI 1')
while 1:
    for msg in port:
        print(msg)
        
    time.sleep(0.01)

