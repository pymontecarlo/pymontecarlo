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
        self._standards = {}
        
        # Select and store detector key
        detectors = self._options.detectors.findall(PhotonIntensityDetector).values()
        if detector is None and len(detectors) == 1:
            detector = detectors[0]
        if detector not in detectors:
            raise ValueError, "Detector not included in options: %s" % detector
        self._detector_key = self._options.detectors.find(detector)
    
    def set_kratio(self, dict_kratios):
        """
        Manually set all k-ratios for this measurement.
        
        :arg kratios: a dictionary of the form {transition: kratio}
        """
        
        transitions = [transition for transition, _kratio in dict_kratios.iteritems()]
        if not sorted(transitions) == sorted(self._transitions):
            raise ValueError, 'Transitions of this measurement and the given k-ratios do not match'
        
        self._kratios = dict_kratios
    
    def get_kratios(self):
        """
        Returns a list with all k-ratios from this measurement.
        The list is sorted by the transition of the k-ratios.
        """
        
        vals = []
        if self._kratios: # k-ratios have been manually set
            for _transition, kratio in sorted(self._kratios.iteritems()):
                vals.append(kratio)
        else: # extract k-ratios from the simulated results
            if not self._results or (self._standards and not self._results_std):
                raise ValueError, 'Tried to extract kratios from results' \
                    + ' but unknowns and/or standards have not been simulated'
            if not self._detector_key:
                raise ValueError, 'No detector has been specified'
            
            for transition in sorted(self._transitions):
                unk_val, _unc = self._results[self._detector_key].intensity(transition)
                std_val, _unc = self._results_std[transition][self._detector_key].intensity(transition)
                vals.append(unk_val / std_val)
        
        return vals
        
    def set_standards(self, dict_standards):
        """
        Set standards for all transitions.
        
        :arg standards_dict: dictionary of the form {transition: material}
            specifying which material was used to measure the transition's standard intensity 
            (If material is ``None`` it is replaced with a pure material of the 
            element in the specified transition.)
        :type material: instance of :class:`._Material`
        
        """
        transitions = [transition for transition, _standard in dict_standards.iteritems()]
        if not sorted(transitions) == sorted(self._transitions):
            raise ValueError, 'Transitions of this measurement and the given standards do not match'
        
        for transition, standard in dict_standards.iteritems():
            if standard is None:
                standard = pure(transition.z)
                
        self._dict_standards = dict_standards
        
    def standards_simulated(self):
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