#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- Base setup configuration
================================================================================

.. module:: config_setup
   :synopsis: Base setup configuration

.. inheritance-diagram:: pymontecarlo.program.config_setup

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class Setup(object):
    
    def __init__(self, packages=None, py_modules=None, package_dir=None, 
                 package_data=None, ext_modules=None, cmdclass=None):
        """
        Creates a new setup configuration for a program.
        """
        self._packages = packages if packages is not None else []
        self._py_modules = py_modules if py_modules is not None else []
        self._package_dir = package_dir if package_dir is not None else {}
        self._package_data = package_data if package_data is not None else {}
        self._ext_modules = ext_modules if ext_modules is not None else []
        self._cmdclass = cmdclass if cmdclass is not None else {}

    @property
    def packages(self):
        return self._packages

    @property
    def py_modules(self):
        return self._py_modules

    @property
    def package_dir(self):
        return self._package_dir

    @property
    def package_data(self):
        return self._package_data

    @property
    def ext_modules(self):
        return self._ext_modules

    @property
    def cmdclass(self):
        return self._cmdclass
