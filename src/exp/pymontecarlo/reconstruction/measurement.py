#!/usr/bin/env python
"""
================================================================================
:mod:`measurement` -- Stores experimental measurement
================================================================================

.. module:: measurement
   :synopsis: Stores experimental measurement

.. inheritance-diagram:: pymontecarlo.reconstruction.measurement

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy

# Third party modules.

# Local modules.
from pymontecarlo.input.material import pure
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.detector import PhotonIntensityDetector

from pymontecarlo.util.xmlutil import objectxml, Element, XMLIO

# Globals and constants variables.

class Measurement(objectxml):

    def __init__(self, baseoptions, detector=None):
        """
        Creates a new measurement.
        """
        detectors = baseoptions.detectors.findall(PhotonIntensityDetector).values()

        if not detectors:
            raise ValueError, "No photon intensity detector defined"
        if detector is None and len(detectors) == 1:
            detector = detectors[0]
        if detector not in detectors:
            raise ValueError, "Detector not included in base options: %s" % detector

        self._baseoptions = copy.deepcopy(baseoptions)
        self._detector_key = baseoptions.detectors.find(detector)

        self._kratios = {}
        self._standards = {}

    def __repr__(self, *args, **kwargs):
        return '<%s(%i k-ratios defined)>' % \
            (self.__class__.__name__, len(self._kratios))

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        child = element.find('baseoptions')
        if child is None:
            raise IOError, 'Base options missing'
        baseoptions = XMLIO.from_xml(list(child)[0])

        detector_key = element.get('detector_key')
        detector = baseoptions.detectors[detector_key]

        measurement = cls(baseoptions, detector)

        for child in element.iterfind('kratio'):
            val = float(child.get('val'))
            unc = float(child.get('unc'))

            grandchild = child.find('transition')
            if grandchild is None:
                raise IOError, 'kratio does not have a transition'
            transition = XMLIO.from_xml(list(grandchild)[0])

            grandchild = child.find('standard')
            if grandchild is None:
                raise IOError, 'kratio does not have a standard'
            standard = XMLIO.from_xml(list(grandchild)[0])

            measurement.add_kratio(transition, val, unc, standard)

        return measurement

    def __savexml__(self, element, *args, **kwargs):
        element.set('detector_key', self._detector_key)

        child = Element('baseoptions')
        child.append(self._baseoptions.to_xml())
        element.append(child)

        for transition, kratio in self._kratios.iteritems():
            val, unc = kratio
            standard = self._standards[transition]

            child = Element('kratio')
            child.set('val', str(val))
            child.set('unc', str(unc))

            grandchild = Element('transition')
            grandchild.append(transition.to_xml())
            child.append(grandchild)

            grandchild = Element('standard')
            grandchild.append(standard.to_xml())
            child.append(grandchild)

            element.append(child)
    
    def add_kratio(self, transition, val, unc=0.0, standard=None):
        """
        Adds an experimental k-ratio to this measurement.
        
        :arg transition: transition or set of transition for this k-ratio
        :type transition: :class:`.Transition` or :class:`.transitionset`
        
        :arg val: k-ratio value
        :type val: :class:`float`
        
        :arg unc: uncertainty on the k-ratio value (default: 0.0)
        :type unc: :class:`float`
        
        :arg standard: material of the standard geometry of the standard. 
            If ``None``, the standard is assumed to be a pure (100% of the 
            element in the specified transition)
        :type standard: instance of :class:`._Material`
        """
        if transition in self._kratios:
            raise ValueError, 'A k-ratio is already defined for transition: %s' % transition
        if val < 0.0:
            raise ValueError, 'k-ratio value must be greater than 0.0'
        if unc < 0.0:
            raise ValueError, 'k-ratio uncertainty must be greater than 0.0'

        if standard is None:
            standard = pure(transition.z)

        self._kratios[transition] = (val, unc)
        self._standards[transition] = standard

    def remove_kratio(self, transition):
        """
        Removes a k-ratio from this measurement.
        
        :arg transition: transition to be removed
        """
        self._kratios.pop(transition)
        self._standards.pop(transition)

    def clear_kratios(self):
        """
        Removes all k-ratios from this measurement.
        """
        self._kratios.clear()
        self._standards.clear()

    def has_kratio(self, transition):
        """
        Whether a k-ratio is defined for this transition.
        
        :arg transition: transition
        """
        return transition in self._kratios

    def get_kratios(self):
        """
        Returns the k-ratios defined for this measurement.
        The k-ratio values are sorted by the specified transitions.
        """
        vals = []
        for _transition, kratio in sorted(self._kratios.iteritems()):
            vals.append(kratio[0])
        return vals
    
    def get_transitions(self):
        return [transition for transition in sorted(self._kratios.iterkeys())]

    def create_standard_options(self, basename):
        """
        Creates the options to simulate the standards of this measurement.
        
        :arg basename: base name of the options
        """
        list_options = []

        for transition, material in self._standards.iteritems():
            options = copy.deepcopy(self._baseoptions)
            options.name = basename + '+' + str(transition)
            options.geometry = Substrate(material)
            list_options.append(options)

        return list_options

    def extract_standard_intensities(self, basename, dict_results):
        """
        Extracts the intensities from the simulations of the standards of 
        this measurement.
        Returns an array with the intensities.
        The value ordering and length of the array are equal to the one returned 
        by :attr:`get_kratios`.
        """
        intensities = []

        for transition in sorted(self._kratios.iterkeys()):
            results = dict_results[basename + '+' + str(transition)]
            val, _unc = results[self._detector_key].intensity(transition)
            intensities.append(val)

        return intensities

    def create_unknown_options(self, name, unkgeometry):
        """
        Creates the required options to simulate this measurement.

        :arg name: name of the options for this measurement
        :arg unkgeometry: geometry for the unknown
        """
        options = copy.deepcopy(self._baseoptions)
        options.name = name
        options.geometry = unkgeometry
        return options

    def extract_unknown_intensities(self, results):
        """
        Extracts the intensities from the simulation of the unknown of this
        measurements.
        Returns an array with the intensities.
        The value ordering and length of the array are equal to the one returned 
        by :attr:`get_kratios`. 

        :arg results: results for this measurement
        """
        intensities = []

        for transition in sorted(self._kratios.iterkeys()):
            val, _unc = results[self._detector_key].intensity(transition)
            intensities.append(val)

        return intensities
    
XMLIO.register('{http://pymontecarlo.sf.net}measurement', Measurement)
