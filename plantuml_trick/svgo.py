from __future__ import absolute_import

import docker
from compiler import CompileTrick

# https://github.com/svg/svgo/issues/439#issuecomment-147253790
default_compile_opts = ["--pretty", "--indent=2"]


class SVGOTrick(CompileTrick):
    def __init__(
        self,
        src_dir: str = ".",
        docker_image: str = "thorisalaptop/svgo",
        compile_opts=None,
    ):
        super(SVGOTrick, self).__init__(
            src_dir=src_dir,
            dest_dir=src_dir,
            docker_image=docker_image,
            compile_opts=(compile_opts or default_compile_opts),
            insert_infix=False,
            conjunction_removal=False,
            dest_ext=".svg",
        )

    def compile(self, src_path):
        client = docker.from_env()
        context = self.src_dir
        cmd = " ".join([*self.compile_opts, src_path])
        print("Compiling {}".format(src_path))

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
