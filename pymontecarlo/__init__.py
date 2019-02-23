"""
Common interface to several Monte Carlo codes
"""

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Standard library modules.
import os
import sys
import importlib
import pkgutil

# Third party modules.
import pint

# Local modules.

# Globals and constants variables.

#--- Units

unit_registry = pint.UnitRegistry()
unit_registry.define('electron = mol')
pint.set_application_registry(unit_registry)

#--- Plug-ins

pymontecarlo_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('pymontecarlo_')
}