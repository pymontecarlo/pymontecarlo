#!/usr/bin/env python
"""
================================================================================
:mod:`reconstructor` -- Reconstruction of experiment by non-linear optimisation
================================================================================

.. module:: reconstructor
   :synopsis: Reconstruction of experiment by non-linear optimisation

.. inheritance-diagram:: pymontecarlo.reconstruction.reconstructor

"""

# Script information for the file.
__author__ = "Niklas Mevenkamp"
__email__ = "niklas.mevenkamp@rwth-aachen.de"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Niklas Mevenkamp"
__license__ = "GPL v3"

# Standard library modules.
import time

# Third party modules.

# Local modules.

# Globals and constants variables.



class Simulator(object):

    def __init__(self, runner, experiment):
        """
        Creates a new simulator.
        
        :arg runner: runner for the simulations
        :arg experiment: experiment to simulate
        """
        self._runner = runner
        self._experiment = experiment
        
    def simulate(self, list_values):
        """
        Runs simulations of the unknowns based on the specified parameter 
        values.
        Returns a :class:`list` of arrays. 
        Each array corresponds to the intensities of a set of value of the
        parameters.
        
        :arg list_values: :class:`list` containing arrays. Each array specifies
            the value of the parameters
        """
        list_options = self._experiment.create_unknown_options(list_values)
        map(self._runner.put, list_options)
        
        self._runner.start()
        
        while self._runner.is_alive():
            print self._runner.report()
            time.sleep(1)

        list_results = self._runner.get_results()
        list_unkintensities = \
            self._experiment.extract_unknown_intensities(list_results)
            
        self._runner.stop()

        return list_unkintensities

    def simulate_std(self):
        """
        Runs simulations of the standards.
        Returns an array with the intensities.
        """
        list_options = self._experiment.create_standard_options()
        map(self._runner.put, list_options)
        
        self._runner.start()
        
        while self._runner.is_alive():
            print self._runner.report()
            time.sleep(1)

        list_results = self._runner.get_results()
        stdintensities = self._experiment.extract_standard_intensities(list_results)
        
        self._runner.stop()
        
        return stdintensities
