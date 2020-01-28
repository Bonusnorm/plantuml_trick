import os
import re
from contextlib import suppress
from typing import Dict
from typing import List

import docker

from plantuml_trick.compiler import AutoCompileBaseTrick
from plantuml_trick.mixed_line_ending import main as mixed_line_ending
from plantuml_trick.svgo import SVGOTrick

default_compile_opts = ["-tsvg", "-failfast2", "-charset utf-8"]

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


def get_ext_from_opts(opts=None):
    if opts is None:
        opts = default_compile_opts
    param = set(opts).intersection(set(opt_to_ext_map.keys())).pop()
    return opt_to_ext_map[param]


class PlantumlTrick(AutoCompileBaseTrick):
    def __init__(
        self,
        src_dir: str = os.getcwd(),
        patterns: List[str] = None,
        insert_infix=True,
        conjunction_removal=True,
        docker_image: str = "miy4/plantuml",
        compile_opts=None,
        dest_ext=None,
        postprocess={},
    ):
        opt_regex = r"(?<=-o )\S+$|(?<=-output )\S+$"

        def filter_out_dir(opt):
            return re.search(opt_regex, opt)

        out_opt = list(filter(filter_out_dir, (compile_opts or default_compile_opts)))

        dest_dir = src_dir
        if out_opt:
            possibly_found = re.search(opt_regex, out_opt.pop())
            if possibly_found:
                dest_dir = possibly_found.group(0)

        self.ext_from_opts = get_ext_from_opts(compile_opts or default_compile_opts)

        self.postprocess_opts = (
            postprocess.get(self.ext_from_opts) if postprocess else None
        )

        self.postprocess = postprocess
        self.context_path = os.path.abspath(src_dir)

        super(PlantumlTrick, self).__init__(
            src_dir=src_dir,
            insert_infix=insert_infix,
            conjunction_removal=conjunction_removal,
            dest_dir=dest_dir,
            dest_ext=(dest_ext or self.ext_from_opts),
            patterns=(patterns or ["*.puml", "*.plantuml"]),
            docker_image=docker_image,
            compile_opts=(compile_opts or default_compile_opts),
        )

    def compile(self, src_path):
        client = docker.from_env()
        context = self.context_path
        relative_path = os.path.relpath(src_path, self.context_path)
        cmd = " ".join([*self.compile_opts, relative_path])
        print("Compiling {}".format(os.path.normpath(relative_path)))

        client.containers.run(
            image=self.docker_image,
            stderr=True,
            stdout=True,
            stdin_open=True,
            working_dir="/work",
            tty=True,
            volumes={context: {"bind": "/work", "mode": "rw"}},
            command=cmd,
        )

        former = self.get_dest_fname(src_path)
        new = self.get_altered_dest_fname(src_path)

        if self.insert_infix:
            with suppress(FileNotFoundError):
                print("Moving: {} -> {}".format(former, new))
                os.replace(former, new)

        if self.postprocess.get("mixed_line_ending"):
            mixed_line_ending([*self.postprocess.get("mixed_line_ending"), new])

        if self.postprocess_opts and self.postprocess_opts.get("compile_opts"):
            if self.ext_from_opts == "svg":
                print("SVGOTrick on {}".format(new))
                self.postprocessor = SVGOTrick(
                    compile_opts=self.postprocess_opts.get("compile_opts"),
                    docker_image=self.postprocess_opts.get("docker_image"),
                    src_dir=self.src_dir,
                ).compile(new)
