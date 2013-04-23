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
__author__ = "Niklas Mevenkamp"
__email__ = "niklas.mevenkamp@rwth-aachen.de"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Niklas Mevenkamp"
__license__ = "GPL v3"

# Standard library modules.
import copy
import time

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.reconstruction.experiment import ExperimentCreator

# Globals and constants variables.



class Reconstructor(object):

    def __init__(self, experiment, parameters, experimentrunner, optimizer, eps_diff=1e-4):
        """
        Creates a new reconstructor.
        
        :arg experiment: base experiment with the geometry that should be reconstructed
        :arg parameters: a list of parameters
        :arg experimentrunner: runner for the experiments
        :arg optimizer: optimizer to use for the reconstruction
        :arg eps_diff: relative step length used to calculate jacobian in the function handler
        """
        
        self._experimentrunner = experimentrunner
        self._simulate_standards(experiment)
        self._experimentcreator = ExperimentCreator(experiment, parameters)
        self._optimizer = optimizer
        self._eps_diff = eps_diff

    def reconstruct(self, x0, ref_experiment, ref_x=None):
        """
        Starts reconstruction.
        Returns the reconstructed geometry and the simulated k-ratios.
        
        :arg x0: initial guess for the parameters
        :arg ref_experiment: reference experiment object which is already simulated
            or to which k-ratios were manually added
        :arg ref_x: list of values from which a reference experiment will be created
            and simulated
            (if you want to use this, set ref_experiment to `None`)
        """
        
        if not ref_experiment and not ref_x:
            raise ValueError, 'No reference specified'
        
        if ref_experiment:
            self._ref = ref_experiment
        else:
            self._ref = self._experimentcreator.get_experiment(ref_x)

        fgetter = FunctionGetter(self._experimentcreator, self._experimentrunner, self._ref)
        fhandler = FunctionHandler(fgetter.get_func(), self._eps_diff)

        x_opt, F_opt = \
            self._optimizer.optimize(fhandler.get_func(), fhandler.get_jac(),
                                     x0, self._experimentcreator.get_constraints())
        
        geometry_opt = self._experimentcreator.get_experiment(x_opt).get_geometry()
        
        return geometry_opt, x_opt, F_opt
    
    def _simulate_standards(self, experiment):
        if not experiment.standards_simulated():
            self._experimentrunner.put(experiment)
            self._experimentrunner.start()
            
            while self._experimentrunner.is_alive():
                print self._runner.report()
                time.sleep(1)
                
            experiment = self._experimentrunner.get_results()[0]
            
            self._experimentrunner.stop()
    
    
    
class FunctionGetter(object):
    
    def __init__(self):
        """
        Creates a function getter.
        """
        
        pass
    
    def get_func(self, experimentcreator, experimentrunner, ref_experiment):
        """
        Returns a function that maps a list of lists of values for the experiment parameters
        to a list containing the differences between the simulated k-ratios and the reference k-ratios.
        
        :arg experimentcreator: experiment creator used to produce experiment objects
        :arg experimentrunner: runner to simulate the created experiments
        :arg ref_experiment: experiment from which the reference k-ratios will be extracted
        """
        
        def _func(list_values):
            for values in list_values:
                experiment = experimentcreator.get_experiment(values)
                experimentrunner.put(experiment)
            experimentrunner.start()
            
            while experimentrunner.is_alive():
                print experimentrunner.report()
                time.sleep(1)
                
            list_experiments = experimentrunner.get_results()
            
            list_diff = []
            for experiment in list_experiments:
                list_diff.append(experiment.get_kratios() - ref_experiment.get_kratios())
                
            experimentrunner.stop()

            return list_diff

        return _func

class FunctionHandler(object):
    
    def __init__(self, func, eps_diff):
        """
        Creates a function handler.
        
        :arg func: callable function that should take a list of lists of values and returns
            a list of lists with function values
            (like the one returned by the FunctionGetter)
        :arg eps_diff: finite step size used in the finite differences
            when calculating the Jacobian of the given callable function
        """
        
        self.func = func
        self.eps_diff = eps_diff
        self._f = None
        
    def get_func(self):
        """
        Returns a callable function that maps a list of argument values to a list of
        function values using the previously defined callable function.
        """
        
        def _func(x, *args, **kwargs):
            fs = self.func([x])
            self._f = fs[0]
            
            return self._f
        return _func
    
    def get_jac(self):
        """
        Returns a callable function that maps a list of argument values to a matrix
        containing approximations of the partial derivatives
        of the previously defined callable function.
        """
        
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
