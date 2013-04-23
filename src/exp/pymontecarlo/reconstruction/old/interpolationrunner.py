#!/usr/bin/env python
"""
================================================================================
:mod:`interpolationrunner` -- Calculate kratios based on interpolated data
================================================================================

.. module:: interpolationrunner
   :synopsis: Calculate kratios based on interpolated data

.. inheritance-diagram:: pymontecarlo.runner_tst.interpolationrunner

"""
# Script information for the file.
__author__ = "Niklas Mevenkamp"
__email__ = "niklas.mevenkamp@gmx.net"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Niklas Mevenkamp"
__license__ = "GPL v3"

# Standard library modules
from Queue import Empty

# Third party modules
from scipy.interpolate.interpolate import interp2d

# Local modules
from pymontecarlo.runner_tst.experimentrunner import ExperimentRunner
from pymontecarlo.reconstruction.experiment import Experiment



class ExperimentInterp2DRunner(ExperimentRunner):
    def __init__(self, list_experiments):
        """
        Creates a new interpolation runner that can interpolate kratios that were
        measured in experiments with different values of the same parameters.
        Note: Interpolation is only available for experiments with 2 parameters.
        
        :arg list_experiments: a list of experiment objects
        """
        ExperimentRunner.__init__(self, runner=None)
        
        self.list_experiments = list_experiments
        
        self.data = self._collect_data(self.list_experiments)
        self.spline = self._get_spline(self.data)
    
    @classmethod
    def load(cls, list_paths):
        """
        Creates a new interpolation runner that can interpolate kratios that were
        measured in experiments with different values of the same parameters.
        Note: Interpolation is only available for experiments with 2 parameters.
        
        :arg list_paths: a list of paths to experiment files.
        """
        
        list_experiments = []
        for path in list_paths:
            list_experiments.append(Experiment.load(path))
            
        return cls(list_experiments)
        
        
    def start(self):
        while True:
            try:
                experiment = self._queue_experiments.get_nowait()
                experiment.set_kratios(self._get_kratios(experiment))
                self._queue_experiments_simulated.put(experiment)
                self._queue_experiments.task_done()
            except Empty:
                break
    
    def stop(self):
        pass
    
    def close(self):
        pass
    
    def _get_kratios(self, experiment):
        x = experiment.get_values()
        
        return self.spline(x[0], x[1])
        
    def _collect_data(self, list_experiments):
        xs, ys, zs = [], [], []
        for experiment in list_experiments:
            x = experiment.get_values()
            
            if len(x) <> 2:
                raise ValueError, "Number of paramaters is not equal to two (length is %s)." % len(x)
            
            xs.append(x[0])
            ys.append(x[1])
            zs.append(experiment.get_kratios())
        
        return {'xs': xs, 'ys': ys, 'zs': zs}
    
    def _get_spline(self, data):
        xs = data['xs']
        ys = data['ys']
        zs = data['zs']
        
        splines = []
        for i in range(0,len(zs[0])):
            splines.append(interp2d(xs, ys, [z[i] for z in zs], kind='cubic'))
        
        def _spline(x, y):
            return [spline(x, y)[0] for spline in splines]
        
        return _spline