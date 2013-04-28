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

    def __init__(self, setter, minval=float('-inf'), maxval=float('inf')):
        """
        Creates a parameter 

        :arg setter: function to set this parameter inside the geometry.
            The function should take two arguments: a geometry object and the
            value of the parameter to be updated.
        :arg minval: lower allowable limit of the value of this parameter
        :arg maxval: upper allowable limit of the value of this parameter
        """

        if not callable(setter):
            raise ValueError, "Setter function must be callable"
        self._setter = setter

        self._minval = minval
        self._maxval = maxval

    @property
    def setter(self):
        """
        Function to set this parameter inside the geometry.
        """
        
        def _setter(geometry, val):
            if val < self._minval or val > self._maxval:
                raise ValueError, "Value outside limits: %s" % val
            self._setter(geometry, val)
            
        return _setter

    @property
    def constraints(self):
        """
        Lower and upper allowable limit of the value of this parameter.
        """
        return self._minval, self._maxval
