#!/usr/bin/env python
"""
================================================================================
:mod:`bdist_mac` -- Build mac distribution command for distutils
================================================================================

.. module:: bdist_mac
   :synopsis: Build mac distribution command for distutils

.. inheritance-diagram:: pymontecarlo.util.dist.command.bdist_mac

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from distutils.dir_util import copy_tree

# Third party modules.
from cx_Freeze.macdist import bdist_mac as _bdist_mac

# Local modules.

# Globals and constants variables.

class bdist_mac(_bdist_mac):

    user_options = _bdist_mac.user_options + \
        [('dist-dir=', 'd',
          "directory to put final built distributions in "
          "[default: dist]"), ]

    def initialize_options(self):
        _bdist_mac.initialize_options(self)
        self.dist_dir = None

    def finalize_options(self):
        _bdist_mac.finalize_options(self)

        if self.dist_dir is None:
            self.dist_dir = "dist"

    def run(self):
        # Modify to run on all executables
        for executable in list(self.distribution.executables):
            self.distribution.executables.remove(executable)
            self.distribution.executables.insert(0, executable)

            _bdist_mac.run(self)

            copy_tree(self.bundleDir,
                      os.path.join(self.dist_dir, executable.shortcutName + '.app'))