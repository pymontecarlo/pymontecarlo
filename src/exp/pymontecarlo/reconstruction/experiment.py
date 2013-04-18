#!/usr/bin/env python
"""
================================================================================
:mod:`experiment` -- Experiment
================================================================================

.. module:: experiment
   :synopsis: Experiment

.. inheritance-diagram:: pymontecarlo.reconstruction.experiment

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy
from operator import attrgetter

# Third party modules.
import numpy as np

# Local modules.

# Globals and constants variables.

class Experiment(object):

    def __init__(self, geometry, measurements, parameters):
        """
        Creates a new experiment.
        """
        self._basegeometry = copy.deepcopy(geometry)
        self._measurements = list(measurements) # copy
        self._parameters = list(parameters) # copy

    @property
    def reference_kratios(self):
        """
        An array of the reference values.
        """
        vals = []
        for measurement in self._measurements:
            vals.extend(measurement.get_kratios())
        return np.array(vals)

    @property
    def parameters_initial_values(self):
        """
        Initial values of the parameters.
        """
        return map(attrgetter('initial_value'), self._parameters)

    @property
    def parameters_constraints(self):
        """
        Minimum and maximum value of the parameters.
        """
        return map(attrgetter('constraints'), self._parameters)
    
    @property
    def parameters_getters(self):
        """
        Callable getter functions of the parameters.
        """
        return map(attrgetter('getter'), self._parameters)

    def create_standard_options(self):
        """
        Creates the options to simulate the standards of all measurements.
        """
        list_options = []

        for i, measurement in enumerate(self._measurements):
            basename = '%i' % i
            list_options.extend(measurement.create_standard_options(basename))

        return list_options

    def extract_standard_intensities(self, list_results):
        """
        Extracts the intensities from the simulations of the standards of 
        all measurements.
        Returns an array with the intensities.
        The value ordering and length of the array are equal to the one returned 
        by :attr:`reference_kratios`.
        """
        intensities = []

        # Extract name from results options
        dict_results = {}
        for results in list_results:
            dict_results[results.options.name] = results

        for i, measurement in enumerate(self._measurements):
            basename = '%i' % i
            intensities.extend(measurement.extract_standard_intensities(basename, dict_results))

        return np.array(intensities)

    def create_geometry(self, values):
        """
        Returns a new geometry object where the parameters values have been
        applied.
        
        :arg values: array containing the value of each parameter
        """
        if len(values) != len(self._parameters):
            raise ValueError, "Incorrect number of values, should be %i" % len(self._parameters)

        geometry = copy.deepcopy(self._basegeometry)

        for parameter, value in zip(self._parameters, values):
            parameter.setter(geometry, value)

        return geometry

    def create_unknown_options(self, list_values):
        """
        Returns a :class:`list` of options to simulate for one iteration.
        The options included those required for the unknown and standard 
        simulations.
        The options are setup based on the specified parameters values and the
        base options specified for each measurement.
        
        .. important::
        
           Each options is given a special name that should not be changed.
           This name is required for the :meth:`extract_unknown_intensities`
           method to work properly.
           
        :arg list_values: :class:`list` containing arrays. Each array specifies
            the value of the parameters
        """
        list_options = []

        for i, values in enumerate(list_values):
            unkgeometry = self.create_geometry(values)

            for j, measurement in enumerate(self._measurements):
                basename = '%i-%i' % (i, j)
                list_options.append(measurement.create_unknown_options(basename, unkgeometry))

        return list_options

    def extract_unknown_intensities(self, list_results):
        """
        Extracts the intensities from the simulations of the unknowns of all
        measurements.
        Returns a :class:`list` of arrays. 
        Each array corresponds to the intensities of a set of value of the
        parameters.
        The value ordering and length of each array are equal to the one 
        returned by :attr:`reference_kratios`.
        
        :arg list_results: :class:`list` of results
        """
        # Extract name from results options
        dict_results = {}
        maxseries = float('-inf')
        for results in list_results:
            name = results.options.name
            maxseries = max(maxseries, int(name.split('-')[0]))
            dict_results[name] = results

        # Extract values
        list_intensities = []
        for i in range(maxseries + 1):
            intensities = []

            for j, measurement in enumerate(self._measurements):
                name = '%i-%i' % (i, j)
                results = dict_results[name]
                intensities.extend(measurement.extract_unknown_intensities(results))

            list_intensities.append(np.array(intensities))

        return list_intensities
