#!/usr/bin/env python
import fnmatch
import os
from contextlib import suppress

from watchdog.tricks import Trick

from plantuml_trick import utils


class CompileTrick(Trick):
    def __init__(self, src_dir, dest_dir, **kwargs):
        self.src_dir = os.path.abspath(src_dir)
        self.dest_dir = dest_dir
        self.dest_ext = kwargs.pop("dest_ext")
        self.insert_infix = kwargs.pop("insert_infix")
        self.conjunction_removal = kwargs.pop("conjunction_removal")
        self.docker_image = kwargs.pop("docker_image", None)
        self.compile_opts = kwargs.pop("compile_opts", [])
        self.postprocessor = kwargs.pop("postprocessor", False)
        super(CompileTrick, self).__init__(**kwargs)

    def get_altered_dest_ext(self, src_path):
        return "{}.{}".format(src_path.rsplit(".", 1).pop(), self.dest_ext)

    def get_altered_dest_fname(self, src_fname):
        if not self.insert_infix:
            return self.get_dest_fname(src_fname)

        base_dir, file = os.path.split(src_fname)
        dest_dir = os.path.join(base_dir, self.dest_dir)
        dest_file = "{}.{}".format(file, self.dest_ext)
        return os.path.join(dest_dir, dest_file)

    def get_dest_fname(self, src_fname):
        base_dir, file = os.path.split(src_fname)
        dest_dir = os.path.join(base_dir, self.dest_dir)
        root, _ = os.path.splitext(file)
        return os.path.join(dest_dir, "{}.{}".format(root, self.dest_ext))

    def remove(self, src_path):
        if self.conjunction_removal:
            with suppress(FileNotFoundError):
                dest_file = self.get_altered_dest_fname(src_path)
                base_dir, _ = os.path.split(dest_file)
                print("Removing {}".format(dest_file))
                os.remove(dest_file)
                if not os.listdir(base_dir):
                    with suppress(OSError):
                        os.rmdir(base_dir)


class AutoCompileBaseTrick(CompileTrick):
    def compile(self, _):
        return self

    def __init__(self, **kwargs):
        super(AutoCompileBaseTrick, self).__init__(**kwargs)

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
