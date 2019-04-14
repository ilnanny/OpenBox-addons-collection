import distutils
import glob
import os
import os.path
import re
import sys
import distutils.command.build

class build_extra(distutils.command.build.build):
    """Adds the extra commands to the build target. This class should be used
       with the core distutils"""
    def __init__(self, dist):
        distutils.command.build.build.__init__(self, dist)

        self.user_options.extend([("i18n", None, "use the localisation"),
                                  ("icons", None, "use icons"),
                                  ("kdeui", None, "use kdeui"),
                                  ("help", None, "use help system")])
    def initialize_options(self):
        distutils.command.build.build.initialize_options(self)
        self.i18n = False
        self.icons = False
        self.help = False
        self.kdeui = False

    def finalize_options(self):
        def has_help(command):
            return self.help == "True" or \
                   ("build_help" in self.distribution.cmdclass and not \
                    self.help == "False")
        def has_icons(command):
            return self.icons == "True" or \
                   ("build_icons" in self.distribution.cmdclass and not \
                    self.help == "False")
        def has_i18n(command):
            return self.i18n == "True" or \
                   ("build_i18n" in self.distribution.cmdclass and not \
                    self.i18n == "False")
        def has_kdeui(command):
            return self.kdeui == "True" or \
                   ("build_kdeui" in self.distribution.cmdclass and not \
                    self.kdeui == "False")

        distutils.command.build.build.finalize_options(self)
        self.sub_commands.append(("build_i18n", has_i18n))
        self.sub_commands.append(("build_icons", has_icons))
        self.sub_commands.append(("build_help", has_help))
        self.sub_commands.insert(0, ("build_kdeui", has_kdeui)) # need to run before build_py

class build(build_extra):
    """Adds the extra commands to the build target. This class should be
       used with setuptools."""
    def finalize_options(self):
        def has_help(command):
            return self.help == "True"
        def has_icons(command):
            return self.icons == "True"
        def has_i18n(command):
            return self.i18n == "True"
        def has_kdeui(command):
            return self.kdeui == "True"
        distutils.command.build.build.finalize_options(self)
        self.sub_commands.append(("build_i18n", has_i18n))
        self.sub_commands.append(("build_icons", has_icons))
        self.sub_commands.append(("build_help", has_help))
        self.sub_commands.insert(0, ("build_kdeui", has_kdeui)) # need to run before build_py
