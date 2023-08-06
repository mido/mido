import mido
import fractions

mid = mido.MidiFile('C:/Dropbox/Literature/PROJECTS/MIO/app - piano roll video/MIDI files/GoodTheBadAndTheUgly.mid')


'''
for msg in mid:
    if msg.type == 'control_change' and msg.control==0x65:
        print(msg.control)
        print(msg.value)
'''
for msg, inferred in mid:
    #print(msg, inferred)
    pass

#print([*mid])

#print(mid)



