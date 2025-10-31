# 🎵 Bailoteo – Beat de Reguetón (MIDI)
# BPM: 96 | Estilo: Reggaetón comercial
# Autor: ChatGPT (GPT-5)

from mido import Message, MidiFile, MidiTrack, bpm2tempo

# Crear archivo MIDI y pista
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Configurar tempo
bpm = 96
track.append(Message('program_change', program=0, time=0))
track.append(Message('control_change', control=7, value=100, time=0))  # volumen

tempo = bpm2tempo(bpm)
track.append(Message('program_change', program=32, time=0))  # Synth bass

# Función helper
def note_on_off(note, velocity, duration, channel=0):
    track.append(Message('note_on', note=note, velocity=velocity, time=0, channel=channel))
    track.append(Message('note_off', note=note, velocity=0, time=int(duration), channel=channel))

# --- Estructura del beat (4 compases de reggaetón) ---
# Dembow clásico: bombo, caja, bombo-bombo, caja

# Nota: MIDI ticks -> ajustado para 480 ticks por beat (por defecto)
beat = 480

# Instrumentos MIDI channels
kick_ch = 9    # canal 10 (percusión)
snare_ch = 9
bass_ch = 1
chord_ch = 2

# Dembow pattern (bombo y caja)
def dembow_pattern():
    # 1
    track.append(Message('note_on', note=36, velocity=110, time=0, channel=kick_ch))  # Kick
    track.append(Message('note_off', note=36, velocity=0, time=int(beat/2), channel=kick_ch))
    # 2
    track.append(Message('note_on', note=38, velocity=100, time=0, channel=snare_ch))  # Snare
    track.append(Message('note_off', note=38, velocity=0, time=int(beat/2), channel=snare_ch))
    # 3
    track.append(Message('note_on', note=36, velocity=110, time=0, channel=kick_ch))
    track.append(Message('note_off', note=36, velocity=0, time=int(beat/4), channel=kick_ch))
    # 4
    track.append(Message('note_on', note=36, velocity=100, time=0, channel=kick_ch))
    track.append(Message('note_off', note=36, velocity=0, time=int(beat/4), channel=kick_ch))
    # 5
    track.append(Message('note_on', note=38, velocity=100, time=0, channel=snare_ch))
    track.append(Message('note_off', note=38, velocity=0, time=int(beat/2), channel=snare_ch))

# Bajo (A1 -> G1)
def bass_pattern():
    note_on_off(33, 100, beat//2, bass_ch)  # A1
    note_on_off(33, 90, beat//2, bass_ch)
    note_on_off(31, 100, beat//2, bass_ch)  # G1
    note_on_off(31, 100, beat//2, bass_ch)

# Acordes (Amin -> Gmin)
def chords_pattern():
    for note in [57, 60, 64]:  # A minor chord
        note_on_off(note, 70, beat//2, chord_ch)
    for note in [55, 58, 62]:  # G minor chord
        note_on_off(note, 70, beat//2, chord_ch)

# Construir 8 compases (~loop principal)
for i in range(8):
    dembow_pattern()
    bass_pattern()
    chords_pattern()

# Guardar archivo
mid.save("bailoteo_beat.mid")

print("✅ Archivo MIDI creado: bailoteo_beat.mid")
