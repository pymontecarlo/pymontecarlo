#!/usr/bin/env python
"""
================================================================================
:mod:`option` -- Base class for all PENELOPE options
================================================================================

.. module:: option
   :synopsis: Base class for all PENELOPE options

.. inheritance-diagram:: pymontecarlo.input.penelope.option

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
from pymontecarlo.util.xmlutil import XMLIO
from pymontecarlo.input.base.option import Option #@UnusedImport

# Globals and constants variables.

XMLIO.add_namespace('mc-pen', 'http://pymontecarlo.sf.net/input/penelope',
                    resource_filename(__name__, 'penelope.xsd'))
