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
import numpy as np
import h5py

# Local modules.
from pymontecarlo.input.options import Options
from pymontecarlo.input.material import pure, Material
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.detector import PhotonIntensityDetector

from pymontecarlo.output.results import Results

import pymontecarlo.util.xmlutil as xmlutil
import pymontecarlo.util.transition as transitionutil

# Globals and constants variables.

class Measurement(object):

    VERSION = '1'

    def __init__(self, options, transitions, detector=None):
        """
        Creates a new Measurement.
        
        :args options: options for this measurement
        :args transitions: a list of transitions that should be observed in this experiment
        :args detector: the detector from which the intensities should be extracted
        """

        self._options_unk = copy.deepcopy(options)
        self._transitions = sorted(transitions)
        self._kratios = {}
        self._results_unk = None
        self._results_std = {}
        self._standards_material = {}
        self._detector_key = self._select_detector_key(self._options_unk, detector)

    @classmethod
    def load(cls, filepath):
        hdf5file = h5py.File(filepath, 'r')

        try:
            return cls._load(hdf5file)
        finally:
            hdf5file.close()

    @classmethod
    def _load(cls, hdf5parent):
        if hdf5parent.attrs['version'] != cls.VERSION:
            raise IOError, "Incorrect version of measurement. Only version %s is accepted" % \
                    cls.VERSION

        element = xmlutil.parse(hdf5parent.attrs['options_unk'])
        options_unk = Options.from_xml(element)

        transitions = [transitionutil.from_string(transition) \
                            for transition in hdf5parent.attrs['transitions']]

        detector_key = hdf5parent.attrs['detector_key']
        detector = options_unk.detectors[detector_key]

        meas = cls(options_unk, transitions, detector)

        # k-ratios
        for transition, kratio in hdf5parent['kratios'].attrs.iteritems():
            meas.set_kratio(transitionutil.from_string(transition), kratio)

        # Unknown result
        if 'results_unk' in hdf5parent:
            results_unk = Results._load(hdf5parent['results_unk'])
            meas.put_results_unk(results_unk)

        # Standard results
        for transition, hdf5group in hdf5parent['results_std'].iteritems():
            results = Results._load(hdf5group)
            meas.put_results_std(transitionutil.from_string(transition), results)

        # Standards
        for transition, attrvalue in hdf5parent['standards'].attrs.iteritems():
            material = Material.from_xml(xmlutil.parse(attrvalue))
            meas.set_standard(transitionutil.from_string(transition), material)

        return meas

    def save(self, filepath):
        hdf5file = h5py.File(filepath, 'w')

        try:
            self._save(hdf5file)
        finally:
            hdf5file.close()

    def _save(self, hdf5parent):
        hdf5parent.attrs['version'] = self.VERSION

        hdf5parent.attrs['options_unk'] = xmlutil.tostring(self._options_unk.to_xml(), pretty_print=False)
        hdf5parent.attrs['transitions'] = [str(transition) for transition in self._transitions]

        hdf5group = hdf5parent.create_group("kratios")
        for transition, kratio in self._kratios.iteritems():
            hdf5group.attrs[str(transition)] = kratio

        if self._results_unk:
            hdf5group = hdf5parent.create_group("results_unk")
            self._results_unk._save(hdf5group)

        hdf5group = hdf5parent.create_group("results_std")
        for transition, results in self._results_std.iteritems():
            hdf5groupchild = hdf5group.create_group(str(transition))
            results._save(hdf5groupchild)

        hdf5group = hdf5parent.create_group("standards")
        for transition, material in self._standards_material.iteritems():
            hdf5group.attrs[str(transition)] = xmlutil.tostring(material.to_xml(), pretty_print=False)

        hdf5parent.attrs['detector_key'] = self._detector_key

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
        Returns a numpy array containing all k-ratios from this measurement.
        The array is sorted by the transition of the k-ratios.
        """

        kratios = []
        if self._kratios: # k-ratios have been manually set
            for _transition, kratio in sorted(self._kratios.iteritems()):
                kratios.append(kratio)
        else: # extract k-ratios from the simulated results
            if not self.simulated_unk():
                raise ValueError, 'k-ratios were neither simulated nor manually set'
            if not self._detector_key:
                raise ValueError, 'Cannot extract k-ratios! No detector has been specified.'

            for transition in self.get_transitions():
                unk_int, _unc = self._results_unk[self._detector_key].intensity(transition)
                if self.simulated_std():
                    std_int, _unc = self._results_std[transition][self._detector_key].intensity(transition)
                else:
                    std_int = 1.0
                kratios.append(unk_int / std_int)

        return np.array(kratios)

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

        if material is None:
            material = pure(transition.z)

        self._standards_material[transition] = material

    def has_standards(self):
        """
        Returns 'True' iff standards have been specified for this measurement.
        """

        return len(self._standards_material) == len(self._transitions)

    def simulated_unk(self):
        """
        Returns `True` iff the unknown options have been simulated.
        """

        return self._results_unk is not None

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

    def put_results_unk(self, results):
        """
        Puts a results object to the measurement from which unknown intensities can be retrieved.
        
        :arg results: results object with simulation results for the measurement
        """

        self._results_unk = results

    def put_results_std(self, transition, results):
        """
        Puts a results object to the measurement from which standard intensities of a given
        transition can be retrieved.
        
        :arg transition: transition for which the standard is used
        :arg results: results object with the simulation results for the standard
        """

        self._results_std[transition] = results

    def get_options_unk(self):
        """
        Returns the options object specifying the measurement on the unknown sample.
        """

        return self._options_unk

    def get_options_std(self, transition):
        """
        Returns an the options object for the standard of the given transition.
        
        :arg transition: transition of the standard whose options object should be returned
        """

        if not transition in self._standards_material:
            raise ValueError, 'No standard material specified for transition "%s"' % transition

        options = copy.deepcopy(self._options_unk)
        options.geometry = Substrate(self._standards_material[transition])

        return options

    def _select_detector_key(self, options, detector=None):
        detectors = options.detectors.findall(PhotonIntensityDetector).values()
        if detector is None and len(detectors) == 1:
            detector = detectors[0]
        if detector not in detectors:
            raise ValueError, "Detector not included in options: %s" % detector

        return options.detectors.find(detector)
