#!/usr/bin/env python
"""
================================================================================
:mod:`reconstructor` -- Reconstruction of experiment by non-linear optimization
================================================================================

.. module:: reconstructor
   :synopsis: Reconstruction of experiment by non-linear optimization

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

# Third party modules.
import numpy as np

# Local modules.

# Globals and constants variables.



class Reconstructor(object):

    def __init__(self, simulator, optimizer, experiment, eps_diff):
        """
        Creates a new reconstructor.
        
        :arg runner: runner for the simulations
        :arg optimizer: optimizer to use for the reconstruction
        :arg experiment: experiment to reconstruct
        :arg eps_diff: relative step length used to calculate jacobian in the function handler
        """
        self._simulator = simulator
        self._optimizer = optimizer
        self._experiment = experiment
        self._eps_diff = eps_diff

    def reconstruct(self):
        """
        Starts reconstruction.
        Returns the reconstructed geometry and the simulated k-ratios.
        """
        self._simulator.runner.start()

        stdintensities = self._simulator.simulate_std()
        reference_kratios = self._experiment.reference_kratios

        func = self.get_targetfunction(stdintensities, reference_kratios)
        fhandler = _FunctionHandler(func, self._eps_diff)

        initial_values = self._experiment.parameters_initial_values
        constraints = self._experiment.parameters_constraints

        x_opt, F_opt = \
            self._optimizer.optimize(fhandler.get_func(), fhandler.get_jac(),
                                     initial_values, constraints)
        
        self.simulator.runner.close()
        
        geometry_opt = self._experiment.create_geometry(x_opt)

        return geometry_opt, x_opt, F_opt
    
    def get_targetfunction(self, stdintensities, reference_kratios):
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

class _FunctionHandler(object):
    def __init__(self, func, eps_diff):
        self.func = func
        self.eps_diff = eps_diff
        self._f = None
        
    def get_func(self):
        def _func(x, *args, **kwargs):
            fs = self.func([x])
            self._f = fs[0]
            
            return self._f
        return _func
    
    def get_jac(self):
        def _jac(x, *args, **kwargs):
            # Setup step sizes for finite difference quotients
            xphs, dxs = [], np.zeros(len(x))
            for i in range(0, len(x)):
                xph = copy.deepcopy(x)
                xph[i] += self.eps_diff*abs(x[i])
                xphs.append(xph)
                dxs[i] = xph[i] - x[i]
            
            # Calculate function evaluations
            fs = self.func(xphs)
            
            # Compute the jacobian using forward differences
            J = np.zeros([len(x), len(fs[0])]) # Create empty jacobian
            for i in range(0, len(x)): # Calculate finite differences
                J[i] = (fs[i] - self._f)/dxs[i]
            J = J.transpose()
                
            return J
        
        return _jac
