#!/usr/bin/env python
"""
================================================================================
:mod:`pymontecarlo` -- Common interface to several Monte Carlo codes
================================================================================

.. module:: pymontecarlo
   :synopsis: Common interface to several Monte Carlo codes

.. inheritance-diagram:: pymontecarlo

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import logging

# Third party modules.
from pkg_resources import resource_string #@UnresolvedImport

# Local modules.
from pymontecarlo.util.config import ConfigReader
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

settings = ConfigReader()

def __load_settings():
    filepaths = []
    filepaths.append(os.path.join(os.path.expanduser('~'), '.pymontecarlo',
                                  'settings.cfg'))
    filepaths.append(os.path.join(os.path.dirname(__file__), 'settings.cfg'))

    for filepath in filepaths:
        if os.path.exists(filepath):
            logging.debug('Loading settings from: %s', filepath)

            with open(filepath, 'r') as f:
                settings.read(f)

            break

__load_settings()

XMLIO.add_namespace('mc', 'http://pymontecarlo.sf.net',
                    source=resource_string(__name__, 'schema.xsd'))
