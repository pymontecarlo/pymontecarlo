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
from pymontecarlo.input.detector import PhotonIntensityDetector

# Globals and constants variables.

class Measurement(object):
    
    def __init__(self, options, transitions, detector=None):
        """
        Creates a new Measurement.
        
        :args options: options for this measurement
        :args transitions: a list of transitions that should be observed in this experiment
        :args detector: the detector from which the intensities should be extracted
        """
        
        self._options = copy.deepcopy(options)
        self._transitions = sorted(transitions)
        self._kratios = None
        self._results = None
        self._results_std = {}
        self._standards_material = {}
        
        # Select and store detector key
        detectors = self._options.detectors.findall(PhotonIntensityDetector).values()
        if detector is None and len(detectors) == 1:
            detector = detectors[0]
        if detector not in detectors:
            raise ValueError, "Detector not included in options: %s" % detector
        self._detector_key = self._options.detectors.find(detector)
    
    def set_kratio(self, transition, kratio):
        """
        Manually set the k-ratio of the given transition for this measurement.
        
        :arg transition: transition of the k-ratio that is begin set
        :arg kratio: k-ratio to be manually set for this measurement
        """
        
        if not transition in self._transitions:
            raise ValueError, 'Given transition "%s" not observed in this measurement' % transition
        
        self._kratios[transition] = kratio
    
    def get_kratios(self):
        """
        Returns a list with all k-ratios from this measurement.
        The list is sorted by the transition of the k-ratios.
        """
        
        kratios = []
        if self._kratios: # k-ratios have been manually set
            for _transition, kratio in sorted(self._kratios.iteritems()):
                kratios.append(kratio)
        else: # extract k-ratios from the simulated results
            if not self.simulated():
                raise ValueError, 'k-ratios were neither simulated nor manually set'
            if not self._detector_key:
                raise ValueError, 'Cannot extract k-ratios! No detector has been specified.'
            
            for transition in self.get_transitions():
                unk_val, _unc = self._results[self._detector_key].intensity(transition)
                if self.simulated_std():
                    std_val, _unc = self._results_std[transition][self._detector_key].intensity(transition)
                else:
                    std_val = 1.0
                kratios.append(unk_val / std_val)
        
        return kratios
    
    def set_standard(self, transition, material=None):
        """
        Set standards for all transitions.
        
        :arg transition: transition that the given standard corresponds to
        :arg material: material of the standard
            (if material is `None` the material is assumed to be pure bulk
            of the element corresponding to the given transition)
        :type material: instance of :class:`._Material`
        """
        
        if not transition in self._transitions:
            raise ValueError, 'Given transition "%s" is not observed in this measurement' % transition
        
        if material == None:
            material = pure(transition.z)
        
        self._standards_material[transition] = material
    
    def has_standards(self):
        """
        Returns 'True' iff standards have been specified for this measurement.
        """
        
        return len(self._standards_material) == len(self._transitions)
    
    def simulated(self):
        """
        Returns `True` iff the unknown options have been simulated.
        """
        
        return self._results == True
    
    def simulated_std(self):
        """
        Returns `True` iff all standards have been simulated.
        """
        
        return len(self._results_std) == len(self._transitions)
        
    def get_transitions(self):
        """
        Returns a sorted list with all transitions observed in this measurement.
        """
        
        return sorted(self._transitions)
    
    def put_results(self, results):
        """
        Puts a results object to the measurement from which intensities can be retrieved.
        
        :arg results: results object with simulation results for the measurement
        """
        
        self._results = results
    
    def put_results_std(self, transition, results):
        """
        Puts a results object to the measurement from which standard intensities of a given
        transition can be retrieved.
        
        :arg transition: transition for which the standard is used
        :arg results: results object with the simulation results for the standard
        """
        
        self._results_std[transition] = results
    
    def get_options(self):
        """
        Returns the options object specifying this measurement.
        """
        
        return self._options
    
    def get_options_std(self, transition):
        """
        Returns an the options object for the standard of the given transition.
        
        :arg transition: transition of the standard whose options object should be returned
        """
        
        if not transition in self._standards_material:
            raise ValueError, 'No standard material specified for transition "%s"' % transition
        
        options = copy.deepcopy(self._options)
        options.geometry = self._standards_material[transition]
        # TODO: is standards material a geometry?
            
        return options