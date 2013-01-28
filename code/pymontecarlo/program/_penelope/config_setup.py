#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- PENELOPE Monte Carlo setup configuration
================================================================================

.. module:: config_setup
   :synopsis: PENELOPE Monte Carlo setup configuration

.. inheritance-diagram:: pymontecarlo.program._penelope.config_setup

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from distutils.core import Extension
from distutils.command.build_ext import build_ext as _build_ext

# Third party modules.

# Local modules.
from pymontecarlo.program.config_setup import Setup

import penelopelib

# Globals and constants variables.

class _PenelopeSetup(Setup):

    def __init__(self, packages=None, py_modules=None, package_dir=None,
                 package_data=None, ext_modules=None, cmdclass=None):
        if packages is None: packages = []
        packages += ['pymontecarlo.program._penelope',
                     'pymontecarlo.program._penelope.input',
                     'pymontecarlo.program._penelope.io',
                     'penelopelib']

        if package_dir is None: package_dir = {}
        package_dir.update({'penelopelib': os.path.dirname(penelopelib.__file__)})

        basedir = os.path.join(os.path.dirname(penelopelib.__file__), '..', '..')
        fsource_dir = os.path.abspath(os.path.join(basedir, 'fsource'))
        csource_dir = os.path.abspath(os.path.join(basedir, 'csource'))
        include_dir = os.path.abspath(os.path.join(basedir, 'include'))

        material_ext = Extension('penelopelib._material',
                                 sources=[os.path.join(fsource_dir, 'penelope.f'),
                                          os.path.join(fsource_dir, 'rita.f'),
                                          os.path.join(fsource_dir, 'penvared.f'),
                                          os.path.join(fsource_dir, 'timer.f'),
                                          os.path.join(fsource_dir, 'utils.f'),
                                          os.path.join(csource_dir, 'cmaterial.c'),
                                          os.path.join(csource_dir, 'cutils.c')],
                                 include_dirs=[include_dir])

        pengeom_ext = Extension('penelopelib._pengeom',
                                sources=[os.path.join(fsource_dir, 'pengeom.f'),
                                         os.path.join(fsource_dir, 'utils.f'),
                                         os.path.join(csource_dir, 'cpengeom.c'),
                                         os.path.join(csource_dir, 'cutils.c')],
                                include_dirs=[include_dir])

        penelope_ext = Extension('penelopelib._penelope',
                                 sources=[os.path.join(fsource_dir, 'penelope.f'),
                                          os.path.join(fsource_dir, 'utils.f'),
                                          os.path.join(fsource_dir, 'timer.f'),
                                          os.path.join(fsource_dir, 'rita.f'),
                                          os.path.join(csource_dir, 'cpenelope.c'),
                                          os.path.join(csource_dir, 'cutils.c')],
                                 include_dirs=[include_dir])

        if ext_modules is None: ext_modules = []
        ext_modules += [material_ext, pengeom_ext, penelope_ext]

        class build_ext(_build_ext):
            def build_extension(self, ext):
                self.compiler.src_extensions.append('.f')
                self.compiler.linker_so[0] = 'gfortran'
                self.compiler.linker_exe[0] = 'gfortran'

                _build_ext.build_extension(self, ext)

        if cmdclass is None: cmdclass = {}
        cmdclass.update({'build_ext': build_ext})

        Setup.__init__(self, packages, py_modules, package_dir, package_data,
                       ext_modules, cmdclass)

setup = _PenelopeSetup()
