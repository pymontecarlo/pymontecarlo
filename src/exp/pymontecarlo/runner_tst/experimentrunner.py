#!/usr/bin/env python
"""
================================================================================
:mod:`experimentrunner` -- Adaptors to run experiments.
================================================================================

.. module:: experimentrunner
   :synopsis: Runners to run experiments

.. inheritance-diagram:: pymontecarlo.runner_tst.experimentrunner

"""
# Script information for the file.
__author__ = "Niklas Mevenkamp"
__email__ = "niklas.mevenkamp@gmx.net"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Niklas Mevenkamp"
__license__ = "GPL v3"

# Standard library modules
import copy

# Third party modules
from scipy.interpolate.interpolate import interp2d

# Local modules
from pymontecarlo.runner.sequence import SequenceRunner
from pymontecarlo.reconstruction.experiment import Experiment



class ExperimentRunner(SequenceRunner):
    def __init__(self, runner):
        """
        Creates a new experiment runner that can simulate experiments
        using the specified runner for the options files.
        
        :arg runner: instance of a runner class that can run options objects
        """
        
        SequenceRunner.__init__(self, runner)
        self._sequencerunner = SequenceRunner(self._runner)
        self.list_experiments = []

    def put(self, experiment):
        self._list_experiments.append(copy.deepcopy(experiment))
        options_seq = []
        for measurement in experiment.get_measurements():
            options_seq.append(measurement.get_options())
        self._sequencerunner.put(options_seq)
        #TODO: put options for standards

    def start(self):
        self._sequencerunner.start()
    
    def stop(self):
        self._sequencerunner.stop()

    def close(self):
        self._sequencerunner.stop()

    def is_alive(self):
        return self._sequencerunner.is_alive()

    def join(self):
        self._sequencerunner.join()

    def get_results(self):
        results = []
        list_results_sequence = self._sequencerunner.get_results()
        #TOdO: retrieve results for standards
        for results_sequence in list_results_sequence:
            experiment = self._pop_experiment(results_sequence)
            for (results, measurement) in zip(results_sequence._list_results, experiment.get_measurements()):
                measurement.put_results(copy.deepcopy(results))
            results.append(copy.deepcopy(experiment))
            
        return results
    
    def report(self):
        self._sequencerunner.report()
        
    def _pop_experiment(self, results_sequence):
        # should search self._list_experiments for the experiment belonging to the given results_sequence,
        # delete it from that list and return it
        pass
    
class ExperimentInterp2DRunner(ExperimentRunner):
    def __init__(self, list_experiments_data):
        """
        Creates a new interpolation runner that can interpolate kratios that were
        measured in experiments with different values of the same parameters.
        Note: Interpolation is only available for experiments with 2 parameters.
        
        :arg list_experiments_data: a list of experiment objects used as data for interpolation
        """
        ExperimentRunner.__init__(self, runner=None)
        
        self._list_experiments_data = list_experiments_data
        
        self._data = self._collect_data(self._list_experiments_data)
        self._spline = self._get_spline(self._data)
    
    @classmethod
    def load(cls, list_paths):
        """
        Creates a new interpolation runner that can interpolate kratios that were
        measured in experiments with different values of the same parameters.
        Note: Interpolation is only available for experiments with 2 parameters.
        
        :arg list_paths: a list of paths to experiment files.
        """
        
        list_experiments_data = []
        for path in list_paths:
            list_experiments_data.append(Experiment.load(path))
            
        return cls(list_experiments_data)
        
        
    def start(self):
        pass
    
    def get_results(self):
        results = []
        for experiment in self._list_experiments:
            experiment._set_kratios(self._calc_kratios(experiment))
            results.append(copy.deepcopy(experiment))
        
        # Clear queues
        self.list_experiments = []
        # TODO: clear sequence runner queues
        
        return results
    
    def _calc_kratios(self, experiment):
        x = experiment.get_values()
        
        return self._spline(x[0], x[1])
    
    def stop(self):
        pass
    
    def close(self):
        pass
        
    def _collect_data(self, list_experiments_data):
        xs, ys, zs = [], [], []
        for experiment in list_experiments_data:
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