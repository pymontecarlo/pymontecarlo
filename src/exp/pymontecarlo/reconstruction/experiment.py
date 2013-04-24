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
import copy

# Third party modules.
import numpy as np

# Local modules.

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
        
        experiment = copy.deepcopy(self._base_experiment)
        
        # Add name extension
        self._iterator += 1
        experiment._name += "_" + self._iterator
        
        # Set values
        experiment._values = values
        
        # Set geometry based on the given values
        geometry = experiment.get_geometry()
        for parameter, value in zip(self._parameters, values):
            parameter.setter(geometry, value)
        experiment.set_geometry(geometry)
                
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

    def __init__(self, name, geometry, measurements):
        """
        Creates a new experiment.
        
        :arg name: name of the experiment
        :arg measurements: a list of easurements executed during this experiment
        """
        self._name = name
        self._geometry = geometry
        self._measurements = measurements
        self._values = None
        
        # Override geometry in measurements to make sure they all use the same one
        self.set_geometry(geometry)        
    
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
        
        return np.array([measurement.get_kratios() for measurement in self._measurements])
    
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
        
        if self._values == None:
            raise ValueError, 'This experiment has not been created using parameters'
        
        return self._values()
    
    def get_geometry(self):
        """
        Returns the geometry of this experiment.
        """
        
        return self._geometry
    
    def set_geometry(self, geometry):
        """
        Set the geometry of this experiment.
        
        :arg geometry: geometry of the sample observed in this experiment
        """
        
        self._geometry = geometry
        
        for measurement in self.get_measurements():
            measurement.get_options().geometry = self._geometry
        
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
        
        return [measurement.has_standards() for measurement in self._measurements].all()
    
    def simulated(self):
        """
        Returns `True`iff all unknowns of all measurements have been simulated.
        """
        
        return [measurement.simulated() for measurement in self.get_measurements()].all()
    
    def simulated_std(self):
        """
        Returns `True` iff all standards of all measurements have been simulated.
        """
        
        return [measurement.simulated_std() for measurement in self.get_measurements()].all()
    
    @classmethod
    def load(self, path):
        """
        Loads an experiment from a file specified by the given path.
        
        :arg path: path to an experiment file
        """
        #TODO
        pass
        
    def save(self, path):
        """
        Saves an experiment to a file at the specified path.
        
        :arg path: location where the experiment should be saved
        """
        #TODO
        pass