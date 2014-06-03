#!/usr/bin/env python
"""
================================================================================
:mod:`bdist_exe` -- Build exe distribution command for distutils
================================================================================

.. module:: bdist_exe
   :synopsis: Build exe distribution command for distutils

.. inheritance-diagram:: pymontecarlo.util.dist.command.bdist_exe

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import platform
from distutils.core import Command
from distutils.archive_util import make_archive

# Third party modules.

# Local modules.

# Globals and constants variables.

class bdist_exe(Command):

    user_options = [('dist-dir=', 'd',
                     "directory to put final built distributions in "
                     "[default: dist]"), ]

    def initialize_options(self):
        self.dist_dir = None

    def finalize_options(self):
        if self.dist_dir is None:
            self.dist_dir = "dist"

    def run(self):
        self.run_command('build_exe')

        build_dir = self.get_finalized_command("build_exe").build_exe
        base_name = os.path.join(self.dist_dir,
                                 "pymontecarlo-%s" % platform.machine())
        make_archive(base_name, 'zip', build_dir)