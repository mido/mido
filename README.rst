import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

# Create a new MIDI file and track
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Set tempo (for example, 120 BPM). The tempo here is given in microseconds per beat.
# 120 BPM corresponds to 500000 microseconds per beat.
track.append(MetaMessage('set_tempo', tempo=500000, time=0))

# Define a simple function to add a chord (all notes at the same time) to the track.
def add_chord(track, notes, start_time, duration, velocity=64, channel=0):
    """Adds a chord (list of MIDI note numbers) starting at start_time with given duration."""
    for note in notes:
        track.append(Message('note_on', note=note, velocity=velocity, time=start_time, channel=channel))
        # time for subsequent notes in the chord should be 0 so they play simultaneously.
        start_time = 0  
    for note in notes:
        track.append(Message('note_off', note=note, velocity=velocity, time=duration, channel=channel))

# MIDI note numbers for chords in a rough approximation (these may need adjustments to sound musical)
# Example chord voicings (in the appropriate octave):
#   Am: A3, C4, E4  -> MIDI notes: 57, 60, 64
#   Em: E3, G3, B3  -> MIDI notes: 52, 55, 59
#   Cmaj7: C4, E4, G4, B4  -> MIDI notes: 60, 64, 67, 71
#   B: B3, D#4, F#4  -> MIDI notes: 59, 63, 66

# Define the chords and timing (time in ticks; mido default ticks per beat = 480)
chords = [
    {'notes': [57, 60, 64], 'duration': 480},    # Am (1 beat)
    {'notes': [52, 55, 59], 'duration': 480},    # Em (1 beat)
    {'notes': [60, 64, 67, 71], 'duration': 480}, # Cmaj7 (1 beat)
    {'notes': [59, 63, 66], 'duration': 480},    # B (1 beat)
]

# For the intro, we loop the progression twice (customize as needed)
time_between_chords = 0  # We start chords immediately one after another
current_time = 0

for _ in range(2):  # Repeat the progression twice
    for chord in chords:
        add_chord(track, chord['notes'], current_time, chord['duration'])
        # After adding a chord, set time to 0 because the chord already indicates its duration.
        current_time = 0  # subsequent chords start after the previous one finishes

# Optionally add a small rest at the end
track.append(Message('note_off', note=0, velocity=0, time=480))

# Save the MIDI file
mid.save('veins_are_still_blue_intro.mid')

print("MIDI file 'veins_are_still_blue_intro.mid' created successfully.")
