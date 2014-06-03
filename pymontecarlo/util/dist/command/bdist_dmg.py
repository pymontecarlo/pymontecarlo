#!/usr/bin/env python
"""
================================================================================
:mod:`bdist_dmg` -- Build DMG distribution command for distutils
================================================================================

.. module:: bdist_dmg
   :synopsis: DMG distribution command for distutils

.. inheritance-diagram:: pymontecarlo.util.dist.command.bdist_dmg

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.
from cx_Freeze.macdist import bdist_dmg as _bdist_dmg

# Local modules.

# Globals and constants variables.

class bdist_dmg(_bdist_dmg):

    user_options = _bdist_dmg.user_options + \
        [('dist-dir=', 'd',
          "directory to put final built distributions in "
          "[default: dist]"), ]

    def initialize_options(self):
        _bdist_dmg.initialize_options(self)
        self.dist_dir = None

    def finalize_options(self):
        _bdist_dmg.finalize_options(self)

        if self.dist_dir is None:
            self.dist_dir = "dist"

    def buildDMG(self):
        for executable in list(self.distribution.executables):
            self.volume_label = 'pymontecarlo-%s.dmg' % executable.shortcutName
            self.dmgName = os.path.join(self.dist_dir, self.volume_label)
            self.bundleDir = os.path.join(self.dist_dir,
                                          executable.shortcutName + '.app')
            _bdist_dmg.buildDMG(self)