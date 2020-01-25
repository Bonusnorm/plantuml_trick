#!/usr/bin/env python
import os
from string import Template
from typing import Dict
from typing import List

from watchdog.tricks import Trick

from plantuml_trick import utils

default_compile_opts = ["-tsvg", "-failfast2"]

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
        self.docker_image = kwargs.pop("docker_image")
        self.compile_opts = kwargs.pop("compile_opts", "")

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
        self.remove(event.src_path)
        if event.dest_path.endswith(self.src_ext) and event.dest_path.startswith(
            self.src_dir,
        ):
            self.compile(event.dest_path)

    def get_dest_fname(self, src_fname):
        return (
            src_fname.replace(self.src_dir, self.dest_dir).rsplit(".", 1)[0]
            + "."
            + self.dest_ext
        )

    def compile(self, filename):
        print(self.get_dest_fname(filename))

        # utils.exec_cmd(
        #     self.assemble_compile_cmdline(filename, self.get_dest_fname(filename)),
        # )

    # def assemble_compile_cmdline(self, src, dst):
    #     return Template(self.compile_command).substitute(
    #         {"src": src, "dst": dst, "opts": self.compile_opts},
    #     )

    def remove(self, filename):
        utils.exec_cmd("rm " + self.get_dest_fname(filename))


def ext_from_opts(opts=None):
    if opts is None:
        opts = default_compile_opts
    param = set(opts).intersection(set(opt_to_ext_map.keys())).pop()
    return opt_to_ext_map[param]


class PlantumlTrick(AutoCompileTrick):
    def __init__(
        self,
        src_dir: str = ".",
        dest_dir: str = ".",
        patterns: List[str] = None,
        docker_image: str = "miy4/plantuml",
        compile_opts=None,
    ):
        super(PlantumlTrick, self).__init__(
            src_dir=src_dir,
            dest_dir=dest_dir,
            dest_ext=ext_from_opts(compile_opts),
            patterns=(patterns or ["*.puml", "*.plantuml"]),
            docker_image=docker_image,
            compile_opts=(compile_opts or default_compile_opts),
        )
