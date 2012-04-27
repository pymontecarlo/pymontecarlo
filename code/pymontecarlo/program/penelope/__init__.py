#!/usr/bin/env python
"""
================================================================================
:mod:`penelope` -- PENELOPE Monte Carlo program
================================================================================

.. module:: penelope
   :synopsis: PENELOPE Monte Carlo program

.. inheritance-diagram:: pymontecarlo.program.penelope

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from pkg_resources import resource_filename #@UnresolvedImport

# Local modules.

# Globals and constants variables.
from pymontecarlo.util.xmlutil import XMLIO


XMLIO.add_namespace('mc-pen', 'http://pymontecarlo.sf.net/penelope',
                    resource_filename(__name__, 'schema.xsd'))
