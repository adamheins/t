# trash

Simple CLI tool for removing files.

## Motivation

I make mistakes, but I don't want one of those mistakes to be accidentally
permanently deleting an important file. I spend much of my computer time in the
terminal, but `rm` can be a dangerous thing. There are already tools that seek
to remedy this problem; `trash` is another one. 

`trash` is designed for interactive use, and incorporates more protections for
this usecase than [safe-rm](https://launchpad.net/safe-rm). At the same time,
it is much simpler than larger projects like
[trash-cli](http://code.google.com/p/trash-cli/).

## Features
* Incorporates directory blacklist like `safe-rm` to avoid deleting important
  system directories.
* Prompts user for confirmation before removing multiple items.
* Keeps deleted items for a configurable number of days before automatically
  permanently deleting them. Permanent deletion requires the `-f` flag and
  prompts for confirmation.
* Only deletes multiple files if no error occurs with any one of them.

## Usage
```
usage: trash [-rf] <files>...

options:
  -f  Delete files forever.
  -r  Recursively remove directories.
```

## License
MIT - see the LICENSE file.
