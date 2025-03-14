# t

Simple CLI tool for removing files safely. Wraps
[trash-cli](https://github.com/andreafrancia/trash-cli).

I make mistakes, but I don't want one of those mistakes to be accidentally
permanently deleting an important file. Inspired by
[safe-rm](https://launchpad.net/safe-rm), I originally wrote this as a more
interactive alternative to `rm` that keeps files for a while before permanent
deletion and provides more interactive prompts.

Then I discovered the [XDG trash
spec](https://freedesktop.org/wiki/Specifications/trash-spec/) and the CLI
implementation [trash-cli](https://github.com/andreafrancia/trash-cli).
Allowing trash-cli to do the heavy lifting, I converted this project to a
simple wrapper around trash-cli's `trash-put` command. I wrote a bit about
different "safer `rm`" options [here](https://adamheins.com/blog/a-safer-rm).

The goal of `t` is to ensure you don't make mistakes deleting files. To that
end, it adds the following on top of trash-cli's `trash-put`:

* incorporates directory exclusion list like safe-rm to avoid deleting
  important system directories;
* prompts user for confirmation before removing multiple items;
* does require `-r` for directories;
* only deletes multiple files if no error occurs with any one of them.

## Install

Install with [uv](https://docs.astral.sh/uv/): 
```
uv tool install git+https://github.com/adamheins/t.git
```
or [pipx](https://pipx.pypa.io/stable/):
```
pipx install git+https://github.com/adamheins/t.git
```

## Usage
```
usage: t [-r] <files>...

options:
  -r  Recursively remove directories.
```

## Automatically empty trash
Install [trash-cli](https://github.com/andreafrancia/trash-cli), then use the
`trash-empty` script in a cronjob. Run `crontab -e` and add something like
```
@daily /path/to/trash-cli/trash-empty 30
```
which removes items in the trash older than 30 days everyday. Alternatively, you may want to use something like
```
0 * * * * /path/to/trash-cli/trash-empty 30
```
to empty the trash every hour. The `@daily` directive is run by anacron under
the root user by default, which does not empty the user's trash properly.

## License
MIT - see the LICENSE file.
