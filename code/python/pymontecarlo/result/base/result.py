#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- Common results
================================================================================

.. module:: result
   :synopsis: Common results

.. inheritance-diagram:: result

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from math import sqrt
from collections import Iterable

# Third party modules.

# Local modules.
from pymontecarlo.util.transition import from_string

# Globals and constants variables.
GENERATED = "g"
EMITTED = "e"
NOFLUORESCENCE = "nf"
CHARACTERISTIC = "cf"
BREMSSTRAHLUNG = "bf"
TOTAL = "t"

class _Result(object):

    def __init__(self, detector):
        self._detector = detector

    @property
    def detector(self):
        return self._detector

def create_intensity_dict(transition,
                          gcf=(0.0, 0.0), gbf=(0.0, 0.0), gnf=(0.0, 0.0), gt=(0.0, 0.0),
                          ecf=(0.0, 0.0), ebf=(0.0, 0.0), enf=(0.0, 0.0), et=(0.0, 0.0)):
    return {transition: {
                GENERATED: {
                    CHARACTERISTIC: gcf,
                    BREMSSTRAHLUNG: gbf,
                    NOFLUORESCENCE: gnf,
                    TOTAL: gt},
                EMITTED: {
                    CHARACTERISTIC: ecf,
                    BREMSSTRAHLUNG: ebf,
                    NOFLUORESCENCE: enf,
                    TOTAL: et}
                         }
            }

class PhotonIntensityResult(_Result):
    def __init__(self, detector, intensities={}):
        """
        Creates a new result to store photon intensities.
        
        :arg detector: photon intensity detector
        :arg intensities: :class:`dict` containing the intensities.
            One should use :func:`.create_intensity_dict` to create the dictionary
        """
        _Result.__init__(self, detector)

        self._intensities = intensities

    def _get_intensity(self, key, transition, absorption=True):
        if isinstance(transition, basestring):
            transition = from_string(transition)

        # Get intensity data
        data = []
        if isinstance(transition, Iterable): # transitionset
            if transition in self._intensities:
                data.append(self._intensities[transition])
            else:
                for t in transition:
                    if t in self._intensities: # Add only known transitions
                        data.append(self._intensities[t])

            if not data:
                raise ValueError, "No intensity for transition(s): %s" % transition
        else: # single transition
            try:
                data.append(self._intensities[transition])
            except KeyError:
                raise ValueError, "No intensity for transition(s): %s" % transition

        # Retrieve intensity (and its uncertainty)
        absorption_key = EMITTED if absorption else GENERATED
        total_val = 0.0; total_err = 0.0
        for datum in data:
            val, err = datum[absorption_key][key]
            total_val += val
            try:
                total_err += (err / val) ** 2
            except ZeroDivisionError: # if val == 0.0
                pass

        total_err = sqrt(total_err) * total_val

        return total_val, total_err

    def intensity(self, transition, absorption=True, fluorescence=True):
        """
        Returns the intensity (and its uncertainty) in counts / (sr.A).
        
        These examples will all returned the same values::
        
            >>> result.intensity(Transition(13, 4, 1))
            >>> result.intensity('Al Ka1')
        
        or
        
            >>> result.intensity(K_family(13))
            >>> result.intensity('Al K')
            
        Note that in the case of a set of transitions (e.g. family, shell),
        the intensity of each transition in the set is added. 
        For instance, the following lines will yield the same result::
        
            >>> result.intensity('Al Ka1')[0] + result.intensity('Al Ka2')[0]
            >>> result.intensity('Al K')[0]
            
        Note that the ``[0]`` is to return the intensity part of the 
        intensity/uncertainty tuple.
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.
        :arg fluorescence: whether to return the intensity with fluorescence.
            If ``True``, intensity with fluorescence is returned, if ``false``
            intensity without fluorescence.
            
        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        key = TOTAL if fluorescence else NOFLUORESCENCE
        return self._get_intensity(key, transition, absorption)

    def characteristic_fluorescence(self, transition, absorption=True):
        """
        Returns the intensity (and its uncertainty) of the characteristic photons
        produced by fluorescence of primary photons in counts / (sr.A).
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.
            
        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        return self._get_intensity(CHARACTERISTIC, transition, absorption)

    def bremsstrahlung_fluorescence(self, transition, absorption=True):
        """
        Returns the intensity (and its uncertainty) of the Bremsstrahlung photons
        produced by fluorescence of primary photons in counts / (sr.A).
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.
            
        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        return self._get_intensity(BREMSSTRAHLUNG, transition, absorption)

    def fluorescence(self, transition, absorption=True):
        """
        Returns the intensity (and its uncertainty) of the fluorescence 
        contribution to the total intensity in counts / (sr.A).
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg fluorescence: whether to return the intensity with fluorescence.
            If ``True``, intensity with fluorescence is returned, if ``false``
            intensity without fluorescence.
            
        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        # Note: TOTAL - FLUORESCENCE should be equal to CHARACTERISTIC + BREMSS
        v1, e1 = self._get_intensity(NOFLUORESCENCE, transition, absorption)
        v2, e2 = self._get_intensity(TOTAL, transition, absorption)

        return v2 - v1, e1 + e2

    def absorption(self, transition, fluorescence=True):
        """
        Returns the intensity (and its uncertainty) of the absorption 
        contribution to the total intensity in counts / (sr.A).
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.
            
        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        v1, e1 = self.intensity(transition, absorption=False, fluorescence=fluorescence)
        v2, e2 = self.intensity(transition, absorption=True, fluorescence=fluorescence)

        return v2 - v1, e1 + e2

    def iter_transitions(self, absorption=True, fluorescence=True):
        """
        Returns an iterator returning a tuple of the transition and intensity.
        
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.
        :arg fluorescence: whether to return the intensity with fluorescence.
            If ``True``, intensity with fluorescence is returned, if ``false``
            intensity without fluorescence.
        """
        for transition in self._intensities:
            yield transition, self.intensity(transition, absorption, fluorescence)


