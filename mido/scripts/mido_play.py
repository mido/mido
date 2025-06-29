#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Play MIDI file on output port.

Example:

    mido-play some_file.mid

Todo:

  - add option for printing messages
"""
import argparse
import re
import sys

import mido
from mido import Message, MidiFile, tempo2bpm


def program_override(value):
    """Parse a CHANNEL=PROGRAM format commandline option."""
    match = re.match(r"(?P<channel>\d+)=(?P<program>\d+)", value)
    if match:
        return int(match["channel"]), int(match["program"])
    raise ValueError


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    arg = parser.add_argument

    arg('-o', '--output-port',
        help='Mido port to send output to')

    arg('-m', '--print-messages',
        dest='print_messages',
        action='store_true',
        default=False,
        help='Print messages as they are played back')

    arg('-q', '--quiet',
        dest='quiet',
        action='store_true',
        default=False,
        help='print nothing')

    arg("-f", "--force-program",
        type=program_override,
        action="append",
        default=[],
        help="Override the program for program_change messages on the given channel. "
             "Can be passed multiple times.",
        metavar="CHANNEL=PROGRAM",
    )

    arg('files',
        metavar='FILE',
        nargs='+',
        help='MIDI file to play')

    return parser.parse_args()


def play_file(output, filename, print_messages, program_overrides):
    midi_file = MidiFile(filename)

    print(f'Playing {midi_file.filename}.')
    length = midi_file.length
    print('Song length: {} minutes, {} seconds.'.format(
        int(length / 60),
        int(length % 60)))
    print('Tracks:')
    for i, track in enumerate(midi_file.tracks):
        print(f'  {i:2d}: {track.name.strip()!r}')

    for message in midi_file.play(meta_messages=True):
        if print_messages:
            sys.stdout.write(repr(message) + '\n')
            sys.stdout.flush()

        if isinstance(message, Message):
            if message.type == "program_change" and message.channel in program_overrides:
                message.program = program_overrides[message.channel]
            output.send(message)
        elif message.type == 'set_tempo':
            print('Tempo changed to {:.1f} BPM.'.format(
                tempo2bpm(message.tempo)))

    print()


def main():
    args = parse_args()

    if args.quiet:
        global print
        def print(*args):
            pass

    try:
        with mido.open_output(args.output_port) as output:
            print(f'Using output {output.name!r}.')
            output.reset()
            try:
                for filename in args.files:
                    play_file(output=output,
                              filename=filename,
                              print_messages=args.print_messages,
                              program_overrides=dict(args.force_program),
                              )
            finally:
                print()
                output.reset()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
