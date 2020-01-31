#!/usr/bin/env python
from __future__ import absolute_import

import argparse
import sys

from watchdog import watchmedo

from .plantuml import PlantumlTrick

TRICKS_REF = "tricks"
PLANTUML_REF = "plantuml_trick.plantuml.PlantumlTrick"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="tricks.yaml", help="Path to tricks config",
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to compile")
    args = parser.parse_args(argv)

    conf = watchmedo.load_config(args.config)

    options = list(filter(lambda x: x.get(PLANTUML_REF), conf.get(TRICKS_REF)))

    retv = 0

    if not options:
        raise ValueError(
            "Improper --config provided. Did you define '{}' settings?"
            - format(PLANTUML_REF),
        )

    for opts in options:
        trick = PlantumlTrick(**opts.get(PLANTUML_REF))
        for filename in args.filenames:
            trick.compile(filename)

    return retv


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
