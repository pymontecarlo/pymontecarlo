"""
================================================================================
:mod:`result` -- Load and save results for a simulation
================================================================================

.. module:: result
   :synopsis: Load and save results for a simulation

.. inheritance-diagram:: pymontecarlo.result

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
    Imports all ``result`` modules inside ``pymontecarlo.result``
    """
    package_path = __path__
    package_name = 'pymontecarlo.result'
    includes = ['pymontecarlo.result.*.result']
    import_recursive(package_path, package_name, includes)

_init()
