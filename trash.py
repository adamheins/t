#!/usr/bin/env python3

import datetime
import os
import shutil
import sys

import colorama


TRASH_DIR = os.path.expanduser('~/.trash')
N_DAYS_TO_KEEP = 7

# These directories are not removed.
PROTECTED_DIRS = ['/bin', '/boot', '/dev', '/etc', '/home', '/initrd', '/lib',
                  '/lib32', '/lib64', '/proc', '/root', '/sbin', '/sys',
                  '/usr', '/usr/bin', '/usr/include', '/usr/lib', '/usr/local',
                  '/usr/local/bin', '/usr/local/include', '/usr/local/sbin',
                  '/usr/local/share', '/usr/sbin', '/usr/share', '/usr/src',
                  '/var']

HELP_TEXT = '''
usage: trash [-r] file1 [file2...]

options:
  -r  Recursively remove directories.
'''.strip()

DATE_FMT = '%Y-%m-%d'
UNIQ_FILENAME_FMT = '{root}__{n}{ext}'


def yellow(s):
    ''' Yellow tty text. '''
    return colorama.Fore.YELLOW + s + colorama.Fore.RESET


def confirm(prompt):
    ''' Prompt user for confirmation. '''
    ans = input(prompt)
    if len(ans) > 0:
        return ans[0] == 'y' or ans[0] == 'Y'
    return False


def uniq_name(filename, dirname):
    ''' Return a unique name based on `filename` relative to the files in
        directory `dirname`. '''
    root, ext = os.path.splitext(filename)

    counter = 1
    new_name = filename

    # Increment appended number until name collision goes away.
    while os.path.exists(os.path.join(dirname, new_name)):
        new_name = UNIQ_FILENAME_FMT.format(root=root, ext=ext, n=counter)
        counter += 1
    return new_name


def move_uniq(src, dst):
    ''' Move src to directory dst, creating a unique name for src so that it is
        unique in dst. '''
    name = os.path.basename(src)
    name = uniq_name(name, dst)
    dst = os.path.join(dst, name)
    shutil.move(src, dst)


def make_today_dir():
    ''' Make directories for today's trash. '''
    # Create trash directory if it doesn't exist.
    if not os.path.exists(TRASH_DIR):
        os.mkdir(TRASH_DIR)

    # Make today's trash directory.
    today = datetime.datetime.now()
    today_dir = os.path.join(TRASH_DIR, today.strftime(DATE_FMT))
    if not os.path.exists(today_dir):
        os.mkdir(today_dir)

    return today_dir


def remove_old_trash():
    ''' Remove old trash that has been around for too long. '''
    dirs = os.listdir(TRASH_DIR)
    today = datetime.datetime.now()

    # We use the +1 to round up the delta.
    days_to_keep = datetime.timedelta(days=N_DAYS_TO_KEEP+1)

    for d in dirs:
        try:
            date = datetime.datetime.strptime(d, DATE_FMT)
        except ValueError:
            continue
        if date < today - days_to_keep:
            shutil.rmtree(os.path.join(TRASH_DIR, d))


def main():
    args = sys.argv[1:]
    recurse = False

    # Check for recursive flag.
    if len(args) > 0 and args[0] == '-r':
        recurse = True
        args = args[1:]

    if len(args) == 0:
        print(HELP_TEXT)
        return 1

    # Prompt user for confirmation if multiple items are to be deleted.
    if len(args) > 1:
        n = str(len(args))
        prompt = 'Multiple items ({}) passed for removal. Continue? [yN] '.format(yellow(n))
        if not confirm(prompt):
            print('Aborted.')
            return 1

    # Check for protected directories.
    for arg in args:
        if arg in PROTECTED_DIRS:
            print('{} is protected. Aborting.'.format(yellow(arg)))
            return 1

    for arg in args:
        # Use lexists because we also want to be able to delete broken symlinks.
        if not os.path.lexists(arg):
            print('Could not find {}. Aborting.'.format(yellow(arg)))
            return 1

        # Check for directory (that isn't a symlink) without the recursive flag.
        if os.path.isdir(arg) and not os.path.islink(arg) and not recurse:
            print('{} is a directory, but {} flag was not used. Aborting.'
                  .format(yellow(arg), yellow('-r')))
            return 1

    today_dir = make_today_dir()
    remove_old_trash()

    for arg in args:
        move_uniq(arg, today_dir)

    return 0


if __name__ == '__main__':
    main()
