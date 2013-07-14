#!/usr/bin/env python
"""
================================================================================
:mod:`mathutil` -- Math utilities
================================================================================

.. module:: math
   :synopsis: Math utilities

.. inheritance-diagram:: pymontecarlo.util.mathutil

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from collections import namedtuple
import numbers
import math
from operator import add, sub, mul, div, neg

# Third party modules.

# Local modules.

# Globals and constants variables.

class _vector(object):
    
    def __nonzero__(self):
        return all(map(lambda x: x == 0, self))
#
    def __add__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(*map(lambda x: x + other, self))
        else:
            return self.__class__(*map(add, self, other))

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(*map(lambda x: x - other, self))
        else:
            return self.__class__(*map(sub, self, other))

    def __rsub__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(*map(lambda x: other - x, self))
        else:
            return self.__class__(*map(sub, other, self))

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(*map(lambda x: x * other, self))
        else:
            return self.__class__(*map(mul, self, other))

    __rmul__ = __mul__

    def __div__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(*map(lambda x: x / other, self))
        else:
            return self.__class__(*map(div, self, other))

#    def __rdiv__(self, other):
#        if isinstance(other, numbers.Number):
#            return self.__class__(*map(lambda x: other / x, self))
#        else:
#            return self.__class__(*map(div, other, self))
#
    def __neg__(self):
        return self.__class__(*map(neg, self))

    def __abs__(self):
        return math.sqrt(sum(map(lambda x: x ** 2, self)))

    magnitude = __abs__

    def normalize(self):
        d = self.magnitude()
        try:
            return self / d
        except ZeroDivisionError:
            return self.__class__(*self)

    def dot(self, other):
        return sum(map(mul, self, other))

class vector3d(_vector, namedtuple('vector3d', ['x', 'y', 'z'])):

    def cross(self, other):
        return vector3d(self.y * other.z - self.z * other.y,
                       - self.x * other.z + self.z * other.x,
                       self.x * other.y - self.y * other.x)
#
class vector2d(_vector, namedtuple('vector2d', ['x', 'y'])):
    pass
