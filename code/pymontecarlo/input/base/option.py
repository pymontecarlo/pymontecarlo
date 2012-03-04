#!/usr/bin/env python
"""
================================================================================
:mod:`option` -- Base class for all options
================================================================================

.. module:: option
   :synopsis: Base class for all options

.. inheritance-diagram:: pymontecarlo.input.base.option

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
from pymontecarlo.util.xmlutil import objectxml, XMLIO

# Globals and constants variables.

XMLIO.add_namespace('mc', 'http://pymontecarlo.sf.net/input/base',
                    resource_filename(__name__, 'base.xsd'))

class Option(objectxml):

    def __init__(self):
        self.__dict__.setdefault('_props', {}) # prevent double initialization
