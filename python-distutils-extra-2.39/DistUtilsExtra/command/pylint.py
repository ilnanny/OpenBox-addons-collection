# DistUtilsExtra.command.pylint - DistUtilsExtra command to call pylint
#
# Author: Rodney Dawes <rodney.dawes@canonical.com>
# Copyright 2009 Canonical Ltd.

"""DistUtilsExtra.command.pylint

Implements the DistUtilsExtra 'pylint' command.
"""

import os
import subprocess

from distutils.core import Command


class pylint (Command):
    """Command to run pylint and tests on a module."""

    description = "integrate pylint checks"

    user_options = [("config-file=", None,
                     "pylint config file to use"),
                    ("exclude-files=", None,
                     "list of files to exclude from lint checks"),
                    ("lint-files=", None,
                     "list of modules or packages to run lint checks on")
                   ]

    def initialize_options (self):
        self.config_file = None
        self.exclude_files = None
        self.lint_files = None

    def finalize_options (self):
        if self.config_file is None:
            self.config_file = ""
        if self.exclude_files is None:
            self.exclude_files = "[]"
        if self.lint_files is None:
            self.lint_files = "[" + self.__find_files() + "]"

    def run (self):
        pylint_args = ["--output-format=parseable",
                       "--include-ids=yes"]

        if self.config_file:
            pylint_args.append("--rcfile=" + self.config_file)

        for file in eval(self.lint_files):
            pylint_args.append(file)

        p = subprocess.Popen(["pylint"] + pylint_args,
                             bufsize=4096, stdout=subprocess.PIPE)
        notices = p.stdout

        output = "".join(notices.readlines())
        if output != "":
            print("== Pylint notices ==")
            print(self.__group_lines_by_file(output))

    def __group_lines_by_file(self, input):
        """Format file:line:message output as lines grouped by file."""
        outputs = []
        filename = ""
        excludes = eval(self.exclude_files)
        for line in input.splitlines():
            current = line.split(":", 3)
            if line.startswith("    "):
                outputs.append("    " + current[0] + "")
            elif line.startswith("build/") or current[0] in excludes or \
                    len(current) < 3:
                pass
            elif filename == current[0]:
                outputs.append("    " + current[1] + ": " + current[2])
            elif filename != current[0]:
                filename = current[0]
                outputs.append("")
                outputs.append(filename + ":")
                outputs.append("    " + current[1] + ": " + current[2])

        return "\n".join(outputs)

    def __find_files(self):
        """Find all Python files under the current tree."""
        pyfiles = []
        for root, dirs, files in os.walk(os.getcwd(), topdown=False):
            for file in files:
                if file.endswith(".py"):
                    pyfiles.append("'" + os.path.join(root, file) + "'")
        pyfiles.sort()
        return ",".join(pyfiles)
