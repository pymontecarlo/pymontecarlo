"""
================================================================================
:mod:`input` -- Setup, load and save inputs for a simulation
================================================================================

.. module:: input
   :synopsis: Setup, load and save inputs for a simulation

.. inheritance-diagram:: pymontecarlo.input

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.imp import import_recursive

# Globals and constants variables.


def _init():
    """
    Imports all packages and modules inside ``pymontecarlo.input`` except
    the current module, unit tests and converters.
    """
    package_path = __path__
    package_name = 'pymontecarlo.input'
    includes = ['*']
    excludes = ['*.test_*', '*.converter']
    import_recursive(package_path, package_name, includes, excludes)

_init()
