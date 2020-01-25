#!/usr/bin/env python
import fnmatch
import os
import re
from contextlib import suppress
from functools import reduce
from typing import Dict
from typing import List

import docker
from watchdog.tricks import Trick

from plantuml_trick import utils

default_compile_opts = ["-tsvg", "-failfast2", "-charset utf-8", "-pipe"]

opt_to_ext_map: Dict[str, str] = {
    "-teps": "eps",
    "-thtml": "html",
    "-tlatex": "latex",
    "-tlatex:nopreamble": "latex",
    "-tpdf": "pdf",
    "-tpng": "png",
    "-tscxml": "xml",
    "-tsvg": "svg",
    "-ttxt": "txt",
    "-tutxt": "txt",
    "-tvdx": "vdx",
    "-txmi": "xmi",
}


class AutoCompileTrick(Trick):
    def __init__(self, src_dir, dest_dir, **kwargs):
        self.src_dir = os.path.abspath(src_dir)
        self.dest_dir = os.path.abspath(dest_dir)
        self.dest_ext = kwargs.pop("dest_ext")
        self.docker_image = kwargs.pop("docker_image", None)
        self.compile_opts = kwargs.pop("compile_opts", [])
        self.dest_ext_initial = self.dest_ext

        super(AutoCompileTrick, self).__init__(**kwargs)

    @utils.trace_event
    def on_modified(self, event):
        self.compile(event.src_path)

    @utils.trace_event
    def on_deleted(self, event):
        self.remove(event.src_path)

    @utils.trace_event
    def on_created(self, event):
        self.compile(event.src_path)

    @utils.trace_event
    def on_moved(self, event):
        is_pattern_match = any(
            fnmatch.fnmatch(event.dest_path, elem) for elem in self.patterns
        )
        self.remove(event.src_path)
        is_in_scope = os.path.abspath(event.dest_path).startswith(self.src_dir)

        if is_pattern_match and is_in_scope:
            self.compile(event.dest_path)

    def get_altered_dest_ext(self, src_path):
        return ".{}.{}".format(src_path.rsplit(".", 1).pop(), self.dest_ext)

    def get_dest_fname(self, src_fname):
        # TODO; refactor and test with nested directories
        return (
            src_fname.replace(self.src_dir, self.dest_dir).rsplit(".", 1)[0]
            + "."
            + self.dest_ext
        )

    def compile(self, src_path):
        client = docker.from_env()
        context = self.src_dir
        cmd = " ".join([*self.compile_opts, src_path])
        print("Compiling {}".format(src_path))

        result = client.containers.run(
            image=self.docker_image,
            stderr=True,
            stdout=True,
            stdin_open=True,
            working_dir="/work",
            tty=True,
            volumes={context: {"bind": "/work", "mode": "rw"}},
            command=cmd,
        )

        print(result)

        # TODO insert suffix
        # suffix = self.get_altered_dest_ext(src_path)
        # print(suffix)

    def remove(self, filename):
        with suppress(FileNotFoundError):
            dest_file = os.path.normpath(
                os.path.join(
                    os.path.abspath(self.dest_dir), self.get_dest_fname(filename),
                ),
            )
            print("Removing {}".format(dest_file))
            os.remove(dest_file)


def ext_from_opts(opts=None):
    if opts is None:
        opts = default_compile_opts
    param = set(opts).intersection(set(opt_to_ext_map.keys())).pop()
    return opt_to_ext_map[param]


class PlantumlTrick(AutoCompileTrick):
    def __init__(
        self,
        src_dir: str = ".",
        patterns: List[str] = None,
        docker_image: str = "miy4/plantuml",
        compile_opts=None,
    ):
        opt_regex = r"(?<=-o )\S+$|(?<=-output )\S+$"

        def filter_out_dir(opt):
            return re.search(opt_regex, opt)

        out_opt = list(filter(filter_out_dir, compile_opts))

        dest_dir = src_dir
        if out_opt:
            possibly_found = re.search(opt_regex, out_opt.pop())
            if possibly_found:
                dest_dir = possibly_found.group(0)

        super(PlantumlTrick, self).__init__(
            src_dir=src_dir,
            dest_dir=dest_dir,
            dest_ext=ext_from_opts(compile_opts),
            patterns=(patterns or ["*.puml", "*.plantuml"]),
            docker_image=docker_image,
            compile_opts=(compile_opts or default_compile_opts),
        )
