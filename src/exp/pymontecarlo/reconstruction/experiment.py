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
__author__ = "Niklas Mevenkamp"
__email__ = "niklas.mevenkamp@rwth-aachen.de"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Niklas Mevenkamp"
__license__ = "GPL v3"

# Standard library modules.
import logging
import copy
import os
import glob
from operator import itemgetter
from StringIO import StringIO

# Third party modules.
import numpy as np
import h5py

# Local modules.
from pymontecarlo.reconstruction.measurement import Measurement
from pymontecarlo.output.results import Results
import pymontecarlo.util.xmlutil as xmlutil

# Globals and constants variables.

class ExperimentCreator(object):

    def __init__(self, base_experiment, parameters):
        """
        Creates an experiment creator that can change the given base experiment's
        geometry based on the specified parameters.
        
        :arg base_experiment: fully specified experiment that should be used as a prototype
        :arg parameters: list of parameter objects used to change the geometry of the experiment
        """

        self._base_experiment = base_experiment
        self._parameters = parameters
        self._iterator = 0

    def get_experiment(self, values):
        """
        Returns an experiment fully specified by the given values using previously defined parameters.
        
        :arg values: list of values for the parameters
        """

        if not len(values) == len(self._parameters):
            raise ValueError, 'Dimension of given values does not match with parameters of the base experiment'

        # Create new name using name extension and iterator
        self._iterator += 1
        name = self._base_experiment._name + "_" + str(self._iterator)

        # Set geometry based on the given values
        geometry = copy.deepcopy(self._base_experiment.get_geometry())
        for parameter, value in zip(self._parameters, values):
            parameter.setter(geometry, value)

        experiment = Experiment(name, geometry, self._base_experiment.get_measurements())

        # Set values
        experiment._values = values

        return experiment

    def get_constraints(self):
        """
        Returns a list of tuples with the lower and upper bounds of the parameters.
        """

        list_constraints = []
        for parameter in self._parameters:
            list_constraints.append(parameter.constraints)

        return list_constraints

class Experiment(object):

    VERSION = '1'

    def __init__(self, name, geometry, measurements):
        """
        Creates a new experiment.
        
        :arg name: name of the experiment
        :arg measurements: a list of easurements executed during this experiment
        """
        self._name = copy.deepcopy(name)
        self._geometry = copy.deepcopy(geometry)
        self._measurements = copy.deepcopy(measurements)
        self._values = None

        # Override geometry in measurements to make sure they all use the same one
        for measurement in self.get_measurements():
            measurement.get_options_unk().geometry = self._geometry
            if measurement.has_standards():
                for transition in measurement.get_transitions():
                    measurement.get_options_std(transition).geometry = self._geometry

    @property
    def name(self):
        """
        Returns the name of this experiment.
        """

        return self._name

    def get_kratios(self):
        """
        Returns a a numpy array with the k-ratios from all measuerments.
        The k-ratios are ordered primarily by measurement and secondarily by transition.
        """

        kratios = np.array([])
        for measurement in self.get_measurements():
            kratios = np.hstack((kratios, measurement.get_kratios()))

        return kratios

    def _set_kratios(self, list_kratios):
        """
        Manually set all k-ratios measured in the experiment by giving a sorted list of k-ratios.
        
        :arg list_kratios: a list with k-ratios for all measurements of this experiment
            (the list must be ordered primarily by measurement and secondarily by transition)
        """

        for measurement in self._measurements:
            for transition in measurement.get_transitions():
                measurement.set_kratio(transition, list_kratios.pop(0))

    def get_values(self):
        """
        Returns the list of values of the parameters that were used to create this experiment.
        """

        if self._values is None:
            raise ValueError, 'No values available (probably experiment has not been created using parameters)'

        return self._values

    def get_geometry(self):
        """
        Returns the geometry of this experiment.
        """

        return self._geometry

    def get_measurements(self):
        """
        Returns a list with all measurements. The list has the same order as the one
        given when the class was instantiated.
        """

        return self._measurements

    def has_standards(self):
        """
        Returns 'True' iff for all transistions of all measurements
        standard materials have been specified.
        """

        return all([measurement.has_standards() for measurement in self._measurements])

    def simulated_unk(self):
        """
        Returns `True`iff all unknowns of all measurements have been simulated.
        """

        return all([measurement.simulated_unk() for measurement in self.get_measurements()])

    def simulated_std(self):
        """
        Returns `True` iff all standards of all measurements have been simulated.
        """

        return all([measurement.simulated_std() for measurement in self.get_measurements()])

    @classmethod
    def load(cls, path):
        """
        Loads an experiment from a file specified by the given path.
        
        :arg path: path to an experiment file
        """
        hdf5file = h5py.File(path, "r")

        try:
            if hdf5file.attrs['version'] != cls.VERSION:
                raise IOError, "Incorrect version of experiment. Only version %s is accepted" % \
                        cls.VERSION

            # Name
            name = hdf5file.attrs['name']

            # Geometry
            fp = StringIO(hdf5file.attrs['geometry'])
            element = xmlutil.parse(fp).getroot()
            geometry = xmlutil.XMLIO.from_xml(element)

            # Measurements
            measurements = {}
            for groupname, hdf5group in hdf5file.iteritems():
                measurement_id = int(groupname.split('-')[1])
                measurement = Measurement._load(hdf5group)
                measurements[measurement_id] = measurement

            measurements = measurements.items()
            measurements.sort(key=itemgetter(0))
            measurements = map(itemgetter(1), measurements)

            # Values
            values = hdf5file.attrs['values']

            # Experiment
            exp = cls(name, geometry, measurements)
            exp._values = values
            return exp
        finally:
            hdf5file.close()

    def save(self, path):
        """
        Saves an experiment to a file at the specified path.
        
        :arg path: location where the experiment should be saved
        """
        hdf5file = h5py.File(path, 'w')

        try:
            hdf5file.attrs['version'] = self.VERSION

            hdf5file.attrs['name'] = str(self.name)

            hdf5file.attrs['geometry'] = xmlutil.tostring(self.get_geometry().to_xml(), pretty_print=False)

            for i, measurement in enumerate(self.get_measurements()):
                hdf5group = hdf5file.create_group("measurement-%i" % i)
                measurement._save(hdf5group)

            hdf5file.attrs['values'] = self.get_values()
        finally:
            hdf5file.close()

class ResultsConverter(object):

    def __init__(self):
        """
        Creates a ResultsConverter that converts Results *.h5 files
        that belong to single simulations to Experiment *.h5 files.
        """

        pass

    def convert(self, results, transitions, getters=None, detector=None):
        """
        Converts a Results object corresponding to a single simulation to
        an Experiment object with a single measurement.
        
        :arg results: Results object to be converted
        :arg transitions: list of transitions that should be extracted from the simulation
        :arg getters: list of callable functions that extract the variables of the parameters
            (set to `None` if the results were not created using a parameterized geometry)
            Each getter function should take one argument, a geometry object, and
            return the value of the corresponding parameter.
        """

        # Create experiment
        measurement = Measurement(results.options, transitions, detector)
        measurement.put_results_unk(results)
        experiment = Experiment(results.options.name, results.options.geometry, [measurement])

        # Extract variables
        if getters is not None:
            experiment._values = [getter(results.options.geometry) for getter in getters]

        return experiment

    def convert_dir(self, dir_path, transitions, getters=None, detector=None):
        """
        Loads all Results *.h5 files in the given folder, converts them
        to Experiment objects and saves them.
        (Results objects are kept as a backup.)
        
        :arg dir_path: path to the folder containing the Results *.h5 files to be converted
        :arg transitions: list of transitions that should be extracted from the simulation
        :arg getters: list of callable functions that extract the variables of the parameters
            (set to `None` if the results were not created using a parameterized geometry)
            Each getter function should take one argument, a geometry object, and
            return the value of the corresponding parameter.
        """

        for path in glob.glob(os.path.join(dir_path, "*.h5")):
            #TODO: check type of the *.h5 file (Results or Experiment)

            results = Results.load(path)
            experiment = self.convert(results, transitions, getters, detector)

            os.rename(path, path + ".bak")
            experiment.save(path)
            
            logging.info('Converted results "%s" to experiment.' % results.options.name)
