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
        self._experimentcreator = ExperimentCreator(experiment, parameters)
        self._optimizer = optimizer
        self._eps_diff = eps_diff

    def reconstruct(self, x0, ref_experiment, ref_x=None, rel_err=None):
        """
        Starts reconstruction.
        Returns the reconstructed geometry and the simulated k-ratios.
        
        :arg x0: initial guess for the parameters
        :arg ref_experiment: reference experiment object which is already simulated
            or to which k-ratios were manually added
        :arg ref_x: list of values from which a reference experiment will be created
            and simulated
            (if you want to use this, set ref_experiment to `None`)
        :arg rel_err: if you know ref_x, you can use rel_err to stop the iteration
            when the rel. error w.r.t. ref_x is less than rel_err
        """
        
        # TODO: interp2Drunner can't simulate standards yet
        base_experiment = self._experimentcreator._base_experiment
        if base_experiment.has_standards() and not base_experiment.simulated_std():
            self._experimentcreator._base_experiment = self._simulate_standards(base_experiment)
        
        if not ref_experiment and not ref_x:
            raise ValueError, 'No reference specified'
        
        if ref_experiment:
            self._ref_experiment = ref_experiment
        else:
            self._ref_experiment = self._experimentcreator.get_experiment(ref_x)
            self._experimentrunner.put(self._ref_experiment)
            self._experimentrunner.start()
            while self._experimentrunner.is_alive():
                print self._experimentrunner.report()
                time.sleep(1)
            self._ref_experiment = self._experimentrunner.get_results()[0]

        fgetter = FunctionGetter()
        func = fgetter.get_func(self._experimentcreator, self._experimentrunner, self._ref_experiment)
        fhandler = FunctionHandler(func, self._eps_diff)
        
        if ref_x and rel_err:
            x_opt, F_opt, f_evals, exit_code = \
                self._optimizer.optimize(fhandler.get_func(), fhandler.get_jac(),
                                         x0, self._experimentcreator.get_constraints(), (ref_x, rel_err))
        else:
            x_opt, F_opt, f_evals, exit_code = \
                self._optimizer.optimize(fhandler.get_func(), fhandler.get_jac(),
                                         x0, self._experimentcreator.get_constraints())
        
        geometry_opt = self._experimentcreator.get_experiment(x_opt).get_geometry()
        
        return geometry_opt, x_opt, F_opt, f_evals, exit_code
    
    def _simulate_standards(self, experiment):
        if not experiment.simulated_std():
            # Pretend that the experiment has simulated unknowns
            for measurement in experiment.get_measurements():
                measurement.results_unk = True
            
            self._experimentrunner.put(experiment)
            self._experimentrunner.start()
            
            while self._experimentrunner.is_alive():
                print self._experimentrunner.report()
                time.sleep(1)
                
            experiment = self._experimentrunner.get_results()[0]
            
            # Revert the above
            for measurement in experiment.get_measurements():
                measurement.results_unk = None
                        
            return experiment    
    
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
            
            for experiment in sorted(list_experiments, key=lambda x: x.name):
                list_diff.append(experiment.get_kratios() - ref_experiment.get_kratios())
                
            experimentrunner.stop()

            return list_diff

        return _func

class FunctionHandler(object):
    
    def __init__(self, func, eps_diff=1e-2, n=1):
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
        self.n = n
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
        Here finite differences with step size abs(argmuent) * eps_diff are used. 
        """
        
        def _jac(x, *args, **kwargs):
            # Setup step sizes for finite difference quotients
            xphs, dxs = [], np.zeros(len(x))
            for i in range(len(x)):
                xph = copy.deepcopy(x)
                xph[i] += self.eps_diff * abs(x[i])
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
    
    def get_jac_regression(self):
        """
        Returns a callable function that maps a list of argument values to a matrix
        containing approximations of the partial derivatives
        of the previously defined callable function.
        Here for each argument x, 2*n+1 function evaluations
        (n to the left of x, 1 at x, n to the right of x)
        are used to fit a linear function (the partial derivative) to.
        This way noise in the function can be compensated.
        """
        
        def _jac(x, *args, **kwargs):
            # Setup step sizes for finite difference quotients
            xphs, dxs = np.zeros((len(x), 2*self.n+1, len(x))), np.zeros(len(x))
            for i in range(len(x)):
                for j in range(-self.n,self.n+1):
                    xph = copy.deepcopy(x)
                    xph[i] += j * self.eps_diff * abs(x[i])
                    xphs[i,j + self.n] = xph
                    dxs[i] = xph[i] - x[i]
        
                    # Calculate function evaluations
                    fs = self.func([xphs[i,j] for i in range(len(x)) for j in range(2*self.n+1)])
                    
                    J = np.zeros([len(x), len(fs[0])])
                    for i in range(x):
                        for k in range(len(fs[0])):
                            x = xphs[i,:,i]
                            y = [fs[i * (2 * self.n + 1) + j][k] for j in range(2 * self.n + 1)]
                            J[k,i] = np.polyfit(x, y, 1)[0]
                            
            return J
        
        return _jac