#!/usr/bin/env python
"""
================================================================================
:mod:`bound` -- Tuple to defined the lower and upper bound
================================================================================

.. module:: bound
   :synopsis: Tuple to defined the lower and upper bound

.. inheritance-diagram:: pymontecarlo.input.bound

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from collections import namedtuple

# Third party modules.

# Local modules.
from pymontecarlo.util.mathutil import _vector
from pymontecarlo.input.xmlmapper import mapper, Attribute, PythonType

# Globals and constants variables.

class bound(_vector, namedtuple('bound', ['lower', 'upper'])):

    def __new__(cls, lower, upper):
        return cls.__bases__[1].__new__(cls, min(lower, upper), max(lower, upper))

    @property
    def low(self):
        return self.lower

    @property
    def high(self):
        return self.upper

mapper.register(bound, '{http://pymontecarlo.sf.net}bound',
                Attribute('lower', PythonType(float)),
                Attribute('upper', PythonType(float)))
