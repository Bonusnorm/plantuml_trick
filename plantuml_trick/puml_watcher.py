#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argh import arg
from argh import dispatch_command
from watchdog.watchmedo import observe_with

from plantuml_trick.compiler import PlantumlTrick


def main():
    @arg("LESS_DIR", help="Directory of less source files")
    @arg("CSS_DIR", help="Directory of generated css files")
    @arg("--lessc-path", default="lessc", help="Path to less compiler.(default: lessc)")
    def _watcher(args):
        "Watch changes in less directory and auto-compile modified file to css"
        from watchdog.observers import Observer

        handler = PlantumlTrick(
            src_dir=args.LESS_DIR, dest_dir=args.CSS_DIR, compiler=args.lessc_path,
        )
        observer = Observer(timeout=1.0)
        observe_with(observer, handler, [args.LESS_DIR], True)

    dispatch_command(_watcher)


if __name__ == "__main__":
    main()
