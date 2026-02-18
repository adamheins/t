#!/usr/bin/env python3
"""A simple CLI tool for removing files safely."""
import argparse
import os
from pathlib import Path
import sys

import colorama
from trashcli.put.main import main as put_main


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


def yellow(s):
    """Color string `s` yellow in the terminal."""
    return colorama.Fore.YELLOW + str(s) + colorama.Fore.RESET


def confirm(prompt):
    """Prompt user for confirmation."""
    ans = input(prompt)
    if len(ans) > 0:
        return ans[0] == "y" or ans[0] == "Y"
    return False


def validate_removal(files, recurse):
    """Returns True if passed files can and should be deleted, False otherwise."""
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
            print(
                f"{f_fmt} is a directory, but {yellow('-r')} flag was not used. Aborting."
            )
            return False

    num_files = len(files)

    # Confirm deleting multiple files.
    if num_files > 1:
        files_fmted = "\n".join([f"  {yellow(f)}" for f in files])
        prompt = f"Multiple items ({yellow(num_files)}) will be removed:\n{files_fmted}\nContinue? [yN] "
    else:
        return True

    if not confirm(prompt):
        print("Aborted.")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        prog="t", description="A simple CLI tool for removing files safely."
    )
    parser.add_argument("files", nargs="+", help="The files and directories to remove.")
    parser.add_argument(
        "-r", "--recurse", action="store_true", help="Recursively remove directories."
    )
    args = parser.parse_args()

    if not validate_removal(files=args.files, recurse=args.recurse):
        return 1

    return put_main()


if __name__ == "__main__":
    sys.exit(main())
