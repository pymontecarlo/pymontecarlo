"""
Common interface to several Monte Carlo codes
"""

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

# Standard library modules.
import os
import sys
import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)

# Third party modules.
import pint

# Local modules.
import pymontecarlo.options
import pymontecarlo.options.analysis
import pymontecarlo.options.detector
import pymontecarlo.options.model
import pymontecarlo.options.program
import pymontecarlo.options.sample
import pymontecarlo.results

# Globals and constants variables.

# --- Units

unit_registry = pint.UnitRegistry()
unit_registry.define("electron = mol")
pint.set_application_registry(unit_registry)

# --- Plug-ins

pymontecarlo_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg in pkgutil.iter_modules()
    if name.startswith("pymontecarlo_")
}

logger.debug("Plug-ins: {}".format(", ".join(pymontecarlo_plugins)))
