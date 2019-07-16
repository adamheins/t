#!/usr/bin/env python3

import datetime
import os
import shutil

import colorama
from docopt import docopt


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
usage: trash [-rf] <files>...

options:
  -f  Delete files forever.
  -r  Recursively remove directories.
'''.strip()

DATE_FMT = '%Y-%m-%d'
TIME_FMT = '%H-%M-%S'
UNIQ_FILENAME_FMT = '{root}__{n}{ext}'


def yellow(s):
    ''' Yellow tty text. '''
    return colorama.Fore.YELLOW + s + colorama.Fore.RESET


def remove_item(item):
    ''' Remove file or directory. '''
    if os.path.isdir(item):
        shutil.rmtree(item)
    else:
        os.remove(item)


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


def make_now_dir():
    ''' Make directories for the trash. '''
    # trash is filed under <TRASH_DIR>/YYYY-MM-DD/HH-MM-SS
    now = datetime.datetime.now()
    date_dir = now.strftime(DATE_FMT)
    time_dir = now.strftime(TIME_FMT)

    path = os.path.join(TRASH_DIR, date_dir, time_dir)
    os.makedirs(path, exist_ok=True)

    return path


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
    args = docopt(HELP_TEXT)

    recurse = args['-r']
    forever = args['-f']
    files = args['<files>']

    # If the user passes -f, confirm intention to delete items forever.
    if forever:
        prompt = '{} flag used; delete forever? [yN] '.format(yellow('-f'))
        if not confirm(prompt):
            print('Aborted.')
            return 1

    # Prompt user for confirmation if multiple items are to be deleted.
    if len(files) > 1:
        n = str(len(files))
        prompt = 'Multiple items ({}) passed for removal. Continue? [yN] '.format(yellow(n))
        if not confirm(prompt):
            print('Aborted.')
            return 1

    # Check for protected directories.
    for f in files:
        if f in PROTECTED_DIRS:
            print('{} is protected. Aborting.'.format(yellow(f)))
            return 1

    for f in files:
        # Use lexists because we also want to be able to delete broken symlinks.
        if not os.path.lexists(f):
            print('Could not find {}. Aborting.'.format(yellow(f)))
            return 1

        # Check for directory (that isn't a symlink) without the recursive flag.
        if os.path.isdir(f) and not os.path.islink(f) and not recurse:
            print('{} is a directory, but {} flag was not used. Aborting.'
                  .format(yellow(f), yellow('-r')))
            return 1

    if forever:
        for f in files:
            remove_item(f)
    else:
        now_dir = make_now_dir()
        remove_old_trash()
        for f in files:
            move_uniq(f, now_dir)

    return 0


if __name__ == '__main__':
    main()
