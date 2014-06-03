#!/usr/bin/env python
"""
================================================================================
:mod:`build_exe` -- Build exe command for distutils
================================================================================

.. module:: build_exe
   :synopsis: Build exe command for distutils

.. inheritance-diagram:: pymontecarlo.util.dist.command.build_exe

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
from distutils.file_util import copy_file
from distutils import log

# Third party modules.
from cx_Freeze.dist import build_exe as _build_exe

import pkg_resources

# Local modules.

# Globals and constants variables.

class build_exe(_build_exe):

    def run(self):
        _build_exe.run(self)

        # Add egg info of dependencies
        for dist in pkg_resources.require('pymontecarlo'):
            egg_info_dirpath = dist._provider.egg_info or dist._provider.path
            if egg_info_dirpath is None:
                log.warn('No egg-info found for project %s' % dist.project_name)
                continue

            if os.path.isdir(egg_info_dirpath):
                if os.path.basename(egg_info_dirpath) == 'EGG-INFO':
                    dst = os.path.join(self.build_exe, dist.egg_name() + '.egg-info')
                else:
                    dst = os.path.join(self.build_exe,
                                       os.path.basename(egg_info_dirpath))
                copy_tree(egg_info_dirpath, dst)
            else:
                copy_file(egg_info_dirpath, self.build_exe)