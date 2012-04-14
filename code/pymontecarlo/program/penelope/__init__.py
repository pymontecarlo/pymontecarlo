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
import os

# Third party modules.
from pkg_resources import resource_filename #@UnresolvedImport

# Local modules.
from pymontecarlo import settings
from pymontecarlo.util.xmlutil import XMLIO
from pymontecarlo.program import Program as _Program

import pymontecarlo.program.penelope.input.body
import pymontecarlo.program.penelope.input.material

# Globals and constants variables.

XMLIO.add_namespace('mc-pen', 'http://pymontecarlo.sf.net/penelope',
                    resource_filename(__name__, 'schema.xsd'))

class _PenelopeProgram(_Program):

    def is_valid(self):
        try:
            pendbase = settings.penelope.pendbase
        except AttributeError:
            return False

        return os.path.isdir(pendbase)

