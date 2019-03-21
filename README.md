# trash

Simple CLI tool for removing files.

## Motivation

I make mistakes, but I don't want one of those mistakes to be accidentally
permanently deleting an important file. I spend much of my computer time in the
terminal, but `rm` can be a dangerous thing. There are already tools that seek
to remedy this problem; `trash` is another one. It is designed to be very
simple, yet safe.

## Features
* Incorporates directory blacklist like `safe-rm` to avoid deleting important
  system directories.
* Prompts user for confirmation before removing multiple items.
* Keeps deleted items for a configurable number of days before automatically
  permanently deleting.

## License
MIT - see the LICENSE file.
