from mido import Message, MidiFile, MidiTrack

mid = MidiFile(ticks_per_beat=480)

melody = MidiTrack()
chords = MidiTrack()
bass = MidiTrack()

mid.tracks.append(melody)
mid.tracks.append(chords)
mid.tracks.append(bass)

melody.append(Message('program_change', program=0, time=0))
chords.append(Message('program_change', program=48, time=0))  # Strings/Pad
bass.append(Message('program_change', program=32, time=0))    # Bass

def note(track, n, length=480, vel=70):
    track.append(Message('note_on', note=n, velocity=vel, time=0))
    track.append(Message('note_off', note=n, velocity=vel, time=length))

def chord(track, notes, length=1920, vel=50):
    for n in notes:
        track.append(Message('note_on', note=n, velocity=vel, time=0))
    for i, n in enumerate(notes):
        track.append(Message('note_off', note=n, velocity=vel, time=length if i==0 else 0))

# MIDI note numbers
E4=64; F4s=66; G4=67; A4=69; B4=71; C5s=73; D5=74
D3=50; E3=52; F3s=54; G3=55; A3=57; B3=59

# ====================
# VERSE (4 bars)
# ====================
# Melody
note(melody, F4s); note(melody, G4); note(melody, A4); note(melody, G4)
note(melody, F4s); note(melody, G4); note(melody, A4); note(melody, B4)
note(melody, A4,720); note(melody, G4,720); note(melody, F4s,720)
note(melody, E4,720); note(melody, F4s,720)

# Chords
chord(chords, [50,54,57])   # D
chord(chords, [57,61,64])   # A
chord(chords, [59,62,66])   # Bm
chord(chords, [55,59,62])   # G

# Bass
note(bass, D3,1920)
note(bass, A3,1920)
note(bass, B3,1920)
note(bass, G3,1920)

# ====================
# PRE-CHORUS (2 bars)
# ====================
note(melody, G4); note(melody, A4); note(melody, B4); note(melody, A4)
note(melody, A4); note(melody, B4); note(melody, C5s,960)

chord(chords, [55,59,62])   # G
chord(chords, [57,61,64])   # A

note(bass, G3,1920)
note(bass, A3,1920)

# ====================
# CHORUS (4 bars)
# ====================
note(melody, B4); note(melody, C5s); note(melody, D5); note(melody, C5s)
note(melody, B4,720); note(melody, A4,720); note(melody, G4,720)
note(melody, A4); note(melody, B4); note(melody, C5s); note(melody, D5,960)
note(melody, C5s,960); note(melody, B4,960); note(melody, A4,960)

chord(chords, [59,62,66])   # Bm
chord(chords, [55,59,62])   # G
chord(chords, [50,54,57])   # D
chord(chords, [57,61,64])   # A

note(bass, B3,1920)
note(bass, G3,1920)
note(bass, D3,1920)
note(bass, A3,1920)

mid.save("Mystical_Style_Full.mid")
