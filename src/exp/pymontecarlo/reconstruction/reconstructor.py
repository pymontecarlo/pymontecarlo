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
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy
import time
import logging

# Third party modules.
import numpy as np
from numpy.linalg import norm

# Local modules.

# Globals and constants variables.

class _FunctionHandler(object):
    def __init__(self, func, eps_diff):
        self.func = func
        self.eps_diff = eps_diff
        self._x = None
        self._f = None
        self._J = None
        self.it = 0

    def get_func(self):
        def _func(x, *args):
            if self._x == None or not all(self._x[i] == x[i] for i in range(len(x))) or self._f == None:
                self.it += 1

                self._x = x

                # Setup step sizes for finite difference quotients
                xphs, dxs = [], np.zeros(len(x))
                for i in range(0, len(x)):
                    xph = copy.deepcopy(x)
                    xph[i] += self.eps_diff * abs(x[i])
                    xphs.append(xph)
                    dxs[i] = xph[i] - x[i]

                # Collect all x'es needed for the evaluation of f and its jacobian (using forward differences)
                xs = [x] + xphs
                fs = self.func(xs)
                self._f = fs[0]

                # Compute the jacobian using forward differences and store it for later calls
                self._J = np.zeros([len(x), len(fs[0])]) # Create empty jacobian
                for i in range(0, len(x)): # Calculate finite differences
                    self._J[i] = (fs[i + 1] - fs[0]) / dxs[i]
                self._J = self._J.transpose()

                # Print log
                logging.info("Iteration %i: x=%s; f=%s; res=%s", self.it, self._x, self._f, norm(self._f))
                logging.info("J=%s", self._J)

            return self._f
        return _func

    def get_jac(self):
        def _jac(x, *args):
            return self._J

        return _jac

class Reconstructor(object):

    def __init__(self, runner, optimizer, experiment, eps_diff=1e-4):
        """
        Creates a new reconstructor.
        
        :arg runner: runner for the simulations
        :arg optimizer: optimizer to use for the reconstruction
        :arg experiment: experiment to reconstruct
        """
        self._runner = runner
        self._optimizer = optimizer
        self._experiment = experiment

        self._eps_diff = eps_diff

    def reconstruct(self):
        """
        Starts reconstruction.
        Returns the reconstructed geometry and the simulated k-ratios.
        """
        self._runner.start()

        stdintensities = self._run_standards()
        reference_kratios = self._experiment.reference_kratios

        func = self._get_targetfunction(stdintensities, reference_kratios)
        fhandler = _FunctionHandler(func, self._eps_diff)

        initial_values = self._experiment.parameters_initial_values
        constraints = self._experiment.parameters_constraints

        values, diff = \
            self._optimizer.optimize(fhandler.get_func(), fhandler.get_jac(),
                                     initial_values, constraints)

        geometry = self._experiment.create_geometry(values)

        return geometry, diff

    def _run_standards(self):
        """
        Runs simulations of the standards.
        Returns an array with the intensities.
        """
        list_options = self._experiment.create_standard_options()
        map(self._runner.put, list_options)

        while self._runner.is_alive():
            print self._runner.report()
            time.sleep(1)

        list_results = self._runner.get_results()
        stdintensities = self._experiment.extract_standard_intensities(list_results)

        return stdintensities

    def _run_unknowns(self, list_values):
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

        while self._runner.is_alive():
            print self._runner.report()
            time.sleep(1)

        list_results = self._runner.get_results()
        list_unkintensities = \
            self._experiment.extract_unknown_intensities(list_results)

        return list_unkintensities

    def _get_targetfunction(self, stdintensities, reference_kratios):
        """
        Returns the function to minimize.
        
        :arg stdintensities: array with the standard intensities
        :arg reference_kratios: array of the reference k-ratio values
        """
        if len(stdintensities) != len(reference_kratios):
            raise ValueError, 'Length of standard intensities do not match reference k-ratios'

        def _targetfunction(list_values):
            """
            Function to minimize.
            Returns an array containing the difference between the k-ratios
            simulated from the specified values and the k-ratios from the
            reference.
            
            :arg list_values: :class:`list` containing arrays. Each array specifies
            the value of the parameters
            """
            list_unkintensities = self._run_unknowns(list_values)

            list_diff = []
            for unkintensities in list_unkintensities:
                kratios = unkintensities / stdintensities
                diff = kratios - reference_kratios
                list_diff.append(diff)

            return list_diff

        return _targetfunction


