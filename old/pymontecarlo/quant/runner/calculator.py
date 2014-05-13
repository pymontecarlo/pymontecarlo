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
import os
import math

# Third party modules.
import pyxray.element_properties as ep

# Local modules.
from QuantitativeAnalysisTools.FluorescenceFactor import FluorescenceFactor

from SpecimenTools.Element import Element
from SpecimenTools.SampleRegion import SampleRegion

# Globals and constants variables.
from QuantitativeAnalysisTools.FluorescenceModelName import MODEL_CHARACTERISTIC_DEMERS2007
from QuantitativeAnalysisTools.FluorescenceModelName import MODEL_BREMSSTRAHLUNG_REED1997

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

    def __init__(self, measurement, stdintensities, **kwargs):
        SimpleCalculator.__init__(self, measurement, stdintensities, **kwargs)

        self._characteristic_model = MODEL_CHARACTERISTIC_DEMERS2007
        self._bremsstrahlung_model = MODEL_BREMSSTRAHLUNG_REED1997
        self._config_filepath = \
            os.path.join(os.path.expanduser('~'), '.pymontecarlo', 'fluorescence.cfg')

    def _calculate(self, z, unkintensity, stdintensity):
        kratioval, kratiounc = \
             SimpleCalculator._calculate(self, z, unkintensity, stdintensity)

        factor = self._calculate_factor(z)
        kratioval /= factor
        kratiounc /= factor

        return kratioval, kratiounc

    def _calculate_factor(self, z):
        fluorescence = FluorescenceFactor(self._config_filepath,
                                          self._characteristic_model,
                                          self._bremsstrahlung_model)

        energy_keV = self._measurement.options.beam.energy_eV / 1000.0
        fluorescence.setIncidentEnergy_keV(energy_keV)

        toa_deg = self._measurement.detector.takeoffangle_deg
        fluorescence.setTakeoffAngle_deg(toa_deg)

        elements = []
        material = self._measurement.unknown_body.material
        for atomicnumber, wf in material.composition.iteritems():
            elements.append(Element(atomicnumber, weightFraction=wf))
        region = SampleRegion(elements)
        fluorescence.setSpecimenBulk(region)

        elements = []
        material = self._measurement.get_standards()[z].material
        for atomicnumber, wf in material.composition.iteritems():
            elements.append(Element(atomicnumber, weightFraction=wf))
        region = SampleRegion(elements)
        fluorescence.setStandardBulk(region)

        transitions = self._measurement.get_transitions()
        transition = [t for t in transitions if t.z == z][0]

        element = ep.symbol(transition.z)
        if hasattr(transition, '__iter__'):
            line = transition.name
        else:
            line = transition.siegbahn_nogreek

        return fluorescence.getFactor(element, line)
