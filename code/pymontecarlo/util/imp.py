#!/usr/bin/env python
"""
================================================================================
:mod:`imp` -- Import utilities
================================================================================

.. module:: imp
   :synopsis: Import utilities

.. inheritance-diagram:: pymontecarlo.util.imp

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import pkgutil
from fnmatch import fnmatch

# Third party modules.

# Local modules.

# Globals and constants variables.

def _match(name, includes, excludes):
    if not any(map(lambda pat: fnmatch(name, pat), includes)):
        return False

    if not any(map(lambda pat: fnmatch(name, pat), excludes)):
        return True

    return False

def import_recursive(package, includes=['*'], excludes=[]):
    package_path = package.__path__
    package_name = package.__name__ + '.'

    for _loader, name, _ispkg in pkgutil.walk_packages(package_path, package_name):
        if _match(name, includes, excludes):
            print name
            __import__(name)

