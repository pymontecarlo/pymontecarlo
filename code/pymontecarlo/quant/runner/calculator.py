#!/usr/bin/env python
"""
================================================================================
:mod:`calculator` -- Algorithm to calculate k-ratios
================================================================================

.. module:: calculator
   :synopsis: Algorithm to calculate k-ratios

.. inheritance-diagram:: pymontecarlo.quant.runner.calculator

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math

# Third party modules.

# Local modules.

# Globals and constants variables.

class _Calculator(object):
    def __init__(self, measurement, stdintensities, **kwargs):
        """
        Creates a new k-ratio calculator.
        
        :arg measurement: measurement being quantified
        :type measurement: :class:`.Measurement`
        
        :arg stdintensities: calculated/simulated intensities of the standards.
            This is a :class:`dict` where the keys are atomic numbers and the
            values are tuples of the intensity values and uncertainties.
        :type stdintensities: :class:`dict`
        """
        self._measurement = measurement
        self._stdintensities = stdintensities

    def calculate(self, unkintensities):
        """
        Calculates the k-ratios from the specified unknown intensities.
        
        :arg unkintensities: :class:`dict` where the keys are atomic numbers
            and the values are tuples of the intensity values and uncertainties.
        :type unkintensities: :class:`dict`
        """
        kratios = {}

        for z, unkintensity in unkintensities.iteritems():
            stdintensity = self._stdintensities[z]
            kratios[z] = self._calculate(z, unkintensity, stdintensity)

        return kratios

    def _calculate(self, z, unkintensity, stdintensity):
        """
        Method to be implemented by the derived class.
        The method should return the k-ratio for the specified atomic number,
        unknown and standard intensities.
        
        :arg z: atomic number
        :type z: :class:`int`
        
        :arg unkintensity: unknown intensity (value and uncertainty)
        :type unkintensity: :class:`tuple` of :class:`float`
        
        :arg stdintensity: standard intensity (value and uncertainty)
        :type stdintensity: :class:`tuple` of :class:`float`
        """
        raise NotImplementedError

class SimpleCalculator(_Calculator):

    def _calculate(self, z, unkintensity, stdintensity):
        unkval, unkunc = unkintensity
        stdval, stdunc = stdintensity

        try:
            kratioval = unkval / stdval
        except ZeroDivisionError:
            kratioval = 0.0

        try:
            unkuncrel = unkunc / unkval
        except ZeroDivisionError:
            unkuncrel = 0.0
        try:
            stduncrel = stdunc / stdval
        except ZeroDivisionError:
            stduncrel = 0.0
        kratiounc = kratioval * math.sqrt(unkuncrel ** 2 + stduncrel ** 2)

        return kratioval, kratiounc

class FluorescenceCalculator(SimpleCalculator):

    def _calculate(self, z, unkintensity, stdintensity):
        kratioval, kratiounc = \
             SimpleCalculator._calculate(self, z, unkintensity, stdintensity)


        return kratioval, kratiounc
