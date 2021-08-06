import mido
import queue
import time

rtmidi = mido.Backend('mido.backends.rtmidi')

def myfunc(msg, q):
    print(f'Got message: {msg}')
    q.put(msg)

q = queue.Queue()
input_ = rtmidi.open_input('testing', virtual=True, callback_w_args=(myfunc, q))

while True:
    time.sleep(1)
