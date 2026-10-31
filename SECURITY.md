<!-- SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com> -->
<!-- SPDX-License-Identifier: CC0-1.0 -->

# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.3.x   | :white_check_mark: |
| < 1.3   | :x: |

## Threat Model & Scope

mido is a library for working with **trusted** MIDI files and real-time
MIDI ports. It implements the MIDI specification and is designed for
musicians and developers handling their own data.

mido is **not** a parser for untrusted or adversarial input. It makes no
claim of robustness against crafted, fuzzed, or malformed files.

This follows the design principle at the core of Python — "we're all
consenting adults here". Python signals errors by raising exceptions and
trusts the caller to handle them, rather than sandboxing or swallowing
them. mido behaves exactly as a Python library is meant to: a caller that
ingests untrusted data is responsible for its own error handling.

### In scope

- Correct implementation of the MIDI specification for valid input.
- Crashes or incorrect behavior on **spec-conformant** files.
- Security issues within mido's own trust boundaries (for example, the
  network-reachable socket port backends).

### Out of scope

These are reported as ordinary bugs at most, not as security
vulnerabilities, and will not receive a CVE:

- Exceptions raised on malformed, truncated, or otherwise
  spec-violating input (IndexError, ValueError, ZeroDivisionError,
  TypeError, ...). Rejecting invalid data is the intended behavior.
- Robustness against adversarial or fuzzed input.
- Use as a parser in security-sensitive contexts (web uploads, ML dataset
  ingest, DAW automation on untrusted corpora) without caller-side
  sandboxing.
- Any behavior that depends on a "documented parse-error contract" —
  mido deliberately documents none.

## Hardened mode (opt-in)

A single, narrow parse-error type is a reasonable API-ergonomics
improvement. PRs are welcome for an opt-in "hardened" mode that collapses
the above exceptions into one documented error class. The default
behavior — spec-conformant parsing of trusted files — remains unchanged,
and the existence of such a mode does not imply that the default is
vulnerable.

## Reporting a Vulnerability

[Create an issue](https://github.com/mido/mido/issues/new/choose) and
select the appropriate feature, see below. Please check the **Out of
scope** list before filing.

### Publicly

Select `Bug report`.

### Privately

Select `Report a vulnerability`.
