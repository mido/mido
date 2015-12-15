__author__ = 'brianoneill'

from unittest import TestCase

import mido
from mido.messages import Message
from mido.midifiles import MidiFile, MidiTrack

import io
import tempfile
import os
import sys


class TestMidiFileIO(TestCase):
    bio = io.BytesIO()    # will contain a midifile
    expected_bio = b'MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\xe0' \
                   b'MTrk\x00\x00\x00\x10\x00\xc0\x0c \x90@@\x81\x00\x80@\x7f\x00\xff/\x00'
    expected_sio = '''\
=== Track 0
<message program_change channel=0 program=12 time=0>
<message note_on channel=0 note=64 velocity=64 time=32>
<message note_off channel=0 note=64 velocity=127 time=128>
<meta message end_of_track time=0>
'''

    @classmethod
    def setUpClass(cls):
        """Create new/empty MidiFile, populate it, save to `cls.bio`.
        """
        with MidiFile() as midi:
            track = MidiTrack()
            midi.tracks.append(track)

            track.append(Message('program_change', program=12, time=0))
            track.append(Message('note_on', note=64, velocity=64, time=32))
            track.append(Message('note_off', note=64, velocity=127, time=128))

            # midi.save('new_song.mid')
            midi.save(file=cls.bio)

    def test_midifile_to_bytesIO(self):
        """Compare bio to expected value.
        """
        self.assertFalse(self.bio.closed)
        self.assertEqual(self.bio.getvalue(), self.expected_bio)

    def test_midifile_from_bytesIO(self):
        """Create MidiFile from `self.bio`; temporarily trap stdout and call `print_tracks()`;
        compare what was printed to expected value.
        """
        midifile = MidiFile(file=self.bio)

        _stdout = sys.stdout
        sio= io.StringIO()
        sys.stdout = sio
        midifile.print_tracks()
        sys.stdout = _stdout

        self.assertEqual(sio.getvalue(), self.expected_sio)

    def test_midifile_to_from_file(self):
        """Write MidiFile to external file, read file back in as a MidiFile,
        `save` it to another BytesIO; compare to `self.bio`.
        Also check that writes to, reads from external file close file when
        use of them is finished.
        """
        midifile = MidiFile(file=self.bio)

        # Get a temp file name, don't leave the file open,
        # but don't delete it either, just to reserve the name.
        named_tempfile = tempfile.NamedTemporaryFile('wb', delete=False)    # keep after closing
        tempfilename = named_tempfile.name
        named_tempfile.close()

        # Write midifile to temp file (name)
        midifile.save(tempfilename)             # closes named_tempfile
        self.assertTrue(named_tempfile.file.closed)

        # read midifile back in to another BytesIO
        bio2 = io.BytesIO()
        with MidiFile(tempfilename) as midi2:   # closes it again
            midi2.save(file=bio2)
        self.assertFalse(bio2.closed)
        self.assertTrue(named_tempfile.file.closed)

        os.remove(named_tempfile.name)          # cleanup temp file

        # compare midifile(s)
        self.assertEqual(self.bio.getvalue(), bio2.getvalue())
