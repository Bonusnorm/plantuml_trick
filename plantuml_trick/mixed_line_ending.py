# Copyright (c) 2014 pre-commit dev team: Anthony Sottile, Ken Struys
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import collections
from typing import Dict
from typing import Optional
from typing import Sequence


CRLF = b"\r\n"
LF = b"\n"
CR = b"\r"
# Prefer LF to CRLF to CR, but detect CRLF before LF
ALL_ENDINGS = (CR, CRLF, LF)
FIX_TO_LINE_ENDING = {"cr": CR, "crlf": CRLF, "lf": LF}


def _fix(filename, contents, ending):  # type: (str, bytes, bytes) -> None
    new_contents = b"".join(
        line.rstrip(b"\r\n") + ending for line in contents.splitlines(True)
    )
    with open(filename, "wb") as f:
        f.write(new_contents)


def fix_filename(filename, fix):  # type: (str, str) -> int
    with open(filename, "rb") as f:
        contents = f.read()

    counts = collections.defaultdict(int)  # type: Dict[bytes, int]

    for line in contents.splitlines(True):
        for ending in ALL_ENDINGS:
            if line.endswith(ending):
                counts[ending] += 1
                break

    # Some amount of mixed line endings
    mixed = sum(bool(x) for x in counts.values()) > 1

    if fix == "no" or (fix == "auto" and not mixed):
        return mixed

    if fix == "auto":
        max_ending = LF
        max_lines = 0
        # ordering is important here such that lf > crlf > cr
        for ending_type in ALL_ENDINGS:
            # also important, using >= to find a max that prefers the last
            if counts[ending_type] >= max_lines:
                max_ending = ending_type
                max_lines = counts[ending_type]

        _fix(filename, contents, max_ending)
        return 1
    else:
        target_ending = FIX_TO_LINE_ENDING[fix]
        # find if there are lines with *other* endings
        # It's possible there's no line endings of the target type
        counts.pop(target_ending, None)
        other_endings = bool(sum(counts.values()))
        if other_endings:
            _fix(filename, contents, target_ending)
        return other_endings


def main(argv=None):  # type: (Optional[Sequence[str]]) -> int
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--fix",
        choices=("auto", "no") + tuple(FIX_TO_LINE_ENDING),
        default="auto",
        help='Replace line ending with the specified. Default is "auto"',
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to fix")
    args = parser.parse_args(argv)

    retv = 0

    for filename in args.filenames:
        if fix_filename(filename, args.fix):
            if args.fix == "no":
                print("{}: mixed line endings".format(filename))
            else:
                print("{}: fixed mixed line endings".format(filename))
            retv = 1
    return retv


if __name__ == "__main__":
    exit(main())
