#!/usr/bin/env python3

import sys
import datetime
import os
from pathlib import Path
import shutil

from docopt import docopt


TRASH_DIR = Path("~/.trash").expanduser()  # where to keep the trash
N_DAYS_TO_KEEP = 7  # number of days of trash to keep

# These directories are not removed.
PROTECTED_DIRS = [
    "/bin",
    "/boot",
    "/dev",
    "/etc",
    "/home",
    "/initrd",
    "/lib",
    "/lib32",
    "/lib64",
    "/proc",
    "/root",
    "/sbin",
    "/sys",
    "/usr",
    "/usr/bin",
    "/usr/include",
    "/usr/lib",
    "/usr/local",
    "/usr/local/bin",
    "/usr/local/include",
    "/usr/local/sbin",
    "/usr/local/share",
    "/usr/sbin",
    "/usr/share",
    "/usr/src",
    "/var",
]

HELP_TEXT = """
usage: trash [-rf] <files>...

options:
  -f  Delete files forever.
  -r  Recursively remove directories.
""".strip()

DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H-%M-%S"
UNIQ_FILENAME_FMT = "{root}__{n}{ext}"


class Color:
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def yellow(s):
    return Color.YELLOW + str(s) + Color.END


def underline(s):
    return Color.UNDERLINE + str(s) + Color.END


def remove_item(item):
    """Remove file or directory."""
    if os.path.isdir(item):
        shutil.rmtree(item)
    else:
        os.remove(item)


def dir_size(path):
    """Calculate size of files in all subdirectories."""
    # See https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    path = Path(path)

    # include the size of the directory itself
    total_size = path.stat().st_size

    for f in path.glob("**/*"):
        if f.is_file() or f.is_dir():
            total_size += f.stat().st_size

    return total_size


def readable_size(size):
    """Return a string representing a human-readable size of bytes."""
    if size < 1e3:
        return "{} bytes".format(size)
    if size < 1e6:
        return "{:.1f}K".format(size / 1e3)
    if size < 1e9:
        return "{:.1f}M".format(size / 1e6)
    return "{:.1f}G".format(size / 1e9)


def confirm(prompt):
    """Prompt user for confirmation."""
    ans = input(prompt)
    if len(ans) > 0:
        return ans[0] == "y" or ans[0] == "Y"
    return False


def uniq_name(filename, dirname):
    """Return a unique name based on `filename` relative to the files in
    directory `dirname`.
    """
    root, ext = os.path.splitext(filename)

    counter = 1
    new_name = filename

    # Increment appended number until name collision goes away.
    while os.path.exists(os.path.join(dirname, new_name)):
        new_name = UNIQ_FILENAME_FMT.format(root=root, ext=ext, n=counter)
        counter += 1
    return new_name


def move_uniq(src, dst):
    """Move src to directory dst, creating a unique name for src so that it is
    unique in dst.
    """
    name = os.path.basename(src)
    name = uniq_name(name, dst)
    dst = os.path.join(dst, name)
    shutil.move(src, dst)


def make_dir_stamped():
    """Make directories for the trash."""
    # trash is filed under <TRASH_DIR>/YYYY-MM-DD/HH-MM-SS
    now = datetime.datetime.now()
    date_dir = now.strftime(DATE_FMT)
    time_dir = now.strftime(TIME_FMT)

    path = TRASH_DIR.joinpath(date_dir, time_dir)
    path.mkdir(exist_ok=True)

    # create a symlink to the most recent trash item
    link_path = TRASH_DIR.joinpath("last")
    if os.path.lexists(link_path):
        link_path.unlink()
    link_path.symlink_to(path)

    return path


def remove_old_trash():
    """Remove old trash that has been around for too long."""
    today = datetime.datetime.now()

    # We use the +1 to round up the delta.
    days_to_keep = datetime.timedelta(days=N_DAYS_TO_KEEP + 1)

    dirs_to_remove = []
    size_to_remove = 0

    found_trash_to_remove = False

    # Find all directories older than N_DAYS_TO_KEEP days (based on the
    # timestamp in their name).
    for d in TRASH_DIR.iterdir():
        try:
            date = datetime.datetime.strptime(d.name, DATE_FMT)
        except ValueError:
            continue
        if date < today - days_to_keep:
            if not found_trash_to_remove:
                print("Removing old trash...", end=" ")
                found_trash_to_remove = True
            path = TRASH_DIR.joinpath(d)
            size = dir_size(path)

            dirs_to_remove.append(path)
            size_to_remove += size

    if len(dirs_to_remove) == 0:
        return

    for path in dirs_to_remove:
        shutil.rmtree(path)

    size_to_remove = readable_size(size_to_remove)
    print(f"done. Removed {size_to_remove}.")


def validate_removal(files, recurse, forever):
    """Returns True if passed files can and should be deleted, False
    otherwise.
    """
    for f in files:
        f_fmt = yellow(f)

        # Check for protected directories.
        if f in PROTECTED_DIRS:
            print(f"{f_fmt} is protected. Aborting.")
            return False

        # To move a file, we need execute and write permissions on the parent
        # directory (no permissions are required on the file itself). Abort if
        # we don't have these permissions.
        fullpath = Path(f).resolve()
        moveable = os.access(fullpath.parent, os.X_OK + os.W_OK)
        if not moveable:
            print(f"Cannot remove {f_fmt}: permission denied. Aborting.")
            return False

        # Use lexists because we also want to be able to delete broken
        # symlinks.
        if not os.path.lexists(f):
            print(f"Could not find {f_fmt}. Aborting.")
            return False

        # Check for directory (that isn't a symlink) without the recursive
        # flag.
        if os.path.isdir(f) and not os.path.islink(f) and not recurse:
            print(f"{f_fmt} is a directory, but {yellow('-r')} flag was not used. Aborting.")
            return False

    num_files = len(files)

    # Confirm deleting multiple files and permanent deletion.
    if num_files > 1 and forever:
        prompt = f"Delete {yellow(num_files)} files {underline('forever')}? [yN]"
    elif num_files > 1:
        prompt = f"Multiple items ({yellow(num_files)}) passed for removal. Continue? [yN] "
    elif forever:
        prompt = "Delete {yellow(files[0])} {underline('forever')}? [yN] "
    else:
        return True

    if not confirm(prompt):
        print("Aborted.")
        return False
    return True


def restore():
    # TODO this is initial, incomplete work to add a restore functionality to
    # removed trash, for ease of use
    last_path = TRASH_DIR.joinpath("last").readlink()
    files = list(last_path.iterdir())
    print(files)


def main():
    # print("hello!")
    args = docopt(HELP_TEXT)

    recurse = args["-r"]
    forever = args["-f"]
    files = args["<files>"]

    if not validate_removal(files, recurse, forever):
        return 1

    if not TRASH_DIR.exists():
        TRASH_DIR.mkdir()

    # TODO we can get an issue where we can move a directory with a nested
    # unremovable file (subdirectory and file it contains both
    # unwriteable), but then we cannot remove it
    try:
        remove_old_trash()
    except PermissionError as e:
        print(e)
        print("There was a problem removing old trash.")

    if forever:
        for f in files:
            remove_item(f)
    else:
        now_dir = make_dir_stamped()
        for f in files:
            # TODO this will fail if the is a non-removable file in a
            # subdirectory
            move_uniq(f, now_dir)

    return 0


if __name__ == "__main__":
    main()
