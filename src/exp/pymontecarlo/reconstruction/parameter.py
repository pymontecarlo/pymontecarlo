#!/usr/bin/env python
"""
================================================================================
:mod:`parameter` -- Parameter for reconstruction
================================================================================

.. module:: parameter
   :synopsis: Parameter for reconstruction

.. inheritance-diagram:: pymontecarlo.reconstruction.parameter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class Parameter(object):

    def __init__(self, getter, setter, val0,
                 minval=float('-inf'), maxval=float('inf')):
        """
        Creates a parameter 
        
        :arg getter: function to get the value of this parameter from a 
            geometry. The function should take one argument, a geometry object,
            and returns the value of this parameter.
        :arg setter: function to set this parameter inside the geometry.
            The function should take two arguments: a geometry object and the 
            value of the parameter to be updated.
        :arg val0: initial value
        :arg minval: lower allowable limit of the value of this parameter
        :arg maxval: upper allowable limit of the value of this parameter
        """
        if not callable(getter):
            raise ValueError, "Getter function must be callable"
        self._getter = getter

        if not callable(setter):
            raise ValueError, "Setter function must be callable"
        self._setter = setter

        if val0 < minval or val0 > maxval:
            raise ValueError, "Initial value outside limits: %s" % val0
        self._val0 = val0

        self._minval = minval
        self._maxval = maxval

    @property
    def getter(self):
        """
        Function to get the value of this parameter.
        """
        return self._getter

    @property
    def setter(self):
        """
        Function to set this parameter inside the geometry.
        """
        return self._setter

    @property
    def initial_value(self):
        """
        Initial value of this parameter.
        """
        return self._val0

    @property
    def constraints(self):
        """
        Lower and upper allowable limit of the value of this parameter.
        """
        return self._minval, self._maxval
