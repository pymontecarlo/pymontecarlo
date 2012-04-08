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

# Local modules.
from pymontecarlo.util.xmlutil import objectxml

# Globals and constants variables.

class Option(objectxml):

    def __init__(self):
        self.__dict__.setdefault('_props', {}) # prevent double initialization
