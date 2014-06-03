#!/usr/bin/env python
"""
================================================================================
:mod:`clean` -- Clean command for distutils
================================================================================

.. module:: clean
   :synopsis: Clean command for distutils

.. inheritance-diagram:: pymontecarlo.util.dist.comman.clean

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from fnmatch import filter as fnfilter
from distutils.command.clean import clean as _clean
from distutils.dir_util import remove_tree
from distutils import log

# Third party modules.

# Local modules.

# Globals and constants variables.

class clean(_clean):

    user_options = _clean.user_options + \
        [('purge', 'p', "remove all build and dist output"),
         ('build-exe=', 'b',
         'directory for built executables'), ]
    boolean_options = _clean.boolean_options + ['purge']

    def initialize_options(self):
        _clean.initialize_options(self)

        self.purge = None
        self.build_exe = None
        self.dist_dir = None

    def finalize_options(self):
        _clean.finalize_options(self)

        self.set_undefined_options('bdist',
                                   ('dist_dir', 'dist_dir'))
        self.set_undefined_options('build_exe',
                                   ('build_exe', 'build_exe'))

        if self.purge:
            self.all = True

    def run(self):
        _clean.run(self)

        # Remove egg-info directory
        if self.all:
            dirs = self.distribution.package_dir
            egg_basedir = (dirs or {}).get('', os.curdir)

            for egg_infodir in fnfilter(os.listdir(egg_basedir), '*.egg-info'):
                if os.path.exists(egg_infodir):
                    remove_tree(egg_infodir, dry_run=self.dry_run)
                else:
                    log.warn("'%s' does not exist -- can't clean it", egg_infodir)

        # Remove build directories
        if self.all:
            for directory in (self.build_exe,):
                if os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.warn("'%s' does not exist -- can't clean it",
                             directory)

        # Purge
        if self.purge:
            if os.path.exists(self.dist_dir):
                remove_tree(self.dist_dir, dry_run=self.dry_run)
            else:
                log.warn("'%s' does not exist -- can't clean it", self.dist_dir)

