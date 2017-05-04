"""
Common interface to several Monte Carlo codes
"""

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Standard library modules.
import os
import sys

# Third party modules.

# Local modules.

# Globals and constants variables.

#--- Units

import pint

unit_registry = pint.UnitRegistry()
unit_registry.define('electron = mol')
pint.set_application_registry(unit_registry)

#--- Settings

from pymontecarlo._settings import Settings

try:
    settings = Settings.read()
except:
    settings = Settings()
