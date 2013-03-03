#!/usr/bin/env python
"""
================================================================================
:mod:`command` -- Special command for distutils
================================================================================

.. module:: command
   :synopsis: Special command for distutils

.. inheritance-diagram:: pymontecarlo.util.dist.command

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from fnmatch import filter as fnfilter
from distutils.command.clean import clean as _clean
from distutils.dir_util import remove_tree
from distutils import log

# Third party modules.
from setuptools.command.build_py import build_py as _build_py

# Local modules.

# Globals and constants variables.

class build_py(_build_py):

    def build_packages(self):
        _build_py.build_packages(self)

        # Add missing __init__.py
        for package in self.packages:
            subpackages = package.split('.')

            packagedir = self.build_lib
            for subpackage in subpackages:
                packagedir = os.path.join(packagedir, subpackage)
                init_filepath = os.path.join(packagedir, '__init__.py')

                if not os.path.exists(init_filepath):
                    print 'creating missing %s' % init_filepath
                    open(init_filepath, 'w').close()

class clean(_clean):

    user_options = _clean.user_options + \
        [('purge', 'p', "remove all build and dist output")]

    boolean_options = _clean.boolean_options + ['purge']

    def initialize_options(self):
        _clean.initialize_options(self)

        self.purge = None
        self.dist_dir = None

    def finalize_options(self):
        _clean.finalize_options(self)

        self.set_undefined_options('bdist',
                                   ('dist_dir', 'dist_dir'))

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

        # Purge
        if self.purge:
            if os.path.exists(self.dist_dir):
                remove_tree(self.dist_dir, dry_run=self.dry_run)
            else:
                log.warn("'%s' does not exist -- can't clean it", self.dist_dir)
